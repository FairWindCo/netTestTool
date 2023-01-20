import concurrent.futures
import datetime
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from clients.dns_test import DnsTest
from clients.full_http_test import FullHTTPTest
from clients.full_icmp_test import FullICMPTest
from clients.http_test import HTTPTest
from clients.icmp_test import ICMPTest
from clients.tcp_test import TCPTest
from clients.udp_test import UdpTest
from servers.multi_thread_server import ThreadedTcpSocketServer
from servers.tcp_echo_server import EchoServer
from servers.threaded_udp_server import ThreadedUdpSocketServer
from telegram import send_message_to_all


class ComplexTest:

    def __init__(self, config_dict: dict) -> None:
        super().__init__()
        self.templates = config_dict.get('template', {})
        self.tests = config_dict.get('tests', {})
        self.servers = config_dict.get('servers', {})
        self.stop_server_after_test = config_dict.get('stop_servers', False)
        self.active_servers = []
        self.active_server_threads = []
        self.active_tests = {}
        self.concurrent = config_dict.get('concurrent', True)
        self.max_workers = config_dict.get('max_workers', None)
        self.max_execution_time = config_dict.get('max_execution_time', None)

    @staticmethod
    def get_test_by_name(test_name: str, config_dict: dict):
        test_name = test_name.upper().strip()
        if test_name == 'DNS':
            return DnsTest(config_dict)
        if test_name == 'HTTP':
            return HTTPTest(config_dict)
        if test_name == 'FULL_HTTP':
            return FullHTTPTest(config_dict)
        if test_name == 'FULL_PING':
            return FullICMPTest(config_dict)
        if test_name == 'TCP':
            return TCPTest(config_dict)
        if test_name == 'UDP':
            return UdpTest(config_dict)
        if test_name == 'PING':
            return ICMPTest(config_dict)
        raise ValueError("Incorrect Test Type:", test_name)

    @staticmethod
    def get_server_by_name(server_name, config_dict):
        test_name = server_name.upper().strip()
        port = config_dict.get('port', None)
        interfaces = config_dict.get('host', None)
        buffer_size = config_dict.get('buffer_size', None)
        if test_name == 'TCP':
            return ThreadedTcpSocketServer(port=port, bidning=interfaces, buffer_size=buffer_size)
        if test_name == 'UDP':
            return ThreadedUdpSocketServer(port=port, bidning=interfaces, max_buffer=buffer_size)
        if test_name == 'TCP_ECHO':
            return EchoServer(port=port, bidning=interfaces, buffer_size=buffer_size)
        raise ValueError("Incorrect Test Type:", test_name)

    def create_test_config(self, test: dict) -> dict:
        test_template_name = test.get('template', None)
        result = {}
        if test_template_name:
            template = self.templates.get(test_template_name)
            result.update(self.create_test_config(template))
        result.update(test)
        return result

    @staticmethod
    def create_test(test_config):
        test_type = test_config['type']
        return ComplexTest.get_test_by_name(test_type, test_config)

    @staticmethod
    def create_server(test_config):
        test_type = test_config['type']
        return ComplexTest.get_server_by_name(test_type, test_config)

    def run_servers(self):
        for server_name, server_config in self.servers.items():
            server = self.create_server(server_config)
            self.active_servers.append(server)
            thread = threading.Thread(target=server.run)
            thread.start()
            self.active_server_threads.append(thread)

    def join_servers(self):
        for thread in self.active_server_threads:
            thread.join()

    def stop_all_servers(self):
        if self.stop_server_after_test:
            for server in self.active_servers:
                server.stop()

    def run_test(self, test_desc, test_name=None):
        if test_name is None:
            test_for_config = self.create_test_config(test_desc)
            test = ComplexTest.create_test(test_for_config)
        else:
            if test_name is self.active_tests:
                return self.active_tests[test_name]
            else:
                test_for_config = self.create_test_config(test_desc)
                test = ComplexTest.create_test(test_for_config)
                self.active_tests[test_name] = test
        test.execute_test_procedure()
        return test.get_result() if test_desc.get('full_result', False) else test.get_brief_result()

    def run(self):
        # result = {}
        # for test_name, test_desc in self.tests.items():
        #     result[test_name] = self.run_test(test_desc)
        result = {test_name: self.run_test(test_desc) for test_name, test_desc in self.tests.items()}
        self.stop_all_servers()
        return result

    def run_concurred(self, max_worker=None, max_execution_time=None):
        executor = ThreadPoolExecutor(max_workers=max_worker)
        result = {}
        try:

            futures = {test_name: executor.submit(self.run_test, test_desc)
                       for test_name, test_desc in self.tests.items()}
            concurrent.futures.wait(futures.values(), timeout=max_execution_time)
            for name_of_test, future in futures.items():
                try:
                    result[name_of_test] = future.result(timeout=max_execution_time)
                except concurrent.futures.CancelledError:
                    result[name_of_test] = {
                        'is_error': True,
                        'error': f'Canceled',
                    }
                except concurrent.futures.TimeoutError:
                    result[name_of_test] = {
                        'is_error': True,
                        'error': f'timeout: {max_execution_time}',
                    }
        finally:
            self.stop_all_servers()
            executor.shutdown(wait=False)
        return result

    @staticmethod
    def load_config(config_file='config.json'):
        with open(config_file, 'rt') as f:
            return json.load(f)

    def run_all_tests(self, concurrent_mode=True, max_workers=None, max_execution_time=None):
        start_test_time = time.monotonic()
        if concurrent_mode or self.concurrent:
            result = self.run_concurred(max_worker=max_workers or self.max_workers,
                                        max_execution_time=max_execution_time or self.max_execution_time)
        else:
            result = self.run()
        # if not complex.stop_server_after_test:
        #     complex.join_servers()
        total_result = True
        for _result in result.values():
            if _result['is_error']:
                total_result = False
                break
        return {
            'all_test_time': (time.monotonic() - start_test_time),
            'all_test_count': len(result),
            'all_test_success': total_result,  # all(not _result['is_error'] for _result in result.values()),
            'datetime': datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            'results': result,
            'timestamp': time.time(),
        }

    @staticmethod
    def create_complex_test(filename="config.json", with_servers=True):
        _config = ComplexTest.load_config(filename)
        complex_tests = ComplexTest(_config)
        if with_servers:
            complex_tests.run_servers()
        return complex_tests, _config

    @staticmethod
    def run_tests(filename="config.json", with_servers=True):
        complex_tests, _config = ComplexTest.create_complex_test(filename, with_servers)
        return complex_tests.run_all_tests(_config.get('concurrent', True),
                                           _config.get('max_worker', None),
                                           _config.get('max_execution_time', None))

    @staticmethod
    def form_error_message(_config, last_result):
        message_error_template = _config.get('message_error_template', 'Ошибка в тесте {} не доступен {}')
        messages_errors = ['Проблемы доступа {}'.format(last_result['datetime']), ]
        for name, detail in last_result['results'].items():
            if detail['is_error']:
                detail_info = detail.get('detail_info', {})
                for ip, info in detail_info.items():
                    if info['is_error']:
                        messages_errors.append(message_error_template.format(name, ip, **info))
                detail_info = detail.get('detail', {})
                if detail_info:
                    messages_errors.append(
                        message_error_template.format(name, detail_info['ip'], **detail_info))
        return '\n'.join(messages_errors)


