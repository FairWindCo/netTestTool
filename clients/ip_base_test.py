from typing import Union, Optional

from clients.base_test import BaseTest
from clients.patch_dns_util import dns_service_control


class BaseTCPIPTest(BaseTest):

    def __init__(self, config_dict, data=None):
        super().__init__(config_dict, data)
        self.host = config_dict.get('target', config_dict.get('host', None))

    @staticmethod
    def socker_error(error):
        if error == 10061 or error == '10061':
            return "connection refused"
        elif error == 10060 or error == '10060':
            return "timeout"
        elif error == 10054 or error == '10054':
            return "An existing connection was forcibly closed by the remote host"

        else:
            return error

    def _on_connect(self, *arg, **kwarg) -> (bool, str):
        mes = self._create_message()
        response = self._communicate(mes, *arg, **kwarg)
        result = self._check_response(response)
        return self._check_response(result)

    def _communicate(self, request: Optional[Union[str, bytes]], *arg, **kwarg) -> Optional[Union[str, bytes, dict]]:
        return request

    def _create_message(self) -> Optional[Union[str, bytes]]:
        return None

    def _check_response(self, response: Optional[Union[str, bytes, dict]]) -> dict:
        return {
            'is_error': False,
            'res_message': response
        }

    def patch_hosts_info(self):
        dns_service_control.activate_rules(self.dns_rules)

    def patch_dns(self):
        dns_service_control.activate_rules(self.dns_rules)

    def check_error(self, err):
        return BaseTCPIPTest.socker_error(super().check_error(err))

    def prepare_for_test(self):
        super().prepare_for_test()
        if self.dns_rules:
            self.patch_dns()

    def get_default(self):
        return {
            "host": '127.0.0.1',
            "dns_rules": {},
        }

    def clear_after_test(self):
        dns_service_control.deactivate_rules()
        super().clear_after_test()
