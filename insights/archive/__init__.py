import sys
from insights.core.dr import load_components


def get_archives(module_name, system_filter):
    load_components(module_name)
    m = sys.modules[module_name]
    for sub_m in m.__all__:
        demo_submodule = sys.modules[".".join([module_name, sub_m])]
        if hasattr(demo_submodule, "demo"):
            for a in demo_submodule.demo:
                if system_filter in a.name:
                    yield a
