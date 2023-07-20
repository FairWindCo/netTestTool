import argparse
import json
import socket

from check_url.multi_url_test import one_test

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='this is utility to transform system ping to json')
    parser.add_argument('-s', '--small_result', action='store_true')
    parser.add_argument('-f', '--full_result', action='store_true')
    arguments = parser.parse_args()
    test_blocks = ({
                       'WEBLOCAL0101.local.erc': (
                           'https://common.sites.local.erc/api/common/ping',
                           'https://common.sites.local.erc/api/common/ping?db=1',
                           'https://sale.local.erc/Tools/Ping/',
                           'https://sale.local.erc/Tools/Ping/?db=1'
                       ),
                       'WEBPUBLIC0101.local.erc': (
                           'http://connect.erc.ua/Tools/Ping/',
                           'http://connect.erc.ua/Tools/Ping/?db=1',
                       ),
                   }, {
                       'WEBLOCAL0201.local.erc': (
                           'https://common.sites.local.erc/api/common/ping',
                           'https://common.sites.local.erc/api/common/ping?db=1',
                           'https://sale.local.erc/Tools/Ping/',
                           'https://sale.local.erc/Tools/Ping/?db=1'
                       ),
                       'WEBPUBLIC0201.local.erc': (
                           'http://connect.erc.ua/Tools/Ping/',
                           'http://connect.erc.ua/Tools/Ping/?db=1',
                       ),
                   })
    indexes = []
    response = {'indexes': indexes}
    tests = []
    threads = []
    index = 0
    for block_test_index, test_block in enumerate(test_blocks):
        tests = []
        for server_name, urls in test_block.items():
            for url in urls:
                tests.append(one_test(url, socket.gethostbyname(server_name), None, None,
                         (server_name, url)).create_test_thread_and_run())
        for test in tests:
            test.wait_for_test_end()
            if arguments.small_result:
                response[index] = test.get_small_result()
            elif arguments.full_result:
                response[index] = test.get_result()
            else:
                response[index] = test.get_brief_result()
            indexes.append({'name': index, 'caption': f'{test.additional_data[0]}:{test.additional_data[1]}'})
            index += 1

    print(json.dumps(response))

    # .\multi_url_test.exe https://common.sites.local.erc/api/common/ping,https://common.sites.local.erc/api/common/ping?db=1 192.168.38.135
