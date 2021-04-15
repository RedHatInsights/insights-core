"""
HDBVersion - Commands
=====================

Shared parser for parsing output of the ``sudo -iu <SID>adm HDB version``
commands.

"""
from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.sap_hdb_version)
class HDBVersion(CommandParser, dict):
    """
    Class for parsing the output of `HDB version` command.

    Typical output of the command is::

        # sudo -iu sr1adm HDB version
        HDB version info:
          version:             2.00.030.00.1522210459
          branch:              hanaws
          machine config:      linuxx86_64
          git hash:            bb2ff6b25b8eab5ab382c170a43dc95ae6ce298f
          git merge time:      2018-03-28 06:14:19
          weekstone:           2018.13.0
          cloud edition:       0000.00.00
          compile date:        2018-03-28 06:19:13
          compile host:        ld2221
          compile type:        rel

    Attributes:
        version (str): the raw HDB version
        major (str): the major version
        minor (str): the minor version
        revision (str): the SAP HANA SPS revision number
        patchlevel (str): the patchlevel number of this revision
        sid (str): the SID of this SAP HANA

    Examples:
        >>> type(hdb_ver)
        <class 'insights.parsers.sap_hdb_version.HDBVersion'>
        >>> hdb_ver.sid
        'sr1'
        >>> hdb_ver.version
        '2.00.030.00.1522210459'
        >>> hdb_ver.major
        '2'
        >>> hdb_ver.minor
        '00'
        >>> hdb_ver.revision
        '030'
        >>> hdb_ver.patchlevel
        '00'
        >>> hdb_ver['machine config']
        'linuxx86_64'
    """

    def parse_content(self, content):
        _ignore_bad_lines = [
            'HDB: Command not found',
            'standard error',
            'does not exist',
        ]
        if len(content) <= 1:
            raise SkipException("Incorrect content.")
        data = {}
        self.sid = self.version = self.revision = None
        self.major = self.minor = self.patchlevel = None
        # get the "sid" from the file_name: "sudo_-iu_<sid>adm_HDB_version"
        if self.file_name and 'adm' in self.file_name:
            self.sid = [i for i in self.file_name.split('_') if i.endswith('adm')][0][:-3]
        for line in content:
            # Skip unexpected lines
            if ':' not in line or any(i in line for i in _ignore_bad_lines):
                continue
            key, val = [i.strip() for i in line.split(':', 1)]
            data[key] = val
            if key == 'version':
                self.version = val
                val_splits = val.split('.')
                if len(val_splits) != 5:
                    raise SkipException("Incorrect HDB version: {0}.".format(val))
                self.major = val_splits[0]
                self.minor = val_splits[1]
                self.revision = val_splits[2]
                self.patchlevel = val_splits[3]
        if not self.version:
            raise SkipException("Incorrect content.")

        self.update(data)

    @property
    def data(self):
        return self
