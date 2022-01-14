"""
crio configuration
==================
The crio files are normally available to rules as a list of CrioConf objects.
"""

from insights.contrib.ConfigParser import NoOptionError, NoSectionError
from insights.core.plugins import combiner
from insights.parsers.crio_conf import CrioConf


@combiner(CrioConf)
class AllCrioConf(object):
    """
    Combiner for accessing all the crio configuration files. There may be multi
    files for crio configuration, and the main config file is crio.conf. In the
    situation that the same section is both in crio.conf and other configuration
    files, the item in crio.conf has the highest precedence. This combiner will
    parse all the CrioConf objects and return a dictionary containing all valid data.

    Sample files::

        /etc/crio/crio.conf:

            [crio]
            storage_driver = "overlay"
            storage_option = [
                    "overlay.override_kernel_check=1",
            ]

            [crio.runtime]
            selinux = true

            [crio.network]
            plugin_dirs = [
                    "/usr/libexec/cni",
            ]
            [crio.metrics]

        /etc/crio/crio.conf.d/00-conmon.conf

            [crio]
            internal_wipe = true
            storage_driver = "overlay"
            storage_option = [
                "overlay.override_kernel_check=1",
            ]

            [crio.api]
            stream_address = ""
            stream_port = "10010"

            [crio.runtime]
            selinux = true
            conmon = ""
            conmon_cgroup = "pod"
            default_env = [
                "NSS_SDB_USE_CACHE=no",
            ]
            log_level = "info"
            cgroup_manager = "systemd"

    Examples:
        >>> all_crio_conf.sections()
        ['crio', 'crio.runtime', 'crio.api', 'crio.network', 'crio.metrics']
        >>> all_crio_conf.options('crio.api')
        ['stream_address', 'stream_port']
        >>> all_crio_conf.files
        ['/etc/crio/crio.conf', '/etc/crio/crio.conf.d/00-conmon.conf']

    Attributes:
        files (list): The list of configuration file names.
    """
    def __init__(self, crio_confs):
        main_data = None
        self.data = {}
        self.files = []

        def dict_merge(dest, src):
            if not src:
                return

            for section in src.sections():
                if section not in dest:
                    dest[section] = {}

                for option in src.items(section):
                    dest[section][option] = src.get(section, option)

        for crio_conf in crio_confs:
            self.files.append(crio_conf.file_path)
            if crio_conf.file_name == "crio.conf":
                main_data = crio_conf
            else:
                dict_merge(self.data, crio_conf)

        dict_merge(self.data, main_data)
        super(AllCrioConf, self).__init__()

    def get(self, section, option):
        """
        Args:
            section (str): The section str to search for.
            option (str): The option str to search for.

        Returns:
            str: Returns the value of the option in the specified section.
        """
        if section not in self.data.keys():
            raise NoSectionError(section)

        header = self.data.get(section)
        if option not in header.keys():
            raise NoOptionError(section, option)

        return header.get(option)

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
