import pkgutil
import inspect
import importlib
from message_handlers.base import BaseMessageHandler, state_handler


def get_all_message_handlers() -> list[BaseMessageHandler]:
    package_name = "message_handlers"
    subclasses = []

    # Итерируем все модули внутри пакета
    package = importlib.import_module(package_name)
    for _, module_name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        if is_pkg:
            continue
        module = importlib.import_module(module_name)
        subclasses += [
            obj
            for _, obj in inspect.getmembers(module, inspect.isclass)
            if issubclass(obj, BaseMessageHandler) and obj is not BaseMessageHandler
        ]

    return subclasses
