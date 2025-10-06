import pkgutil
import importlib


PACKAGE_NAME = "db.models"
subclasses = []

package = importlib.import_module(PACKAGE_NAME)
for _, module_name, is_pkg in pkgutil.walk_packages(
    package.__path__, package.__name__ + "."
):
    if is_pkg:
        continue
    importlib.import_module(module_name)
