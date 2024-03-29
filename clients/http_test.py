import os
from urllib.parse import urlparse

import requests
import urllib3
from requests.auth import HTTPBasicAuth
from requests_ntlm2 import NtlmCompatibility, HttpNtlmAdapter, HttpNtlmAuth

from clients.base_test import BaseTest
from clients.ip_base_test import BaseTCPIPTest


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


class HTTPTest(BaseTCPIPTest):

    def __init__(self, config_dict, data=None):
        super().__init__(config_dict, data)
        self.session = requests.Session()
        self.test_response = None

    def prepare_for_test(self):
        super().prepare_for_test()
        if not self.trust_env:
            self.session.trust_env = False

        if self.proxy_use and self.proxy_ip:

            self.print_info(self.LogLevel.LOG_OPERATION, "TRY USE PROXY")
            http_proxy_url = self.http_proxy_url
            if not http_proxy_url:
                http_proxy_url = 'http://{}:{}'.format(self.proxy_ip, self.proxy_port)
            https_proxy_url = self.https_proxy_url
            if not https_proxy_url:
                https_proxy_url = 'http://{}:{}'.format(self.proxy_ip, self.proxy_port)

            proxies = {
                'http': http_proxy_url,
                'https': https_proxy_url
            }

            self.print_info(BaseTest.LogLevel.LOG_PARAMS, proxies)

            if self.proxy_user and self.proxy_use_auth:
                ntlm_compatibility = get_ntlm_method(self.proxy_auth_method)
                self.print_info(self.LogLevel.LOG_DEBUG, f"METHOD:{ntlm_compatibility}")
                if ntlm_compatibility:
                    self.session.mount(
                        'https://',
                        HttpNtlmAdapter(
                            self.proxy_user,
                            self.proxy_pass,
                            ntlm_compatibility=ntlm_compatibility
                        )
                    )
                    self.session.mount(
                        'http://',
                        HttpNtlmAdapter(
                            self.proxy_user,
                            self.proxy_pass,
                            ntlm_compatibility=ntlm_compatibility
                        )
                    )
            self.session.proxies = proxies
        else:
            os.environ['no_proxy'] = '*'
        if self.login_use and self.username:

            self.print_info(BaseTest.LogLevel.LOG_OPERATION, "TRY USE LOGIN")
            ntlm_compatibility_adapter = get_ntlm_method(self.auth_method)
            if ntlm_compatibility_adapter:
                self.print_info(BaseTest.LogLevel.LOG_PARAMS, "USE NTLM LOGIN")
                self.session.auth = HttpNtlmAuth(
                    self.username,
                    self.password,
                    ntlm_compatibility=ntlm_compatibility_adapter
                )
            else:
                self.print_info(BaseTest.LogLevel.LOG_OPERATION, "USE HTTP Basic LOGIN")
                self.session.auth = HTTPBasicAuth(self.username, self.password)
        if not self.verify:
            from urllib3.exceptions import InsecureRequestWarning
            urllib3.disable_warnings(InsecureRequestWarning)
            #self.


    def _test_procedure(self):
        url = self.url
        method = self.method
        result = {
            'res_size': 0,
            'req_size': 0,
            'status_code': -1,
            'peer_ip': None,
            'peer_port': None,
            'response_header': dict(),
        }
        request_args = {}
        if self.timeout is not None:
            self.print_info(self.LogLevel.LOG_PARAMS, f"set timeout = {self.timeout}")
            request_args['timeout'] = self.timeout
        if self.verify is not None:
            request_args['verify'] = self.verify
        if self.json_data is not None:
            request_args['json'] = self.json_data
        if self.post_data is not None:
            request_args['json'] = self.post_data

        if method == 'get':
            response = self.session.get(url, stream=True, **request_args)
        elif method == 'post':
            response = self.session.post(url, stream=True, **request_args)
        else:
            result['error'] = "Unknown method"
            return result
        if response.raw._connection and response.raw._connection.sock:
            sock_info = response.raw._connection.sock.getpeername()
        else:
            parsed_url = urlparse(url)
            sock_info = parsed_url.netloc, 0
        result['elapsed'] = response.elapsed.total_seconds()
        result['status_code'] = response.status_code
        result['res_size'] = len(response.content)
        self.test_response = response.text
        result['peer_ip'] = sock_info[0]
        result['peer_port'] = sock_info[1]
        result['response_header'] = response.headers
        return result

    def get_default(self):
        return {
            "url": "https://connect.erc.ua/",
            "verify": False,
            "method": "get",
            "username": "erc\\\\cwrk_ShipmentOrder",
            "password": "",
            "use_proxy_auth": False,
            "proxy_user": "",
            "proxy_pass": "",
            "proxy_ip": "fw201.bs.local.erc",
            "proxy_port": "8080",
            "proxy_auth_method": "ntlm2",
            "proxy_use": False,
            "login_use": False,
            "auth_method": "ntlm2",
            "http_proxy_url": "",
            "https_proxy_url": "",
            # disable trust env variables that disable system proxy
            "trust_env": False,
            "timeout": 5,
            "dns_rules": {
                "1connect.erc.ua": "128.0.168.73",
                "2connect.erc.ua": "62.80.166.214"
            },
            "json_data": None,
            "post_data": None,
        }

    def get_brief_result(self) -> dict:
        size = self.result.get('res_size', 0)
        status_code = self.result.get('status_code', 0)
        return {
            'time': self.result['timing'],
            'speed': size / self.result['timing'],
            'is_error': self.result['is_error'] or status_code >= 400,
            'status_code': status_code,
            'url_error': 1 if status_code >= 400 else 0,
            'connect_error': 1 if self.result['is_error'] else 0,
        }

    def get_small_result(self) -> dict:
        size = self.result.get('res_size', 0)
        status_code = self.result.get('status_code', 0)
        return {
            'time': self.result['timing'],
            'speed': size / self.result['timing'],
            'is_error': self.result['is_error'] or status_code >= 400,
            'status_code': self.result.get('status_code', 0),
            'error': self.result['error'] if self.result['is_error'] else '',
            'url_error': 1 if status_code >= 400 else 0,
            'connect_error': 1 if self.result['is_error'] else 0,
        }
