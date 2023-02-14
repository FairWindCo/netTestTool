import socket

from clients.ip_base_test import BaseTCPIPTest


class TCPTest(BaseTCPIPTest):
    def get_default(self):
        return {
            'host': "127.0.0.1",
            'port': 8080,
            'timeout': 5,
        }


    def _test_procedure(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket = sock
        sock.settimeout(self.timeout)
        if self.host in self.dns_rules:
            host_name = self.dns_rules[self.host]
        else:
            host_name = self.host
        host_ip = socket.gethostbyname(host_name)
        sock.settimeout(self.timeout)
        self.result['peer'] = host_ip, self.port
        sock.connect((host_ip, self.port))
        result = self._on_connect(socket=sock)
        sock.close()
        return result
