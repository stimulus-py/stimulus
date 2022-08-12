# Decorator to register function with stimulator
import functools
from types import SimpleNamespace
import stimulus.core.log
import stimulus.core.automation

S = SimpleNamespace()


def run_when(stimulator, *args, **kwargs):
    def inner_decorator(func):
        stimulator(func, *args, **kwargs)
        return func

    return inner_decorator


def _logger(level, msg, *args, stacklevel=1, **kwargs):
    stacklevel += 1
    name = stimulus.core.automation.get_current_automation().name
    stimulus.core.log.user_log(name, level, msg, *args, stacklevel=stacklevel, **kwargs)


logger = SimpleNamespace()
logger.debug = functools.partial(_logger, "debug")
logger.info = functools.partial(_logger, "info")
logger.warning = functools.partial(_logger, "warning")
logger.error = functools.partial(_logger, "error")
logger.critical = functools.partial(_logger, "critical")
