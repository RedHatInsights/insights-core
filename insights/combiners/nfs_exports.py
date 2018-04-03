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
    >>> '/home/redhat' in all_nfs.exports  # All exports stored by path
    True
    >>> sorted(all_nfs.exports['/home/redhat'].keys())  # Each path is a dictionary of host specs and flags.
    ['@rhtttttttttttt', 'ins1.redhat.com', 'ins2.redhat.com', 'ins3.redhat.com']
    >>> all_nfs.exports['/home/redhat']['ins3.redhat.com']  # Each host contains a list of flags.
    ['rw', 'sync', 'no_root_squash']
    >>> '/home/redhat' in all_nfs.ignored_exports  # Ignored exports are remembered within one file
    True
    >>> all_nfs.ignored_exports['/home/redhat'].keys()  # Each ignored export is then stored by source file...
    ['/etc/exports']
    >>> all_nfs.ignored_exports['/home/redhat']['/etc/exports'].keys()  # ... and then by host spec...
    ['ins2.redhat.com']
    >>> all_nfs.ignored_exports['/home/redhat']['/etc/exports']['ins2.redhat.com']  # ... holding the values that were duplicated
    ['rw', 'sync', 'no_root_squash']
    >>> '/home/insights/shared/rw'  in all_nfs.ignored_exports  # Ignored exports are remembered across files
    True

"""

from insights.core.plugins import combiner
from insights.parsers.nfs_exports import NFSExports, NFSExportsD


@combiner(NFSExports, NFSExportsD)
class AllNFSExports(object):
    """
    Combiner for accessing all the NFS export configuration files.

    Exports are allowed to be listed multiple times, with all duplicate
    host after the first causing `exportfs` to emit a warning and ignore
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
    def __init__(self, nfsexports, nfsexportsd):
        self.files = []
        self.exports = {}
        self.ignored_exports = {}
        self.raw_lines = {}

        sources = [nfsexports]
        # Make sure exports are stored in the order they're parsed -
        # alphabetically by file name
        sources.extend(sorted(nfsexportsd, key=lambda f: f.file_path))

        def add_paths_to_dict(src_path, src_dict, dest_dict):
            # Because ignored_exports and raw_lines are stored by path, we
            # keep that and add the paths in them piecewise, stored by the
            # path of this source file.
            for path, value in src_dict.iteritems():
                if path not in dest_dict:
                    dest_dict[path] = {src_path: value}
                else:
                    dest_dict[path][src_path] = value

        for source in sources:
            self.files.append(source.file_path)
            # Add all raw lines from the source to raw lines.
            add_paths_to_dict(source.file_path, source.raw_lines, self.raw_lines)
            # Likewise all the ignored exports from this file.
            add_paths_to_dict(source.file_path, source.ignored_exports, self.ignored_exports)
            # For exports though we have to preserve existing host definitions
            # and ignore repeated host specs.
            for path, hosts in source.data.iteritems():
                if path in self.exports:
                    # Check whether the host specification has been listed
                    # more than once across different files:
                    for host, flags in hosts.iteritems():
                        if host in self.exports[path]:
                            # Add this to the ignored_exports list.  But
                            # because we know that this path-host tuple isn't
                            # duplicated in this file (it's already in
                            # ignored_exports if it does), then we can assume
                            # that the file isn't in the common ignored_exports
                            # already.
                            if path in self.ignored_exports:
                                self.ignored_exports[path][host] = flags
                            else:
                                self.ignored_exports[path] = {host: flags}
                        else:
                            # A new host spec - add as is.
                            self.exports[path][host] = flags
                else:
                    # No exports for this path so far, add them all
                    self.exports[path] = hosts

        super(AllNFSExports, self).__init__()
