import sys
from insights.core import load_package


def get_archives(module_name, system_filter):
    load_package(module_name)
    m = sys.modules[module_name]
    for sub_m in m.__all__:
        demo_submodule = sys.modules[".".join([module_name, sub_m])]
        if hasattr(demo_submodule, "demo"):
            for a in demo_submodule.demo:
                if system_filter in a.name:
                    yield a
