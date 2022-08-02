from typing import Dict, Type
import stimulus.device
import stimulus.automation
from types import SimpleNamespace

DeviceCls = Type[stimulus.device.device]

_registered_device_types: Dict[str, DeviceCls] = {}
_device_dict: Dict[str, stimulus.device.device] = dict()


def register_device_type_class(name: str, device_class: DeviceCls) -> None:
    _registered_device_types[name] = device_class


def device_type_exist(type: str) -> bool:
    return type in _registered_device_types


def get_device_class(type: str) -> DeviceCls:
    return _registered_device_types[type]


def add_device(name: str, device: stimulus.device.device) -> None:
    _device_dict[name] = device


def start_devices() -> None:
    user_devices: Dict[str, stimulus.device.device.user_device] = dict()
    for name, device in _device_dict.items():
        user_devices[name] = device.get_user_class()()
    stimulus.automation.S = SimpleNamespace(**user_devices)
    for device in _device_dict.values():
        device.start()
