import socket


class PatchDNSService:
    def __init__(self) -> None:
        super().__init__()
        self.original_getaddrinfo = socket.getaddrinfo
        self.dns_rules = {}
        self.dns_cache = {}
        self.rule_activate = 0

    def activate_rules(self, dns_rules):
        if dns_rules:
            self.dns_cache.clear()
            self.rule_activate += 1
            self.dns_rules.update(dns_rules)
            self._patch_dns()

    def deactivate_rules(self):
        self.rule_activate -= 1
        if self.rule_activate == 0:
            socket.getaddrinfo = self.original_getaddrinfo

    def _patch_dns(self):
        dns_cache = self.dns_cache
        dns_rules = self.dns_rules
        if dns_rules:
            prv_getaddrinfo = self.original_getaddrinfo

            def new_getaddrinfo(*args):
                try:
                    res = dns_cache[args]
                    #print(args[0], res, args)
                    return res
                except KeyError:
                    replaced_ip = dns_rules.get(args[0], None)
                    if replaced_ip is not None:
                        # res = [(socket.AddressFamily.AF_INET, args[3], 0, '', (replaced_ip, args[1]))]
                        res = prv_getaddrinfo(replaced_ip, *args[1:])
                    else:
                        res = prv_getaddrinfo(*args)
                    dns_cache[args] = res
                    #print(args[0], res)
                    return res

            socket.getaddrinfo = new_getaddrinfo


dns_service_control = PatchDNSService()
