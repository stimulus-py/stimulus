from datetime import datetime
import traceback
from typing import Any, Callable, Optional
import stimulus.core.automation
import concurrent.futures
import stimulus.device
from stimulus.core.log import logger

_thread_pool_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=15, thread_name_prefix="automationPool"
)


class action:
    def __init__(self, callback_function: Callable, to_cancel: Callable):
        self._to_cancel: Callable = to_cancel
        self._callback_function: Optional[Callable] = callback_function
        self._count: int = 0
        self._last_called: Optional[datetime] = None
        self._user_action: Optional[user_action] = None
        self._automation: stimulus.core.automation.automation = (
            stimulus.core.automation.get_current_automation()
        )
        self._error_last_call: bool = False
        self._automation.add_action(self)

    def call(self, payload: Any = None, deleteWhenDone: bool = False) -> None:
        if self._callback_function is None:
            return

        def callback_thread():
            stimulus.core.automation.set_automation(self._automation)
            try:
                self._callback_function(self, payload)
                self._error_last_call = False
            except Exception:
                # stimulus._logging.get_child_logger(self._automation.name).error(traceback.format_exc())
                logger.error(traceback.format_exc())
                self._error_last_call = True
            self._count += 1
            self._last_called = datetime.now()
            if deleteWhenDone:
                # logger.warning("TODO: delete when done")
                pass

        _thread_pool_executor.submit(callback_thread)

    def cancel(self) -> None:
        if self._callback_function is None:
            return
        self._callback_function = None
        self._to_cancel(self)
        self._automation.remove_action(self)

    def get_user_action(self):
        if self._user_action is None:
            self._user_action = user_action(self)
        return self._user_action

    @property
    def count(self) -> int:
        return self._count

    @property
    def last_called(self) -> Optional[datetime]:
        return self._last_called

    @property
    def error_last_call(self) -> bool:
        return self._error_last_call


class user_action:
    def __init__(self, action: action):
        self._action = action

    def cancel(self) -> None:
        self._action.cancel()

    @property
    def count(self) -> int:
        return self._action.count

    @property
    def last_called(self) -> Optional[datetime]:
        return self._action.last_called

    @property
    def error_last_run(self) -> bool:
        return self._action.error_last_call


def register(
    callback_function: Callable, to_cancel: Callable, device: "stimulus.device.device"
) -> action:
    a = action(callback_function, to_cancel)
    return a
