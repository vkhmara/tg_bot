import pkgutil
import importlib


package_name = "databases.models"
subclasses = []

package = importlib.import_module(package_name)
for _, module_name, is_pkg in pkgutil.walk_packages(
    package.__path__, package.__name__ + "."
):
    if is_pkg:
        continue
    importlib.import_module(module_name)
