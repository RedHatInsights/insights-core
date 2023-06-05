"""
Combiners - command ``modinfo <module_name>``
=============================================

ModulesInfo
-----------
The ModulesInfo combines the collected modules info from the result of
``KernelModulesInfo``.
"""
from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.modinfo import KernelModulesInfo


@combiner([KernelModulesInfo])
class ModulesInfo(dict):
    """
    Combiner to combine the result of KernelModulesInfo which supports filter
    and the parsers which only support one single module. It refers
    ``KernelModulesInfo`` first.

    Examples:
        >>> type(modules_obj)
        <class 'insights.combiners.modinfo.ModulesInfo'>
        >>> 'i40e' in modules_obj
        True
        >>> 'bnx2x' in modules_obj.retpoline_y
        False

    Raises:
        SkipComponent: When content is empty.

    Attributes:
        retpoline_y (set): A set of names of the modules with the attribute "retpoline: Y".
        retpoline_n (set): A set of names of the modules with the attribute "retpoline: N".
    """
    def __init__(self, filtered_modules_info):
        self.retpoline_y = set()
        self.retpoline_n = set()
        if filtered_modules_info:
            self.update(filtered_modules_info)
            self.retpoline_n = filtered_modules_info.retpoline_n
            self.retpoline_y = filtered_modules_info.retpoline_y
        if not self:
            raise SkipComponent
