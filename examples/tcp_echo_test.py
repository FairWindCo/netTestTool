import socket

from clients.ip_base_test import BaseTCPIPTest


class TCPEchoTest(BaseTCPIPTest):
    def get_default(self):
        return {
            'host': "127.0.0.1",
            'port': 8080,
            'timeout': 5,
        }

    def init_result(self, **additional_fields):
        return super().init_result(host=self.host,
                                   port=self.port,
                                   **additional_fields)

    def test_procedure(self):
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
        message = self.create_message()
        if message:
            sock.send(message)
        response = sock.recv(len(message))
        result = {}
        if message != response:
            result = {
                'is_error': True,
            }
        sock.close()
        return result
