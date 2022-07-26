# Decorator to register function with stimulator
import functools
from types import SimpleNamespace
import stimulus.core.logging
import stimulus.core.automation

S = SimpleNamespace()

def run_when(stimulator, *args, **kwargs):
    def inner_decorator(func):
        stimulator(func, *args, **kwargs)
        return func
    return inner_decorator

def _logger(level,msg):
    name = stimulus.core.automation.get_current_automation().name
    stimulus.core.logging.user_log(name, level, msg)

logger = SimpleNamespace()
logger.debug = functools.partial(_logger,'debug') 
logger.info = functools.partial(_logger,'info')
logger.warning = functools.partial(_logger,'warning')
logger.error = functools.partial(_logger,'error')
logger.critical = functools.partial(_logger,'critical')

    
