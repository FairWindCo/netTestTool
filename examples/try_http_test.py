from clients.http_test import HTTPTest
from main import load_config

if __name__ == "__main__":
    json_config = load_config()
    http_test = HTTPTest(json_config)
    http_test.execute_test_procedure()
    #print(http_test.output)
    http_test.print()
    #print(http_test.result)
    http_test.print_result()
    print(http_test.get_brief_result())
