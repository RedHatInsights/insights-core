"""
DnfModuleInfoALL
================

This combiner combines all the :class:`insights.parsers.dnf_module.DnfModuleInfo`
"""
from insights import combiner
from insights.parsers.dnf_module import DnfModuleInfo


@combiner(DnfModuleInfo)
class DnfModuleInfoAll(dict):
    """
    Combine to combine all the parsing result of
    :class:`insights.parsers.dnf_module.DnfModuleInfo`

    The modules information is wrapped in this object like a dictionary, with
    the module name as the key and the list of the
    :class:`insights.parsers.dnf_module.DnfModuleDetail` as the value.

    Examples:
        >>> type(all_mods)
        <class 'insights.combiners.dnf_module_info.DnfModuleInfoAll'>
        >>> all_mods.modules
        ['389-ds', 'ant', 'httpd']
        >>> "389-ds" in all_mods
        True
        >>> len(all_mods.get("389-ds"))
        2
        >>> all_mods["389-ds"][0].profiles
        []
        >>> all_mods["389-ds"][0].default_profiles
        ''
        >>> "ant" in all_mods
        True
        >>> len(all_mods.get("ant"))
        1
        >>> type(all_mods.get("ant")[0])
        <class 'insights.parsers.dnf_module.DnfModuleDetail'>
        >>> all_mods["ant"][0].version
        '820181213135032'
        >>> len(all_mods.get("httpd", []))
        2
        >>> all_mods["httpd"][0].profiles
        ['common [d] [i]', 'devel', 'minimal']
        >>> all_mods["httpd"][0].default_profiles
        'common'
    """
    def __init__(self, mod_info_list):
        super(DnfModuleInfoAll, self).__init__()
        for mod_infos in mod_info_list:
            for mod in mod_infos:
                if mod.name not in self:
                    self[mod.name] = []
                self[mod.name].append(mod)

    @property
    def modules(self):
        """Returns a list of the name of module"""
        return sorted(self.keys())
