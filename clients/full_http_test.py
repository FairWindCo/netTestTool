import socket
import time
from urllib.parse import urlparse

from clients.http_test import HTTPTest


class FullHTTPTest(HTTPTest):

    def __init__(self, config_dict):
        super().__init__(config_dict)
        self.need_count = config_dict.get('need_count', None)

    def get_brief_result(self):
        res = super().get_brief_result()
        res['detail_info'] = {}
        res['count'] = self.result['count']
        if self.result['error']:
            res['error'] = self.result['error']
        for key, result in self.result['ips'].items():
            res['detail_info'][key] = {
                'is_error': result['is_error'],
                'time': result['part_time']
            }
        return res

    def test_procedure(self):
        uri = urlparse(self.url)
        host_name, aliases, ips = socket.gethostbyname_ex(uri.hostname)
        test_count = len(ips)
        result = {'ips': {}, 'count': test_count}
        total = False
        for ip in ips:
            self.dns_rules[self.url] = ip
            try:
                start_test_time = time.time()
                res = super().test_procedure()
                result['ips'][ip] = res
                result['ips'][ip]['is_error'] = False
                result['ips'][ip]['part_time'] = (time.time() - start_test_time)
            except Exception as e:
                result['ips'][ip] = {
                    'is_error': True,
                    'error': self.check_error(e),
                    'part_time': 0,
                }
                total = True

        result['is_error'] = total
        if self.need_count is not None:
            result['is_error'] = self.need_count > test_count
            result['error'] = f'need {self.need_count} ip, but have {test_count}'
        return result
