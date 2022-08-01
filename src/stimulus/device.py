import stimulus.core.device
import stimulus.core.action
from types import SimpleNamespace
import functools


def _logger(level, msg):
    # name = stimulus.core.automation.get_current_automation().name
    stimulus.core.logging.device_log("device", level, msg)


logger = SimpleNamespace()
logger.debug = functools.partial(_logger, "debug")
logger.info = functools.partial(_logger, "info")
logger.warning = functools.partial(_logger, "warning")
logger.error = functools.partial(_logger, "error")
logger.critical = functools.partial(_logger, "critical")


class device:
    def __init__(self):
        pass

    def get_user_class(this):
        class_attrs = dict()
        for obj_attr_name, obj_attr in vars(this).items():
            if issubclass(type(obj_attr), stimulus.device.has_user_interface):
                class_attrs.update(obj_attr.get_user_class_attrs(obj_attr_name, this))
        return type("user_device", (object,), class_attrs)

    def start(self):
        pass


class has_user_interface:
    def __init__(self):
        pass

    def set_device(self, device):
        self._device = device


class stimulator(has_user_interface):
    def __init__(self, on_register, on_cancel):
        self._on_register = on_register
        self._on_cancel = on_cancel
        self._user_stimulator = None

    class user_stimulator:
        def __init__(self, stimulator):
            self._stimulator = stimulator

        def __call__(self, function, *args, **Kwargs):
            return self._stimulator._register_action(function, *args, **Kwargs)

    def _register_action(self, function, *args, **kwargs):
        registered_action = stimulus.core.action.register(
            function, self._on_cancel, self._device
        )
        self._on_register(registered_action, *args, **kwargs)
        return registered_action.get_user_action()

    def get_user_class_attrs(self, name, device):
        user_interface = {
            f"{name}": self.get_user_stimulator(device),
        }
        return user_interface

    def get_user_stimulator(self, device):
        if self._user_stimulator is None:
            has_user_interface.set_device(self, device)
            self._user_stimulator = stimulator.user_stimulator(self)
        return self._user_stimulator


class simple_stimulator(stimulator):
    def __init__(self):
        super().__init__(self._register, self._cancel)
        self.actions = []

    def call(self, payload):
        for action in self.actions:
            action.call(payload)

    def _register(self, action):
        self.actions.append(action)

    def _cancel(self, action):
        self.actions.remove(action)


class sprop(has_user_interface):
    def __init__(self, init=None, on_set=None):
        self._value = init
        self._on_set = on_set
        self._on_update = simple_stimulator()
        self._on_change = simple_stimulator()
        # self._on_update_actions = list()
        # self._on_change_actions = list()

    def update(self, value):
        """Updates the stored value and calls notifiers"""
        old_value = self._value
        payload = SimpleNamespace()
        payload.old_value = old_value
        payload.new_value = value
        self._value = value
        self._on_update.call(payload)
        # for action in self._on_update_actions:
        #     action()
        if old_value is not self._value:  # Should we compare via is not or !=?

            self._on_change.call(payload)
            # for action in self._on_change_actions:
            #     action()

    def set(self, value):
        """Calls a method to command a set value (eg on the hardware) and then calls to update the stored value"""
        if self._on_set:
            self._on_set(value)
        self.update(value)

    def get(self):
        return self._value

    def _getter(self, ui_obj):
        return self.get()

    def _setter(self, ui_obj, value):
        self.set(value)

    def get_user_class_attrs(self, name, device):
        has_user_interface.set_device(self, device)
        user_interface = {
            f"{name}": property(fget=self._getter, fset=self._setter),
            # f'on_{name}_update' : stimulator(self.register_on_update),
            # f'on_{name}_change' : stimulator(self.register_on_change),
            f"on_{name}_update": self._on_update.get_user_stimulator(device),
            f"on_{name}_change": self._on_change.get_user_stimulator(device),
        }
        return user_interface


class user_function(has_user_interface):
    def __init__(self, function):
        self._function = function

    def get_user_class_attrs(self, name, device):
        has_user_interface.set_device(self, device)
        user_interface = {
            f"{name}": self._function,
        }
        return user_interface


def device_type(name):
    # Decorator for marking a class as a device
    def decorator(device_class):
        stimulus.core.device.register_device_type_class(name, device_class)
        return device_class

    return decorator
