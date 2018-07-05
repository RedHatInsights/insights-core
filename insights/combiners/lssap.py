"""
Combined NFS exports
====================

The NFS exports files are normally available to rules from both a single
NFSExports object and zero or more NFSExportsD objects.  This combiner turns
those into one set of data.

Examples:
    >>> type(all_nfs)
    <class 'insights.combiners.nfs_exports.AllNFSExports'>
    >>> all_nfs.files  # List of files exporting NFS shares
    ['/etc/exports', '/etc/exports.d/mnt.exports']
    >>> '/home/example' in all_nfs.exports  # All exports stored by path
    True
    >>> sorted(all_nfs.exports['/home/example'].keys())  # Each path is a dictionary of host specs and flags.
    ['@group', 'ins1.example.com', 'ins2.example.com']
    >>> all_nfs.exports['/home/example']['ins2.example.com']  # Each host contains a list of flags.
    ['rw', 'sync', 'no_root_squash']
    >>> '/home/example' in all_nfs.ignored_exports  # Ignored exports are remembered within one file
    True
    >>> list(all_nfs.ignored_exports['/home/example'].keys())  # Each ignored export is then stored by source file...
    ['/etc/exports']
    >>> list(all_nfs.ignored_exports['/home/example']['/etc/exports'].keys())  # ... and then by host spec...
    ['ins2.example.com']
    >>> all_nfs.ignored_exports['/home/example']['/etc/exports']['ins2.example.com']  # ... holding the values that were duplicated
    ['rw', 'sync', 'no_root_squash']
    >>> '/home/insights/shared/rw'  in all_nfs.ignored_exports  # Ignored exports are remembered across files
    True

"""

from insights.core.plugins import combiner
from insights.combiners.hostname import hostname
from insights.parsers.lssap import Lssap

@combiner(hostname, Lssap)
class Lssap(object):
    """
    Combiner for accessing all the NFS export configuration files.

    Exports are allowed to be listed multiple times, with all duplicate
    host after the first causing ``exportfs`` to emit a warning and ignore
    the host.  So we combine the raw lines and ignored exports into structures
    listing the source file for each

    Attributes:
        files (list): the list of source files that contained NFS export
            definitions.

        exports (dict of dicts): the NFS exports stored by export path, with
            each path storing a dictionary of host flag lists.

        ignored_exports (dict): A dictionary of exported paths that have
            host definitions that conflicted with a previous definition,
            stored by export path and then path of the file that defined it.

        raw_lines (dict of dicts): A dictionary of raw lines that define each
            exported path, with the lines stored by defining file.

    """
    sap_type = {'D': 'netweaver',
                'HDB': 'hana',
                'ASCS': 'ascs'}
    def __init__(self, hostname, sap):
        hn = hostname.hostname
        # Rule only matters if the SAP instance returned by lssap refers to this
        # host
        instances = [i for i in lssap.instances if hn == i['SAPLOCALHOST']]
        sap_apps = []
        for i in instances:
            (sap_apps.append(v)
                for k, v in self.sap_type.items()
                if i.startswith(k))

        super(Lssap, self).__init__()

    def is_netweaver(self):
        """bool: SAP Netweaver is running on the system."""
        return 'D' in list(set(self.running_inst_types) & set(self.instance_dict.keys()))

    def is_hana(self):
        """bool: SAP Hana is running on the system."""
        return 'HDB' in list(set(self.running_inst_types) & set(self.instance_dict.keys()))

    def is_ascs(self):
        """bool: SAP System Central Services is running on the system."""
        return 'ASCS' in list(set(self.running_inst_types) & set(self.instance_dict.keys()))
