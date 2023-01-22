import socket
import time

from clients.icmp_test import ICMPTest


class FullICMPTest(ICMPTest):

    def __init__(self, config_dict):
        super().__init__(config_dict)
        self.need_count = config_dict.get('need_count', None)

    def get_brief_result(self):
        res = {
            'is_error': self.result['is_error'],
            'time': self.result['timing'],
            'error': self.result['error'],
            'count': self.result['count'],
            'detail_info': {}
        }
        if self.result['error']:
            res['error'] = self.result['error']
        for key, result in self.result['ips'].items():
            res['detail_info'][key] = {
                'is_error': result['is_error'],
                'time': result['part_time'],
                'avg': result['avg_rtt'],
                'loss': result['loss'],
            }
        return res

    def test_procedure(self):
        host_name, aliases, ips = socket.gethostbyname_ex(self.host)
        test_count = len(ips)
        result = {'ips': {}, 'count': test_count}
        total = False
        for ip in ips:
            self.host = ip
            try:
                start_test_time = time.time()
                res = super().test_procedure()
                result['ips'][ip] = res
                result['ips'][ip]['is_error'] = res['is_error']
                result['ips'][ip]['part_time'] = (time.time() - start_test_time)
                total |= res['is_error']
            except Exception as e:
                result['ips'][ip] = {
                    'is_error': True,
                    'error': self.check_error(e),
                    'part_time': 0,
                    'avg': 0,
                    'loss': 100
                }
                total = True

        result['is_error'] = total
        if self.need_count is not None and self.need_count > test_count:
            result['is_error'] = self.need_count < test_count
            result['error'] = f'need {self.need_count} ip, but have {test_count}'
        return result
