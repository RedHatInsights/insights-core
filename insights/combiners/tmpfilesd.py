"""
Tmpfilesd configuration
=======================

The tmpfilesd files are normally available to rules as a list of TmpFilesd
objects. This combiner turns those into one set of data, and provides a
``find_file()`` method to search for that filename among all the files.
"""

from insights.core.plugins import combiner
from insights.parsers.tmpfilesd import TmpFilesD


@combiner(TmpFilesD)
class AllTmpFiles(object):
    """
    Combiner for accessing all the tmpfilesd configuration files. Configuration
    files can be found in three directories: ``/usr/lib/tmpfiles.d``,
    ``/run/tmpfiles.d``, and ``/etc/tmpfiles.d``. Each directory overrides the
    settings in the previous directory. This combiner checks for and accounts
    for this behavior.

    Attributes:
        files(set): the set of files found in all data files.
        active_rules(dict): a dictionary of rules using the config file as the key
        file_paths(list): a list of the file paths for the configurations.
    """
    def __init__(self, tmpfiles):
        active_rules = {}
        files = set([])
        file_paths = []
        # Files must be sorted so that /etc/tmpfiles.d overrides /run/tmpfiles.d
        # which overides /usr/lib/tmpfiles.d.
        for tmpfile in sorted(tmpfiles, key=lambda f: f.file_path):
            file_paths.append(tmpfile.file_path)
            if not active_rules.get(tmpfile.file_path):
                active_rules[tmpfile.file_path] = []
            for new_rule in tmpfile.rules:
                _file = (new_rule['path'])
                if _file not in files:
                    files.add(_file)
                    active_rules[tmpfile.file_path].append(new_rule)

        self.active_rules = active_rules
        self.files = files
        self.file_paths = file_paths
        super(AllTmpFiles, self).__init__()

    def find_file(self, path):
        """
        Find all the rules matching a given file. Uses the rules dictionary to search
        so duplicate files are alreayd removed.

        Examples:
            >>> data = shared[AllTmpFiles]
            >>> results = data.find_file('/tmp/sap.conf')
            >>> len(results)
            1
            >>> results
            {'/etc/tmpfiles.d/sap.conf': {'path': '/tmp/sap.conf', 'mode': '644', 'type': 'x', 'age': None,
             'gid': None, 'uid': None, 'argument': None}}

        Parameters:
            path(str): path to be searched for among the rules.

        Returns:
            (dict): a dictionary of rules where the path is found using the config
            file path as the key.
        """
        match = {}
        for r, d in self.active_rules.items():
            for i in self.active_rules[r]:
                if i['path'] == path:
                    match[r] = i

        return match
