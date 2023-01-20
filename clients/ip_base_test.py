import socket

from clients.base_test import BaseTest


class BaseTCPIPTest(BaseTest):
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

    def create_message(self):
        return None

    def check_response(self, message):
        return True, ""

    def patch_hosts_info(self):
        dns_cache = {}
        dns_rules = self.dns_rules
        if dns_rules is not None:
            self.print_info(self.LogLevel.LOG_OPERATION, "PATCH gethostbyname")
            self.print_info(self.LogLevel.LOG_PARAMS, dns_rules)
            prv_getaddrinfo = socket.gethostbyname

            def new_gethostbyname(host):
                print('search host', host)
                try:
                    return dns_cache[host]
                except KeyError:
                    res = prv_getaddrinfo(host)
                    dns_cache[host] = res
                    self.print_info(self.LogLevel.LOG_INFO,
                                    f"RESOLVE host {host} {res}")
                    return res

            socket.gethostbyname = new_gethostbyname

    def patch_dns(self):
        dns_cache = {}
        dns_rules = self.dns_rules
        if dns_rules is not None:
            self.print_info(self.LogLevel.LOG_OPERATION, "PATCH DNS OPERATION")
            self.print_info(self.LogLevel.LOG_PARAMS, dns_rules)
            prv_getaddrinfo = socket.getaddrinfo

            def new_getaddrinfo(*args):
                try:
                    return dns_cache[args]
                except KeyError:
                    replaced_ip = dns_rules.get(args[0], None)
                    if replaced_ip is not None:
                        # res = [(socket.AddressFamily.AF_INET, args[3], 0, '', (replaced_ip, args[1]))]
                        res = prv_getaddrinfo(replaced_ip, *args[1:])
                    else:
                        res = prv_getaddrinfo(*args)
                    dns_cache[args] = res
                    self.print_info(self.LogLevel.LOG_INFO,
                                    f"RESOLVE {args[0]}:{args[1]} TO {[adr[4] for adr in res]}")
                    return res

            socket.getaddrinfo = new_getaddrinfo

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