def safe_file(res, file_name='report.json'):
    with open(file_name, 'w') as f:
        json.dump(res, f)


if __name__ == "__main__":
    complex_test, config = ComplexTest.create_complex_test()
    interval = config.get('all_test_interval', 60)
    max_errors = config.get('max_errors_count', 3)
    report_file = config.get('report_file', 'report.json')
    safe_report = config.get('safe_report', True)
    current_error_count = 0
    while True:
        res = complex_test.run_all_tests()
        print(res)
        if safe_report:
            safe_file(res, report_file)
        if not res['all_test_success']:
            current_error_count += 1
            if current_error_count == max_errors:
                mes = ComplexTest.form_error_message(config, res)
                print(mes)
                send_message_to_all(config, mes)
        else:
            if current_error_count > 0:
                pass
            current_error_count = 0
        time.sleep(interval)

        # config = ComplexTest.load_config("config.json")
    # complex = ComplexTest(config)
    #
    # # start = datetime.datetime.now()
    # # print(complex.run())
    # # print(datetime.datetime.now() - start)
    # #
    # # start = datetime.datetime.now()
    # # print(complex.run_concurred(max_worker=15, max_execution_time=5))
    # # print(datetime.datetime.now() - start)
    #
    # # start = datetime.datetime.now()
    # # print(complex.run_concurred(max_execution_time=5))
    # # print(datetime.datetime.now() - start)
