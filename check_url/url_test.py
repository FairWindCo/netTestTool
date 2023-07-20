import argparse
import json
from urllib.parse import urlparse

from check_url.cred import username, user_pass
from clients.http_test import HTTPTest
from ping.clear_temp_folder import cleanup_mei

# https://google.com 192.168.88.1 http://fw01.bs.local.erc:8080
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='this is utility to transform system ping to json')
    parser.add_argument('url', nargs=1, type=str, action='store')
    parser.add_argument('server_ip', nargs='?', type=str, action='store', default=None)
    parser.add_argument('proxy', nargs='?', type=str, action='store', default=None)
    parser.add_argument('timeout', nargs='?', type=int, action='store', default=1000)
    arguments = parser.parse_args()
    # pinger = create_ping_service('8.8.8.8')
    config_dict = {
        'url': arguments.url[0],
        'timeout': arguments.timeout,
        'user': username,
        'password': user_pass,
    }

    if arguments.server_ip:
        parsed_url = urlparse(arguments.url[0])
        config_dict['dns_rules'] = {
            parsed_url.netloc: arguments.server_ip
        }
    if arguments.proxy:
        config_dict['http_proxy_url'] = arguments.proxy
        config_dict['https_proxy_url'] = arguments.proxy
        config_dict['proxy_use'] = True
    print(config_dict)
    http = HTTPTest(config_dict)
    http.execute_test_procedure()
    print(json.dumps(http.get_brief_result()))
    cleanup_mei()
