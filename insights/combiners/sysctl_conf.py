"""
Sysctl configuration files
==========================
"""
import re

from insights.core.plugins import combiner
from insights.parsers.sysctl import SysctlConf, SysctlDConfEtc, SysctlDConfUsr


@combiner([SysctlConf, SysctlDConfUsr, SysctlDConfEtc])
class SysctlConfs(dict):
    """
    Combiner for accessing all the sysctl configuration files in one
    structure.

    Sample input::

        # sysctl.conf sample
        #
          kernel.domainname = example.com

        ; this one has a space which will be written to the sysctl!
          kernel.modprobe = /sbin/mod probe

    Attributes:
        search(dict): Returns a dict of any kv pairs where the
        contains the search word.

    Examples:
        >>> type(sysctl_conf)
        <class 'insights.combiners.sysctl_conf.SysctlConfs'>
        >>> sysctl_conf['kernel.domainname']
        'example.com'
        >>> sysctl_conf['kernel.modprobe']
        '/sbin/mod probe'
        >>> sysctl_conf['kernel.sysrq']
        '1'
        >>> "vm.dirty_ratio" in sysctl_conf
        True
        >>> sysctl_conf.search("domainname")
        {'kernel.domainname': 'example.com'}
    """
    def __init__(self, sysctl_conf, sysctl_d_confs_usr, sysctl_d_confs_etc):
        super(SysctlConfs, self).__init__()
        if sysctl_d_confs_usr:
            # Sort based on the filename to make sure
            # entries are overridden in the correct order.
            sysctl_d_confs_usr = sorted(sysctl_d_confs_usr, key=lambda x: x.file_name)

            for conf in sysctl_d_confs_usr:
                self.update(conf)

        if sysctl_d_confs_etc:
            # Sort based on the filename to make sure
            # entries are overridden in the correct order.
            sysctl_d_confs_etc = sorted(sysctl_d_confs_etc, key=lambda x: x.file_name)

            for conf in sysctl_d_confs_etc:
                self.update(conf)

        if sysctl_conf:
            self.update(sysctl_conf)

    def search(self, s_word):
        found = dict()
        for key, val in self.items():
            if re.search(s_word, key):
                found[key] = val

        return found
