# This is a sample Python script.
import argparse
import datetime
import json
import socket
import time

import requests
import urllib3
from requests import ConnectTimeout
from requests.auth import HTTPBasicAuth
from requests_ntlm2 import (
    HttpNtlmAuth,
    HttpNtlmAdapter,
    NtlmCompatibility
)
from rich import print, pretty
from rich.console import Console

pretty.install()
from urllib3.exceptions import ConnectTimeoutError

console = Console()
pretty.install()


def load_config(config_file='config.json'):
    with open(config_file, 'rt') as f:
        return json.load(f)


def check_dns(conf, debug=False):
    dns_cache = {}
    dns_rules = conf.get('dns_cache', None)
    if dns_rules is not None:
        if debug:
            print("PATCH DNS OPERATION")
            print(dns_rules)
        prv_getaddrinfo = socket.getaddrinfo

        def new_getaddrinfo(*args):
            try:
                return dns_cache[args]
            except KeyError:
                if (replaced_ip := dns_rules.get(args[0], None)) is not None:
                    # res = [(socket.AddressFamily.AF_INET, args[3], 0, '', (replaced_ip, args[1]))]
                    res = prv_getaddrinfo(replaced_ip, *args[1:])
                else:
                    res = prv_getaddrinfo(*args)
                dns_cache[args] = res
                if debug:
                    print(f"RESOLVE {args[0]}:{args[1]} TO {[adr[4] for adr in res]}")
                return res

        socket.getaddrinfo = new_getaddrinfo


def get_ntlm_method(method_name):
    if method_name == 'ntlm1':
        return NtlmCompatibility.LM_AND_NTLMv1
    elif method_name == 'ntlm1ess':
        return NtlmCompatibility.NTLMv1_WITH_ESS
    elif method_name == 'lm':
        return NtlmCompatibility.LM_AND_NTLMv1_WITH_ESS
    elif method_name == 'level4':
        return NtlmCompatibility.NTLMv2_LEVEL4
    elif method_name == 'level5':
        return NtlmCompatibility.NTLMv2_LEVEL5
    elif method_name == 'ntlm2':
        return NtlmCompatibility.NTLMv2_DEFAULT
    else:
        return None


def do_test_connect(conf, url=None, debug=False):
    username = conf.get('user', None)
    password = conf.get('password', None)
    proxy_ip = conf.get('proxy_ip', None)
    proxy_port = conf.get('proxy_port', None)
    proxy_user = conf.get('proxy_user', None)
    proxy_pass = conf.get('proxy_port', "8080")
    proxy_use = conf.get('use_proxy', False)
    proxy_use_auth = conf.get('use_proxy_auth', False)
    login_use = conf.get('use_password', False)
    proxy_auth_method = conf.get('proxy_auth_method', 'ntlm2')
    auth_method = conf.get('auth_method', 'ntlm2')

    session = requests.Session()

    if proxy_use and proxy_ip:
        if debug:
            print("TRY USE PROXY")
        http_proxy_url = conf.get('http_proxy_url', None)
        if not http_proxy_url:
            http_proxy_url = 'http://{}:{}'.format(proxy_ip, proxy_port)
        https_proxy_url = conf.get('https_proxy_url', None)
        if not https_proxy_url:
            https_proxy_url = 'http://{}:{}'.format(proxy_ip, proxy_port)

        proxies = {
            'http': http_proxy_url,
            'https': https_proxy_url
        }
        if debug:
            print(proxies)

        if proxy_user and proxy_use_auth:
            ntlm_compatibility = get_ntlm_method(proxy_auth_method)
            print(f"METHOD:{ntlm_compatibility}")
            if ntlm_compatibility:
                session.mount(
                    'https://',
                    HttpNtlmAdapter(
                        proxy_user,
                        proxy_pass,
                        ntlm_compatibility=ntlm_compatibility
                    )
                )
                session.mount(
                    'http://',
                    HttpNtlmAdapter(
                        proxy_user,
                        proxy_pass,
                        ntlm_compatibility=ntlm_compatibility
                    )
                )
        session.proxies = proxies
    if login_use and username:
        if debug:
            print("TRY USE LOGIN")
        ntlm_compatibility_adapter = get_ntlm_method(auth_method)
        if ntlm_compatibility_adapter:
            if debug:
                print("USE NTLM LOGIN")
            session.auth = HttpNtlmAuth(
                username,
                password,
                ntlm_compatibility=ntlm_compatibility_adapter
            )
        else:
            if debug:
                print("USE HTTP Basic LOGIN")
            session.auth = HTTPBasicAuth(username, password)
    if url is None:
        url = conf.get('url')
    method = conf.get('method', "get")
    result = {
        'time': -1,
        'nano': -1,
        'res_size': 0,
        'req_size': 0,
        'status_code': -1,
        'peer_ip': None,
        'peer_port': None,
        'is_error': True,
        'response_header': dict(),
        'error': '',
    }
    start_time = datetime.datetime.now()
    ns = time.monotonic_ns()
    verify = conf.get('verify', False)
    if not verify:
        from urllib3.exceptions import InsecureRequestWarning
        urllib3.disable_warnings(InsecureRequestWarning)
    timeout = conf.get('timeout', None)
    request_args = {}
    if timeout:
        if debug:
            print(f"set timeout = {timeout}")
        request_args['timeout'] = timeout

    try:
        if debug:
            print("SEND REQUEST")
        if method == 'get':
            response = session.get(url, stream=True, verify=verify, **request_args)
        elif method == 'post':
            response = session.post(url, json=conf.get('data', {}), stream=True, verify=verify, **request_args)
        else:
            result['error'] = "Unknown method"
            return result
        if debug:
            print("END REQUEST")
        sock_info = response.raw._connection.sock.getpeername()
        result = {
            'res_size': len(response.content),
            'time': -1,
            'nano': -1,
            'status_code': response.status_code,
            'peer_ip': sock_info[0],
            'peer_port': sock_info[1],
            'response_header': response.headers,
            'is_error': False,
            'error': "",
        }
        if debug:
            print(f"Response code = {response.status_code}")
            print(f"Peer = {sock_info[0]}:{sock_info[1]}")
            print(f"Response size = {result['res_size']}")

    except ConnectTimeout as ct:
        if debug:
            print("Connection error - Timeout")
        result["error"] = str(ct)
    except ConnectTimeoutError as ce:
        if debug:
            print("Connection error - Timeout")
        result["error"] = str(ce)
    except requests.exceptions.ProxyError as pe:
        if debug:
            print("Proxy Error:", pe.args[0].reason.args[0])
        result["error"] = str(pe)
    except Exception as e:
        if debug:
            print(str(type(e)), e)
        result["error"] = f"{str(type(e))}:{str(e)}"
    end_time = datetime.datetime.now()
    d = time.monotonic_ns() - ns
    delta = (end_time - start_time)
    if debug:
        print(f"Request time = {d / 10 ** 9}s")
    result["time"] = delta.seconds + (delta.microseconds / 10 ** 6) + delta.days * 86400
    result["nano"] = d / 10 ** 9
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--print', action="store_true")
    parser.add_argument('-d', '--detail', action="store_true")
    parser.add_argument('-n', '--no_result', action="store_true")
    parser.add_argument('-u', '--url', action="store")
    args = parser.parse_args()

    with console.status("[bold green]Scraping data...", spinner='aesthetic') as status:
        conf = load_config()
        check_dns(conf, args.detail)
        resp = do_test_connect(conf, url=args.url, debug=args.detail)
        console.log(f'[bold][red]Done!')
    if not args.no_result:
        if args.print:
            print(resp)
        else:
            print(resp)
