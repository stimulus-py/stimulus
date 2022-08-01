import stimulus.device
import stimulus.automation
from types import SimpleNamespace

_registered_device_types = {}
_device_dict = dict()


def register_device_type_class(name, device_class):
    _registered_device_types[name] = device_class


def device_type_exist(type):
    return type in _registered_device_types


def get_device_class(type):
    return _registered_device_types[type]


def add_device(name, device):
    _device_dict[name] = device


def start_devices():
    user_devices = dict()
    for name, device in _device_dict.items():
        user_devices[name] = device.get_user_class()()
    stimulus.automation.S = SimpleNamespace(**user_devices)
    for device in _device_dict.values():
        device.start()
