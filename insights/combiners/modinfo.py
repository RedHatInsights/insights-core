"""
Combiners for the parsers which parse the output of ``modinfo <module_name>``
=============================================================================

ModInfo
-------
The ModInfo combiner gathers all the ModInfoEach parsers into a dictionary
indexed by the module name.

ModulesInfo
-----------
The ModulesInfo combines the collected modules info from the result of
``KernelModulesInfo``.
"""
from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.modinfo import (KernelModulesInfo, ModInfoEach, ModInfoAll)
from insights.util import deprecated


@combiner([ModInfoAll, ModInfoEach])
class ModInfo(dict):
    """
    .. warning::
        This combiner is deprecated, please use
        :py:class:`insights.combiners.modinfo.ModulesInfo` instead.

    Combiner for accessing all the modinfo outputs.

    Examples:
        >>> type(modinfo_obj)
        <class 'insights.combiners.modinfo.ModInfo'>
        >>> type(modinfo_obj['i40e'])
        <class 'insights.parsers.modinfo.ModInfoEach'>
        >>> modinfo_obj['i40e'].module_name
        'i40e'
        >>> modinfo_obj['i40e'].module_name
        'i40e'
        >>> modinfo_obj['i40e']['retpoline']
        'Y'
        >>> modinfo_obj['i40e'].module_version
        '2.3.2-k'
        >>> modinfo_obj['i40e'].module_path
        '/lib/modules/3.10.0-993.el7.x86_64/kernel/drivers/net/ethernet/intel/i40e/i40e.ko.xz'
        >>> "i40e" in modinfo_obj.retpoline_y
        True
        >>> "bnx2x" in modinfo_obj.retpoline_y
        False
        >>> "bnx2x" in modinfo_obj.retpoline_n
        True

    Raises:
        SkipComponent: When content is empty.

    Attributes:
        retpoline_y (set): A set of names of the modules with the attribute "retpoline: Y".
        retpoline_n (set): A set of names of the modules with the attribute "retpoline: N".
    """
    def __init__(self, mi_all, mi_each):
        deprecated(
            ModInfo,
            "Please use the :class:`insights.parsers.modinfo.KernelModulesInfo` instead.",
            "3.1.25"
        )
        self.retpoline_y = set()
        self.retpoline_n = set()
        if mi_all:
            self.update(mi_all)
            self.retpoline_y = mi_all.retpoline_y
            self.retpoline_n = mi_all.retpoline_n
        else:
            for m in mi_each:
                name = m.module_name
                self[name] = m
                self.retpoline_y.add(name) if m.get('retpoline') == 'Y' else None
                self.retpoline_n.add(name) if m.get('retpoline') == 'N' else None

        if len(self) == 0:
            raise SkipComponent("No Parsed Contents")

    @property
    def data(self):
        """
        (dict): Dict with the module name as the key and the module details as the value.
        """
        return self


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
