import inspect
import threading
from typing import Dict
from stimulus.core.log import logger
import stimulus.core.action

threadLocal = threading.local()
automation_dict: Dict[str, "automation"] = dict()


class automation:
    def __init__(self, name):
        self.name = name
        self.actions = set()

    def add_action(self, action: "stimulus.core.action.action") -> None:
        self.actions.add(action)

    def remove_action(self, action: "stimulus.core.action.action") -> None:
        self.actions.remove(action)

    def has_actions(self) -> bool:
        if self.actions:
            return True
        else:
            return False


def get_current_automation() -> automation:
    global threadLocal
    if hasattr(threadLocal, "automation"):
        return threadLocal.automation
    # module must be getting loaded
    stack = inspect.stack()
    for frame_info in stack:
        if frame_info.function == "<module>":
            name = frame_info.frame.f_locals["__name__"]
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


def set_automation(automation: automation) -> None:
    threadLocal.automation = automation
