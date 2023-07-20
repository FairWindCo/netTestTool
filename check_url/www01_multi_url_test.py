import argparse
import json
from threading import Thread

from check_url.multi_url_test import one_test
from ping.clear_temp_folder import cleanup_mei

if __name__ == "__main__":
    server_ip = '192.168.38.136'
    indexes = []
    response = {'indexes': indexes}
    tests = []
    threads = []

    urls = (
        'https://connect.erc.ua/Tools/Ping/',
        'https://connect.erc.ua/Tools/Ping/?db=1',
    )

    for index, url in enumerate(urls):
        test = one_test(url, server_ip, None, None)
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