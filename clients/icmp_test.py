from clients.ip_base_test import BaseTCPIPTest
from ping.os_ping import create_ping_service
from ping.ping import Ping


class ICMPTest(BaseTCPIPTest):

    def __init__(self, config_dict, data=None):
        super().__init__(config_dict, data)
        self.os_ping = config_dict.get('os_ping', False)

    def get_default(self):
        conf = super().get_default()
        conf.update({
            'udp': False,
            'timeout': 1000,
            'count': 5,
            'packet_size': 55,
        })
        return conf

    def _test_procedure(self):
        if self.os_ping:
            os_pinger = create_ping_service(self.host, self.count, self.packet_size, self.timeout)
            return os_pinger.run()
        else:
            p = Ping(self.host, udp=self.udp, timeout=self.timeout, packet_size=self.packet_size)
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
            'avg': self.result.get('avg_rtt', 0),
            'loss': self.result.get('loss', 100),
            'ip': self.result.get('parent', self.host),
        }
        return res
