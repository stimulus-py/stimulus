import builtins
import os
import sys
from typing import MutableMapping, Set
from stimulus.core.log import logger
import importlib
import mergedeep
import yaml
import stimulus.core.device
import stimulus.core.automation
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


def import_user_plugins(settings: MutableMapping) -> None:
    builtins.__import__("stimulus.user.plugins")

    files: Set[str] = set()
    plugin_path: str = os.path.join(settings["user_path"], "plugins")
    logger.info(f"Loading plugin path: {plugin_path}")
    # This is not how we should get files to load, but works until we refactor loading plugins
    for (_, _, filenames) in os.walk(plugin_path):
        files.update(filenames)
        break
    for file in files:
        # skip if not a .py file or begins with _
        if file[0] == "_" or file[-3:].lower() != ".py":
            continue
        logger.info(f"Loading {file}")
        importlib.import_module(f"stimulus.user.plugins.{file[:-3]}")


def create_devices(settings: MutableMapping) -> None:
    for name, device_settings in settings["devices"].items():
        if not name.isidentifier():
            logger.error(f"Device name {name} is invalid, skipping creation of device")
            continue
        if "type" not in device_settings:
            logger.error(f"No device type in {name}. Check your stimulus.yml file")
            exit()
        device_type: str = device_settings["type"]
        if not stimulus.core.device.device_type_exist(device_type):
            try:
                importlib.import_module(f"stimulus.default_plugins.{device_type}")
            except ImportError:
                logger.error(f"Device type {device_type} not defined for device {name}")
                continue
        device_cls = stimulus.core.device.get_device_class(device_type)
        device = device_cls(device_settings)
        stimulus.core.device.add_device(name, device)
    stimulus.core.device.start_devices()


# TODO need to finish, just copied loading plugins here.
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

    logger.info("Loading user plugins")
    import_user_plugins(settings)
    logger.info("Finished loading user plugins")

    logger.info("Creating devices")
    create_devices(settings)
    logger.info("Finished creating devices")

    # Load Automations
    logger.info("Loading automations")
    load_automations(settings)

    logger.info("Finished loading automations")

    # Pause until closed
    signal.pause()
