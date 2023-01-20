import socket
import time
from urllib.parse import urlparse

from clients.http_test import HTTPTest


class FullHTTPTest(HTTPTest):

    def get_brief_result(self):
        res = super().get_brief_result()
        res['detail_info'] = {}
        for key, result in self.result['ips'].items():
            res['detail_info'][key] = {
                'is_error': result['is_error'],
                'time': result['part_time']
            }
        return res

    def test_procedure(self):
        uri = urlparse(self.url)
        host_name, aliases, ips = socket.gethostbyname_ex(uri.hostname)
        result = {'ips': {}}
        total = True
        for ip in ips:
            self.dns_rules[self.url] = ip
            try:
                start_test_time = time.monotonic_ns()
                res = super().test_procedure()
                result['ips'][ip] = res
                result['ips'][ip]['is_error'] = False
                result['ips'][ip]['part_time'] = (time.monotonic_ns() - start_test_time) / 10 ** 9
            except Exception as e:
                result['ips'][ip] = {
                    'is_error': True,
                    'error': self.check_error(e),
                    'part_time': 0,
                }
                total = False

        result['is_error'] = total
        return result
