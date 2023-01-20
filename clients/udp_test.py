import socket

from clients.ip_base_test import BaseTCPIPTest


class UdpTest(BaseTCPIPTest):
    def get_default(self):
        return {
            'host': "",
            'port': 80,
            'timeout': 5,
            'message': ''
        }

    def check_error(self, err):
        return BaseTCPIPTest.socker_error(super().check_error(err))

    def init_result(self, **additional_fields):
        return super().init_result(host=self.host,
                                   port=self.port,
                                   **additional_fields)

    def create_message(self):
        if not self.message:
            return '0'.encode()
        else:
            return self.message.encode()


    def test_procedure(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket = sock
        message = self.create_message()
        if self.host in self.dns_rules:
            host_name = self.dns_rules[self.host]
        else:
            host_name = self.host
        host_ip = socket.gethostbyname(host_name)
        sock.settimeout(self.timeout)
        self.result['peer'] = host_ip, self.port
        bytes_send = sock.sendto(message, (host_ip, self.port))
        try:
            _ = sock.recvfrom(1024)
        finally:
            sock.close()
        return {
            'bytes_send': bytes_send,
        }

