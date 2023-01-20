from clients.udp_test import UdpTest

if __name__ == "__main__":
    test_tcp_config = {
        'host': 'test.com',
        'port': 8081,
        'dns_rules': {
            'test.com': '127.0.0.1'
        }
    }
    tcp_test = UdpTest(test_tcp_config)
    tcp_test.execute_test_procedure()
    tcp_test.print()
    tcp_test.print_result()
    print(tcp_test.get_brief_result())
