from clients.dns_test import DnsTest
from clients.http_test import HTTPTest
from main import load_config
from clients.tcp_test import TCPTest
from clients.udp_test import UdpTest

if __name__ == "__main__":
    json_config = load_config()
    http_test = HTTPTest(json_config)
    http_test.execute_test_procedure()
    #print(http_test.output)
    http_test.print()
    #print(http_test.result)
    http_test.print_result()
    print(http_test.get_brief_result())

    test_tcp_config = {
        'host': 'test.com',
        'port': 80,
        'dns_rules': {
            'test.com': '8.8.8.8'
        }
    }
    tcp_test = TCPTest(test_tcp_config)
    tcp_test.print()
    tcp_test.execute_test_procedure()
    tcp_test.print_result()
    print(tcp_test.get_brief_result())

    tcp_test = UdpTest(test_tcp_config)
    tcp_test.execute_test_procedure()
    tcp_test.print_result()
    print(tcp_test.get_brief_result())

    dns_test = DnsTest({
        'host': 'test.com',
        'port': 53,
        'dns_rules': {
            'test.com': '192.168.88.1'
        }

    })
    dns_test.execute_test_procedure()
    dns_test.print()
    dns_test.print_result()
    print(dns_test.get_brief_result())