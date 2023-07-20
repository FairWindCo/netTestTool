import argparse
import json
from threading import Thread
from urllib.parse import urlparse

from check_url.cred import username, user_pass
from clients.http_test import HTTPTest
from ping.clear_temp_folder import cleanup_mei


def one_test(url, server_ip, proxy, timeout):
    config_dict = {
        'url': url,
        'timeout': timeout,
        'user': username,
        'password': user_pass,
    }

    if server_ip:
        parsed_url = urlparse(url)
        config_dict['dns_rules'] = {
            parsed_url.netloc: server_ip
        }
    if proxy:
        config_dict['http_proxy_url'] = proxy
        config_dict['https_proxy_url'] = proxy
        config_dict['proxy_use'] = True
    #print(config_dict)
    http = HTTPTest(config_dict)
    return http

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='this is utility to transform system ping to json')
    parser.add_argument('url', nargs=1, type=str, action='store')
    parser.add_argument('server_ip', nargs='?', type=str, action='store', default=None)
    parser.add_argument('proxy', nargs='?', type=str, action='store', default=None)
    parser.add_argument('timeout', nargs='?', type=int, action='store', default=1000)
    arguments = parser.parse_args()
    # pinger = create_ping_service('8.8.8.8')
    urls = arguments.url[0].split(',')
    server_ip = arguments.server_ip
    proxy = arguments.proxy
    timeout = arguments.timeout
    indexes = []
    response = {'indexes': indexes}
    tests = []
    threads = []
    for index, url in enumerate(urls):
        test = one_test(url, server_ip, proxy, timeout)
        tests.append(test)
        thread = Thread(target=test.execute_test_procedure)
        thread.run()
    for thread in threads:
        thread.join()
    for index, test in enumerate(tests):
        response[index] = test.get_brief_result()
        indexes.append({'name': index, 'caption': urls[index]})
    print(json.dumps(response))
    cleanup_mei()


#.\multi_url_test.exe https://common.sites.local.erc/api/common/ping,https://common.sites.local.erc/api/common/ping?db=1 192.168.38.135