import inspect
import threading
from stimulus.core.logging import logger

threadLocal = threading.local()
automation_dict = dict()

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

class automation:
    def __init__(self, name):
        self.name = name
        self.actions = set()
    
    def add_action(self,action):
        self.actions.add(action)
    
    def remove_action(self,action):
        self.actions.remove(action)
    
    def has_actions(self):
        if self.actions:
            return True
        else:
            return False