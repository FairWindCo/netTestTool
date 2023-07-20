import time
from enum import Enum

from rich import pretty
from rich.console import Console

console = Console()
pretty.install()


def convert_error(err):
    if hasattr(err, 'args'):
        err_args = getattr(err, 'args')
        if err_args:
            if len(err_args) > 0:
                if hasattr(err.args[0], 'reason'):
                    reason = getattr(err.args[0], 'reason')
                    return convert_error(reason)
                else:
                    return str(err.args[0])
    return str(err)


class BaseTest:
    view_errors = True

    class LogLevel(Enum):
        NO_LOG = 0, ''
        LOG_CRITICAL = 1, '[bold red]'
        LOG_ERROR = 2, '[red]'
        LOG_WARNING = 3, '[yellow]'
        LOG_PARAMS = 4, '[green]'
        LOG_OPERATION = 5, '[bold green]'
        LOG_INFO = 6, '[blue]'
        LOG_DEBUG = 7, ''

    def init_result(self, **additional_fields):
        result = {
            'is_error': False,
            'error': None,
            'timing': 0
        }
        if additional_fields:
            result.update(additional_fields)
        return result

    def __init__(self, config_dict):
        self.trait_unknown_as_null = False
        config = self.get_default()

        if config_dict is not None:
            config.update(config_dict)

        self.debug_level = config.get('debug_level', 8)
        self.config = config
        self.output = []
        self.test_time = 0
        self.trait_unknown_as_null = config.get('trait_unknown_as_null', False)
        self.direct_out = config.get("direct_out", False)
        self.direct_out_error = config.get("direct_out_error", False)
        self.result = self.init_result()

        for name, value in config.items():
            self.print_info(self.LogLevel.LOG_DEBUG, f"config {name}={value}")
            setattr(self, name, value)

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            try:
                config = getattr(self, 'config')
                if name in config:
                    return config[name]
                if self.trait_unknown_as_null:
                    return None
                else:
                    raise
            except AttributeError:
                raise e

    def prepare_for_test(self):
        pass

    def _test_procedure(self):
        return {}

    def execute_test_procedure(self):
        self.prepare_for_test()
        start_test_time = time.time()
        try:
            self.result['is_error'] = False
            self.result.update(self._test_procedure())
        except BaseException as e:
            if self.view_errors:
                console.print_exception()
            self.result['error'] = self.check_error(e)
            self.result['is_error'] = True
            self.result['exception'] = e
        self.test_time = (time.time() - start_test_time)
        self.result['timing'] = self.test_time
        return self.result

    def check_error(self, err: BaseException):
        if self.direct_out_error:
            console.print_exception()
        self.print_info(BaseTest.LogLevel.LOG_ERROR, err)
        return convert_error(err)

    def get_result(self) -> dict:
        return self.result

    def get_output(self):
        return self.output

    def get_default(self) -> dict:
        return {}

    def print_info(self, message_level: LogLevel, message):
        if self.debug_level > message_level.value[0]:
            if self.direct_out:
                console.print(f"{message_level.value[1]}{message}")
            else:
                self.output.append(f"{message_level.value[1]}{message}")

    def print(self):
        for line in self.output:
            console.print(line)

    def print_result(self):
        console.print(self.result)

    def get_brief_result(self) -> dict:
        return {
            'time': self.result['timing'],
            'is_error': self.result['is_error']
        }
