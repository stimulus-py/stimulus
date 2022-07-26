import builtins
import functools
import inspect
import threading
from types import SimpleNamespace
from stimulus.core.logging import logger

threadLocal = threading.local()
automation_dict = dict()
# _original_import = builtins.__import__

# def set_automation_importer():
#     builtins.__import__ = functools.partial(_automation_import,_original_import)

# def set_as_device(device):
#     global threadLocal
#     threadLocal.automation = automation._is_device(device)
        
# def set_as_automation():
#     global threadLocal
#     threadLocal.automation = automation._is_automation()

def get_current_automation():
    global threadLocal
    if hasattr(threadLocal,'automation'):
        return threadLocal.automation
    # module must be getting loaded
    stack = inspect.stack()
    for frame_info in stack:
        if(frame_info.function == '<module>'):
            name = frame_info.frame.f_locals['__name__']
            break
    else:
        logger.critical("Could not locate automation")
        raise Exception("Could not locate automation") 
    logger.debug(f"module: {name}")
    if name in automation_dict:
        return automation_dict[name]
    # automation hasn't been created yet
    # mutex here? and check again?
    automation_dict[name] = automation(name)
    return automation_dict[name]
    
    

def set_automation(automation):
    threadLocal.automation = automation

# def _automation_import(original_import,name, *args, **kwargs):
#     global threadLocal
#     logger.debug(f'automation_import: {name} started')
#     prev_automation = threadLocal.automation
#     threadLocal.automation = automation(prev_automation)
#     threadLocal.automation.name = name
#     module = original_import(name, *args, **kwargs)
#     logger.debug(f'automation_import: {name} finished.')
#     if(threadLocal.automation.has_actions()):
#         logger.info(f'automation: {name} count: {len(threadLocal.automation.actions)}')
#     threadLocal.automation.file = 'test'
#     threadLocal.automation = prev_automation
#     return module
    

class automation:
    def __init__(self, name):
        self.name = name
        self.actions = set()
    
    def add_action(self,action):
        self.actions.add(action)
    
    def has_actions(self):
        if self.actions:
            return True
        else:
            return False