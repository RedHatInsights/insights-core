"""
krb5 configuration
==================
The krb5 files are normally available to rules as a list of
Krb5Configuration objects.
"""

from .. import LegacyItemAccess
from insights.core.plugins import combiner
from insights.parsers.krb5 import Krb5Configuration


@combiner(Krb5Configuration)
class AllKrb5Conf(LegacyItemAccess):
    """
    Combiner for accessing all the krb5 configuration files, the format is dict.
    There may be multi files for krb5 configuration, and the main config file is
    krb5.conf. In the situation that same section is both in krb5.conf and other
    configuration files, section in krb5.conf is the available setting. Data from
    parser krb5 is list of dict(s), this combiner will parse this list and return
    a dict which containing all valid data.

    Sample files::

        /etc/krb5.conf:

            includedir /etc/krb5.conf.d/
            include /etc/krb5test.conf
            module /etc/krb5test.conf:residual

            [logging]
                default = FILE:/var/log/krb5libs.log
                kdc = FILE:/var/log/krb5kdc.log

        /etc/krb5.d/krb5_more.conf:

            [logging]
                default = FILE:/var/log/krb5.log
                kdc = FILE:/var/log/krb5.log
                admin_server = FILE:/var/log/kadmind.log

            [realms]
                dns_lookup_realm = false
                default_ccache_name = KEYRING:persistent:%{uid}

    Examples:
        >>> all_krb5 = shared[AllKrb5Conf]
        >>> all_krb5.include
        ['/etc/krb5test.conf']
        >>> all_krb5.sections()
        ['logging', 'realms']
        >>> all_krb5.options('logging')
        ['default', 'kdc', 'admin_server']
        >>> all_krb5['logging']['kdc']
        'FILE:/var/log/krb5kdc.log'
        >>> all_krb5.has_option('logging', 'admin_server')
        True
        >>> all_krb5['realms']['dns_lookup_realm']
        'false'

    Attributes:
        includedir (list): The directory list that `krb5.conf` includes via
            `includedir` directive
        include (list): The configuration file list that `krb5.conf` includes
            via `include` directive
        module (list): The module list that `krb5.conf` specifed via 'module'
            directive

    """
    def __init__(self, krb5configs):
        self.data = {}
        main_data = {}
        self.includedir = []
        self.include = []
        self.module = []

        for krb5_parser in krb5configs:
            if krb5_parser.file_path == "/etc/krb5.conf":
                main_data = krb5_parser.data
                self.includedir = krb5_parser.includedir
                self.include = krb5_parser.include
                self.module = krb5_parser.module
            else:
                self.data.update(krb5_parser.data)
        # Same options in same section from other configuration files will be covered by the option
        # from main configuration, but different options in same section will be kept.
        for key, value in main_data.items():
            if key in self.data.keys():
                self.data[key].update(value)
            else:
                self.data[key] = value

        super(AllKrb5Conf, self).__init__()

    def sections(self):
        """
        Return a list of section names.
        """
        return self.data.keys()

    def has_section(self, section):
        """
        Indicate whether the named section is present in the configuration.
        Return True if the given section is present, and False if not present.
        """
        return section in self.data

    def options(self, section):
        """
        Return a list of option names for the given section name.
        """
        return self.data[section].keys() if self.has_section(section) else []

    def has_option(self, section, option):
        """
        Check for the existence of a given option in a given section.
        Return True if the given option is present, and False if not present.
        """
        if section not in self.data:
            return False
        return option in self.data[section]
