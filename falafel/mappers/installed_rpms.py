import json
from collections import defaultdict
from distutils.version import LooseVersion as LV
from itertools import chain

from ..util import rsplit
from .. import Mapper, mapper, get_active_lines

KNOWN_ARCHITECTURES = [
    'x86_64',
    'i386',
    'i486',
    'i586',
    'i686',
    'src',
    'ia64',
    'ppc',
    'ppc64',
    's390',
    's390x',
    'amd64',
    '(none)',
    'noarch',
]

PACKAGES = 'PACKAGES'
VULNERABLE_PACKAGES = 'VULNERABLE_PACKAGES'
PACKAGE_NAMES = 'PACKAGE_NAMES'
INSTALLED_PACKAGE = 'INSTALLED_PACKAGE'


@mapper('installed-rpms')
class InstalledRpms(Mapper):
    """
    A mapper for working with data containing a list of installed RPM files on the system and
    related information.
    """
    def __init__(self, *args, **kwargs):
        self.errors = []
        self.unparsed = []
        self.packages = defaultdict(list)
        super(InstalledRpms, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Mapper context content

        Returns:
            dict: dictionary with parsed data
        """
        for line in get_active_lines(content, comment_char='COMMAND>'):
            if line.startswith('error:') or line.startswith('warning:'):
                self.errors.append(line)
            else:
                try:
                    # Try to parse from JSON input
                    rpm = InstalledRpm.from_json(line)
                    self.packages[rpm.name].append(rpm)
                except Exception:
                    # If that fails, try to parse from line input
                    if line.strip():
                        try:
                            rpm = InstalledRpm.from_line(line)
                            self.packages[rpm.name].append(rpm)
                        except Exception:
                            # Both ways failed
                            self.unparsed.append(line)

    def __contains__(self, package_name):
        """
        Checks if package name is in list of installed RPMs.

        Args:
            package_name (str): RPM package name such as 'bash'

        Returns:
            bool: True if package name is in list of installed packages, otherwise False
        """
        return package_name in self.packages

    @property
    def corrupt(self):
        """
        Property shortcut for parsed data.

        Returns:
            bool: True if RPM database is corrupted, else False
        """
        return any('rpmdbNextIterator' in s for s in self.errors)

    def get_max(self, package_name):
        """
        Returns the highest version of the installed package with the given name.

        Args:
            package_name (str): Installed RPM package name such as 'bash'

        Returns:
            InstalledRpm: Installed RPM with highest version
        """
        if package_name not in self.packages:
            return None
        else:
            return max(self.packages[package_name])

    def get_min(self, package_name):
        """
        Returns the lowest version of the installed package with the given name.

        Args:
            package_name (str): Installed RPM package name such as 'bash'

        Returns:
            InstalledRpm: Installed RPM with lowest version
        """
        if package_name not in self.packages:
            return None
        else:
            return min(self.packages[package_name])

    def check_versions_installed(self, packages_strings):
        """
        Check if any of the packages listed in a list is installed on the system.

        Args:
            packages_strings (iterable): list/iterable of checked package strings such as
                                         ['bash-4.2.39-3.el7', ...]

        Returns:
            dict: list of detected packages and list of their names in the following format,
                  otherwise None:

                  {PACKAGES: installed_package_strings,
                   PACKAGE_NAMES: installed_package_names}
        """
        installed_packages = set(chain.from_iterable(self.packages.values()))
        installed_listed_packages = [a for a in installed_packages if a.package in packages_strings]
        installed_listed_package_strings = sorted(a.package for a in installed_listed_packages)
        installed_listed_package_names = sorted({a.name for a in installed_listed_packages})
        if installed_listed_packages:
            return {PACKAGES: installed_listed_package_strings,
                    PACKAGE_NAMES: installed_listed_package_names}

    def vulnerable_versions_installed(self, vulnerable_package_strings):
        """
        Check if any of the packages listed in a list of vulnerable packages is installed on
        the system.

        Args:
            vulnerable_package_strings (iterable): list/iterable of vulnerable package strings
                                                   such as ['bash-4.2.39-3.el7', ...]

        Returns:
            dict: list of detected packages and list of their names in the following format,
                  otherwise None:

                  {VULNERABLE_PACKAGES: installed_vulnerable_package_strings,
                   PACKAGE_NAMES: installed_vulnerable_package_names}

        Warnings:
            This exists only for compatibility with older security rules, use
            'check_installed_version' method instead.
        """
        result = self.check_versions_installed(vulnerable_package_strings)
        if result:
            return {VULNERABLE_PACKAGES: result[PACKAGES], PACKAGE_NAMES: result[PACKAGE_NAMES]}

    def check_package_installed(self, package_name):
        """
        Check if package with concrete name is installed on the system.

        Args:
            package_name (str): name of package such as 'bash'

        Returns:
            dict: first found full package name which matches searched package in the following
                  format, otherwise None:

                  {INSTALLED_PACKAGE: package_found}
        """
        if package_name in self.packages:
            return {INSTALLED_PACKAGE: self.packages[package_name][0].package}


class InstalledRpm(object):
    """
    Class for holding information about one installed RPM.
    """
    SOSREPORT_KEYS = [
        'installtime', 'buildtime', 'vendor', 'buildserver', 'pgpsig', 'pgpsig-short'
    ]

    def __init__(self, data):
        """
        Args:
            data (dict): This class is usually created from dictionary with following structure:
                         {'name': 'package name',
                          'version': 'package version',
                          'release': 'package release,
                          'arch': 'package architecture'
                          }

                          It may also contain supplementary information from SOS report or epoch
                          information from JSON.
        """
        self.name = None
        self.version = None
        self.release = None
        self.arch = None

        for k, v in data.iteritems():
            setattr(self, k, v)
        if 'epoch' not in data:
            self.epoch = '0'

    @classmethod
    def from_package(cls, package_string):
        """
        The object of this class is usually created from dictionary. Alternatively it can be
        created from package string.

        Args:
            package_string (str): package string in the following format (shown as Python string):
                                  'kernel-devel-3.10.0-327.36.1.el7.x86_64'
        """
        return cls(cls._parse_package(package_string))

    @classmethod
    def from_json(cls, json_line):
        """
        The object of this class is usually created from dictionary. Alternatively it can be
        created from JSON line.

        Args:
            json_line (str): JSON string in the following format (shown as Python string):
                             '''{"name": "kernel-devel",
                                 "version": "3.10.0",
                                 "release": "327.36.1.el7",
                                 "arch": "x86_64"}'''
        """
        return cls(json.loads(json_line))

    @classmethod
    def from_line(cls, line):
        """
        The object of this class is usually created from dictionary. Alternatively it can be
        created from package line.

        Args:
            line (str): package line in the following format (shown as Python string):
                        ('kernel-devel-3.10.0-327.36.1.el7.x86_64'
                         '                                '
                         'Wed May 18 14:16:21 2016' '\t'
                         '1410968065' '\t'
                         'Red Hat, Inc.' '\t'
                         'hs20-bc2-4.build.redhat.com' '\t'
                         '8902150305004...b3576ff37da7e12e2285358267495ac48a437d4eefb3213' '\t'
                         'RSA/8, Mon Aug 16 11:14:17 2010, Key ID 199e2f91fd431d51')
        """
        return cls(cls._parse_line(line))

    @staticmethod
    def _arch_sep(package_string):
        """
        Helper method for finding if arch separator is '.' or '-'

        Args:
            package_string (str): dash separated package string such as 'bash-4.2.39-3.el7'

        Returns:
            str: arch separator
        """
        return '.' if package_string.rfind('.') > package_string.rfind('-') else '-'

    @classmethod
    def _parse_package(cls, package_string):
        """
        Helper method for parsing package string.

        Args:
            package_string (str): dash separated package string such as 'bash-4.2.39-3.el7'

        Returns:
            dict: dictionary containing 'name', 'version', 'release', and 'arch' keys
        """
        pkg, arch = rsplit(package_string, cls._arch_sep(package_string))
        if arch not in KNOWN_ARCHITECTURES:
            pkg, arch = (package_string, None)
        pkg, release = rsplit(pkg, '-')
        name, version = rsplit(pkg, '-')
        return {
            'name': name,
            'version': version,
            'release': release,
            'arch': arch
        }

    @classmethod
    def _parse_line(cls, line):
        """
        Helper method for parsing package line with or without SOS report information.

        Args:
            line (str): package line with or without SOS report information

        Returns:
            dict: dictionary containing 'name', 'version', 'release', and 'arch' keys plus
                  additionally 'installtime', 'buildtime', 'vendor', 'buildserver', 'pgpsig',
                  'pgpsig-short' if these are present.
        """
        try:
            pkg, rest = line.split(None, 1)
        except ValueError:
            rpm = cls._parse_package(line.strip())
            return rpm
        rpm = cls._parse_package(pkg)
        rest = rest.split('\t')
        for i, value in enumerate(rest):
            rpm[cls.SOSREPORT_KEYS[i]] = value
        return rpm

    @property
    def package(self):
        return '{}-{}-{}'.format(self.name,
                                 self.version,
                                 self.release
                                 )

    @property
    def nvr(self):
        """
        Alias for ``package``.
        NVR: Name, Version, Release.
        """
        return self.package

    @property
    def nvra(self):
        """
        Just like ``nvr``, but adds arch as well
        NVRA: Name, Version, Release, Arch
        """
        return ".".join([self.package, self.arch])

    @property
    def source(self):
        """
        Returns source RPM of this RPM.

        Returns:
            InstalledRpm: source RPM
        """
        if hasattr(self, 'srpm'):
            rpm = self.from_package(self.srpm)
            # Source RPMs don't have epoch for some reason
            rpm.epoch = self.epoch
            return rpm

    def __getitem__(self, item):
        """
        Allows to use `rpm["element"]` instead of `rpm.element`. Dot notation should be preferred,
        however it is especially useful for values containing dash, such as "pgpsig-short".
        """
        return getattr(self, item)

    def __str__(self):
        return '{}:{}'.format(self.epoch, self.package)

    def __unicode__(self):
        return unicode(str(self))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return (
            type(self) == type(other) and
            self.name == other.name and
            LV(self.epoch) == LV(other.epoch) and
            LV(self.version) == LV(other.version) and
            LV(self.release) == LV(other.release)
        )

    def __lt__(self, other):
        if self.name != other.name:
            raise ValueError('Cannot compare packages with differing names {} != {}'
                             .format(self.name, other.name))
        if self == other:
            return False

        self_v, other_v = LV(self.version), LV(other.version)
        self_ep, other_ep = LV(self.epoch), LV(other.epoch)

        if self_ep != other_ep:
            return self_ep < other_ep

        if self_v != other_v:
            return self_v < other_v

        return LV(self.release) < LV(other.release)

    def __ne__(self, other):
        return self < other or other < self

    def __gt__(self, other):
        return other < self

    def __ge__(self, other):
        return not self < other

    def __le__(self, other):
        return not other < self
