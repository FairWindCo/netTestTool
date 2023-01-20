import socket
import time

from clients.icmp_test import ICMPTest


class FullICMPTest(ICMPTest):

    def get_brief_result(self):
        res = {
            'is_error': self.result['is_error'],
            'error': self.result['error'],
            'detail_info': {}
        }
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
        result = {'ips': {}}
        total = True
        for ip in ips:
            self.host = ip
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
                    'avg': 0,
                    'loss': 100
                }
                total = False

        result['is_error'] = total
        return result
