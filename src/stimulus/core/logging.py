import logging
import sys

_logger = logging.getLogger('Stimulus')  #Actual logger
logger = logging.LoggerAdapter(_logger, {'type':'-'})  #logger with stimulus type set
_device_logger = _logger.getChild('device')
_automation_logger = _logger.getChild('automation')

_logger.setLevel(logging.INFO)

def user_log(name,level,msg):
    logger = _automation_logger.getChild(name)
    logger_level = getattr(logger,level)
    logger_level(msg, extra={'type':'@'})
    
def device_log(name,level,msg):
    logger = _device_logger.getChild(name)
    logger_level = getattr(logger,level)
    logger_level(msg, extra={'type':'#'})


class _ContextFilter_ChildName:
    def filter(self, record):
        split_name = record.name.split('.')
        record.name = split_name[-1]
        return True

_h = logging.StreamHandler(sys.stdout)
# _h.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(type)s %(name)s %(filename)s:%(lineno)d : %(message)s',"%m-%d %H:%M:%S"))
_h.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(type)s %(name)s : %(message)s',"%m-%d %H:%M:%S"))
_h.addFilter(_ContextFilter_ChildName())
_logger.addHandler(_h)

logger.info('logger set up')

