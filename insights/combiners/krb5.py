"""
krb5 configuration
==================
The krb5 files are normally available to rules as a list of
Krb5Configuration objects.
"""
from copy import deepcopy
from insights.core import LegacyItemAccess
from insights.core.plugins import combiner
from insights.parsers.krb5 import Krb5Configuration, _handle_krb5_bool


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
        >>> all_krb5.files
        ['krb5.conf', 'test.conf', 'test2.conf']

    Attributes:
        includedir (list): The directory list that `krb5.conf` includes via
            `includedir` directive
        include (list): The configuration file list that `krb5.conf` includes
            via `include` directive
        module (list): The module list that `krb5.conf` specifed via 'module'
            directive
        files (list): The list of configuration file names.
        dns_lookup_realm (bool): is Kerberos realm DNS lookup enabled?
        dns_lookup_kdc (bool): is Kerberos KDC DNS lookup enabled?
        default_realm (str/None): default realm for clients
        realms (set): realm names from [realms] block

    """
    def __init__(self, krb5configs):
        self.data = {}
        main_data = {}
        self.includedir = []
        self.include = []
        self.module = []
        self.files = []

        for krb5_parser in krb5configs:
            self.files.append(krb5_parser.file_name)
            if krb5_parser.file_path == "/etc/krb5.conf":
                main_data = krb5_parser.data
                self.includedir = krb5_parser.includedir
                self.include = krb5_parser.include
                self.module = krb5_parser.module
            else:
                dict_deep_merge(self.data, krb5_parser.data)
        # Same options in same section from other configuration files will be covered by the option
        # from main configuration, but different options in same section will be kept.
        for key, value in main_data.items():
            if key in self.data.keys():
                self.data[key].update(value)
            else:
                self.data[key] = value

        def _getbool(option, default=None):
            if not self.has_option("libdefaults", option):
                return default
            return self.getboolean("libdefaults", option)

        self.dns_lookup_realm = _getbool("dns_lookup_realm", True)
        self.dns_lookup_kdc = _getbool("dns_lookup_kdc", True)
        if self.has_option("libdefaults", "default_realm"):
            self.default_realm = self["libdefaults"]["default_realm"]
        else:
            self.default_realm = None

        self.realms = set()
        if self.has_section("realms"):
            r = self["realms"]
            for name, value in r.items():
                if (
                    # realm entries must be dicts
                    isinstance(value, dict) and
                    # realm names look like "UPPER-CASE.COM"
                    not any(c.islower() or c == "_" for c in name)
                ):
                    self.realms.add(name)

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

    def getboolean(self, section, option):
        """Parse option as bool

        Returns None is not a krb5.conf boolean string.
        """
        value = self.data[section][option]
        return _handle_krb5_bool(value)


def dict_deep_merge(tgt, src):
    """
    Utility function to merge the source dictionary `src` to the target
    dictionary recursively

    Note:
        The type of the values in the dictionary can only be `dict` or `list`

    Parameters:
        tgt (dict): The target dictionary
        src (dict): The source dictionary
    """
    for k, v in src.items():
        if k in tgt:
            if isinstance(tgt[k], dict) and isinstance(v, dict):
                dict_deep_merge(tgt[k], v)
            else:
                tgt[k].extend(deepcopy(v))
        else:
            tgt[k] = deepcopy(v)
