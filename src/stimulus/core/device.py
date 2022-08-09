from typing import Dict, Type
import stimulus.device
import stimulus.automation

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
    # add devices to stimulus.automations.S before starting any device
    for name, device in _device_dict.items():
        setattr(stimulus.automation.S, name, device.get_user_class()())
    for device in _device_dict.values():
        device.start()
