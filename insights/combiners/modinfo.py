"""
Combiners for the parsers which parse the output of ``modinfo <module_name>``
=============================================================================

ModInfo
-------
The ModInfo combiner gathers all the ModInfoEach parsers into a dictionary
indexed by the module name.

ModulesInfo
-----------
The ModulesInfo combines the collected modules info.
It combines the result of ``KernelModulesInfo``, ``ModInfoI40e``,
``ModInfoIgb``, ``ModInfoIxgbe``, ``ModInfoVeth``, ``ModInfoVmxnet3``
if they exists.
"""

from insights.core.plugins import combiner
from insights.parsers import SkipException
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
        SkipException: When content is empty.

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
        for item in filter(None, []):
            name = item.module_name
            self[name] = item
            self.retpoline_y.add(name) if item.get('retpoline') == 'Y' else None
            self.retpoline_n.add(name) if item.get('retpoline') == 'N' else None
        if not self:
            raise SkipException
