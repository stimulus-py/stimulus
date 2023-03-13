import logging
import logging.handlers
import sys

# import stimulus.core.automation

_logger = logging.getLogger("Stimulus")  # Actual logger
logger = logging.LoggerAdapter(
    _logger, {"type": "-", "s_name": "Stimulus"}
)  # logger with stimulus type set
_device_logger = _logger.getChild("device")
_automation_logger = _logger.getChild("automation")

_logger.setLevel(logging.INFO)


def user_log(name, level, msg, *args, stacklevel=1, extra={}, **kwargs) -> None:
    stacklevel += 1
    extra.update({"type": "@", "s_name": name})
    logger = _automation_logger.getChild(name)
    logger_level = getattr(logger, level)
    logger_level(msg, *args, extra=extra, stacklevel=stacklevel, **kwargs)


def device_logger(name):
    return logging.LoggerAdapter(_device_logger, {"type": "#", "s_name": name})


simple_formatter = logging.Formatter(
    "%(asctime)s.%(msecs)03d %(levelname)s %(type)s %(s_name)s : %(message)s",
    "%m-%d %H:%M:%S",
)
verbose_formatter = logging.Formatter(
    "%(asctime)s.%(msecs)03d %(levelname)s %(type)s %(s_name)s : %(message)s [%(filename)s:%(module)s.%(funcName)s:%(lineno)d]",
    "%Y-%m-%d %H:%M:%S",
)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(simple_formatter)
file_handler = logging.handlers.TimedRotatingFileHandler(
    "stimulus_log.txt",
    when="midnight",
    backupCount=14,
    encoding=None,
    delay=False,
    utc=False,
    atTime=None,
)
file_handler.setFormatter(verbose_formatter)
# _h.addFilter(_ContextFilter_ChildName())
_logger.addHandler(console_handler)
_logger.addHandler(file_handler)
