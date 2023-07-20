import argparse
import json
from threading import Thread

from check_url.multi_url_test import one_test
from ping.clear_temp_folder import cleanup_mei

if __name__ == "__main__":
    server_ip = '192.168.38.135'
    indexes = []
    response = {'indexes': indexes}
    tests = []
    threads = []

    urls = (
        'https://common.sites.local.erc/api/common/ping',
        'https://common.sites.local.erc/api/common/ping?db=1',
        'https://sale.local.erc/Tools/Ping/',
        'https://sale.local.erc/Tools/Ping/?db=1'
    )

    tests = [one_test(url, server_ip, None, None).create_test_thread_and_run() for url in urls]
    for index, test in enumerate(tests):
        test.wait_for_test_end()
        response[index] = test.get_brief_result()
        indexes.append({'name': index, 'caption': urls[index]})
    print(json.dumps(response))
    cleanup_mei()


#.\multi_url_test.exe https://common.sites.local.erc/api/common/ping,https://common.sites.local.erc/api/common/ping?db=1 192.168.38.135