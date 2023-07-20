import argparse
import json
from threading import Thread

from ping.clear_temp_folder import cleanup_mei
from ping.os_ping import create_ping_service

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='this is utility to transform system ping to json')
    parser.add_argument('server', nargs=1, type=str, action='store')
    parser.add_argument('count', nargs='?', type=int, action='store', default=4)
    parser.add_argument('timeout', nargs='?', type=int, action='store', default=1000)

    arguments = parser.parse_args()
    # pinger = create_ping_service('8.8.8.8')
    urls = arguments.server[0].split(',')
    indexes = []
    response = {'indexes': indexes}
    tests = []
    threads = []
    for index, url in enumerate(urls):
        test = create_ping_service(url, count=arguments.count, interval=arguments.timeout)
        tests.append(test)
        thread = Thread(target=test.run)
        thread.run()
    for thread in threads:
        thread.join()
    for index, test in enumerate(tests):
        response[index] = test.result
        indexes.append({'name': index, 'caption': test.host})
    print(json.dumps(response))
    cleanup_mei()

# .\os_ping_multi.exe 10.224.24.1,10.241.24.1
