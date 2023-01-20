

from clients.ip_base_test import BaseTCPIPTest
from ping.ping import Ping


class ICMPTest(BaseTCPIPTest):
    def get_default(self):
        conf = super().get_default()
        conf.update({
            'udp': False,
            'timeout': 1000,
            'count': 5,
            'packet_size': 55,
        })
        return conf

    def test_procedure(self):
        p = Ping(self.host, udp=self.udp, timeout=self.timeout,packet_size=self.packet_size)
        res = p.run(self.count)
        return {
            'parent': res.destination_ip,
            'is_error': self.count == res.packet_lost,
            'max_rtt': res.max_rtt,
            'avg_rtt': res.avg_rtt,
            'min_rtt': res.min_rtt,
            'loss': res.packet_lost
        }

    def get_brief_result(self):
        res = super().get_brief_result()
        res['detail'] = {
            'avg': self.result['avg_rtt'],
            'loss': self.result['loss'],
            'ip': self.result['parent']
        }
        return res

