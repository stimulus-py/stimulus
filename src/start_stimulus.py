import builtins
import os
import sys
from typing import List, MutableMapping, Set
from stimulus.core.log import logger
import importlib
import mergedeep
import yaml
import stimulus.core.device
import stimulus.core.automation
import stimulus.device
import signal


def load_settings() -> MutableMapping:
    user_config = yaml.safe_load(open("user/config/stimulus.yml"))
    default_config = yaml.safe_load(
        open(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "stimulus/defaultconfig.yml",
            )
        )
    )
    mergedeep.merge(user_config, default_config)
    return user_config


def add_stimulus_user_module(settings: MutableMapping) -> None:
    import stimulus.user

    # import user's user directory as module
    if not os.path.isabs(settings["user_path"]):
        settings["user_path"] = os.path.realpath(
            os.path.join(os.path.dirname(__file__), settings["user_path"])
        )
    logger.info(f"user_path set to {settings['user_path']}")
    (user_parent_path, mod_name) = os.path.split(settings["user_path"])
    if not mod_name:
        logger.critical("user_path is invalid")
        raise ValueError("user_path is invalid")
    logger.info(f"User module path: {user_parent_path} and module name: {mod_name}")
    sys.path.insert(0, user_parent_path)
    user_mod = builtins.__import__(mod_name)
    sys.path.remove(user_parent_path)
    stimulus.user = user_mod
    sys.modules["stimulus.user"] = user_mod


def create_devices(settings: MutableMapping) -> bool:
    for name, device_settings in settings["devices"].items():
        if not name.isidentifier():
            logger.error(f"Device name {name} is invalid, skipping creation of device")
            continue
        if "type" not in device_settings:
            logger.error(f"No device type in {name}. Check your stimulus.yml file")
            exit()
        device_type: str = device_settings["type"]
        from_modules: List[str]
        if "from" not in device_settings:
            # if from is not specified then first try stimulus.user.devices.{device_type} then stimulus.default_devices.{device_type}
            from_modules = [
                f"stimulus.user.devices.{device_type}",
                f"stimulus.default_devices.{device_type}",
            ]
        else:
            from_modules = [device_settings["from"]]
        for module_string in from_modules:
            # Try to import module
            try:

                module = importlib.import_module(module_string)

                break
            except ImportError:
                logger.debug(f"Did not find module {module_string}")
                continue
        else:
            logger.critical(
                f"Could not find a module for {device_type}, tried {from_modules}.  Check your stimulus.yml file and from definition for device: {name}"
            )
            return False
        try:
            device_cls = getattr(module, device_type)
        except AttributeError:
            logger.critical(
                f"Could not find device type: {device_type} in {module_string}.  If this is the wrong place to find {device_type} add a from definition in your stimulus.yml file."
            )
            return False
        if not issubclass(device_cls, stimulus.device.device):
            logger.critical(
                f"Could not load device {name} because {module_string}.{device_type} is not a subtype of stimuls.device.device"
            )
            return False
        device = device_cls(device_settings)
        stimulus.core.device.add_device(name, device)
    stimulus.core.device.start_devices()
    return True


def load_automations(settings: MutableMapping) -> None:
    builtins.__import__("stimulus.user.automations")

    files: Set[str] = set()
    automation_path = os.path.join(settings["user_path"], "automations")
    logger.info(f"Loading automation path: {automation_path}")
    for (_, _, filenames) in os.walk(automation_path):
        files.update(filenames)
        break

    for file in files:
        # skip if not a .py file or begins with _
        if file[0] == "_" or file[-3:].lower() != ".py":
            continue
        if not file[:-3].isidentifier():
            logger.warn(
                "Automation file: {file} has a name that can't be imported, skipping"
            )
            continue
        logger.info(f"Loading {file}")
        builtins.__import__(f"stimulus.user.automations.{file[:-3]}")


if __name__ == "__main__":
    logger.info("Loading settings")
    settings = load_settings()

    logger.info("Adding stimulus.user module")
    add_stimulus_user_module(settings)

    logger.info("Creating devices")
    if not create_devices(settings):
        logger.critical("Failed to create all devices")
        sys.exit(-1)

    # Load Automations
    logger.info("Loading automations")
    load_automations(settings)

    logger.info("Finished loading automations")

    # Pause until closed
    signal.pause()
