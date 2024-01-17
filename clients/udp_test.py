import socket
from typing import Optional, Union

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

    def _create_message(self):
        if not self.message:
            return '0'.encode()
        else:
            return self.message.encode()

    def _on_connect(self, *arg, **kwarg) -> (bool, str):
        return super()._on_connect(*arg, **kwarg)

    def _communicate(self, request: Optional[Union[str, bytes]], *arg, **kwarg) -> Optional[Union[str, bytes, dict]]:
        message = self._create_message()
        sock, host_ip, port, *_ = arg
        bytes_send = sock.sendto(message, (host_ip, port))
        response = sock.recvfrom(1024)
        return {
            'response': response,
            'bytes_send': bytes_send,
        }

    def _check_response(self, response: Optional[Union[str, bytes, dict]]) -> dict:
        return {
            'bytes_send': response.get('bytes_send', 0),
            'is_error': False,
        }

    def _test_procedure(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket = sock
        if hasattr(self, 'dns_rules') and self.host in self.dns_rules:
            host_name = self.dns_rules[self.host]
        else:
            host_name = self.host
        host_ip = socket.gethostbyname(host_name)
        sock.settimeout(self.timeout)
        self.result['peer'] = host_ip, self.port
        try:
            return self._on_connect(sock, host_ip, self.port)
        finally:
            sock.close()

if __name__ == '__main__':
    udp = UdpTest({
        'host': '127.0.0.1',
        'port': 8080
    })
    print(udp.execute_test_procedure())