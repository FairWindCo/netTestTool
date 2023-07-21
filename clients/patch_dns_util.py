import socket


class PatchDNSService:
    def __init__(self) -> None:
        super().__init__()
        self.original_getaddrinfo = socket.getaddrinfo
        self.dns_rules = {}
        self.dns_cache = {}
        self.dns_cache_for_rules = {}
        self.rule_activate = 0

    def activate_rules(self, dns_rules):
        if dns_rules:
            self.rule_activate += 1
            self.dns_rules.update(dns_rules)
            for key in dns_rules.keys():
                if key in self.dns_cache_for_rules:
                    del self.dns_cache_for_rules[key]
            self._patch_dns()

    def deactivate_rules(self):
        self.rule_activate -= 1
        if self.rule_activate == 0:
            socket.getaddrinfo = self.original_getaddrinfo

    def _patch_dns(self):
        if self.dns_rules:
            prv_getaddrinfo = self.original_getaddrinfo

            def new_getaddrinfo(*args):
                cached_rule = self.dns_cache_for_rules.get(args[0], None)
                if cached_rule:
                    res = cached_rule
                else:
                    dns_cached = self.dns_cache.get(args[0], None)
                    if dns_cached:
                        res = dns_cached
                    else:
                        replaced_ip = self.dns_rules.get(args[0], None)
                        if replaced_ip is not None:
                            # res = [(socket.AddressFamily.AF_INET, args[3], 0, '', (replaced_ip, args[1]))]
                            res = prv_getaddrinfo(replaced_ip, *args[1:])
                            self.dns_cache_for_rules[args[0]] = res
                        else:
                            res = prv_getaddrinfo(*args)
                            self.dns_cache[args[0]] = res
                # print(args[0], res[0][4])
                return res

            socket.getaddrinfo = new_getaddrinfo


dns_service_control = PatchDNSService()
