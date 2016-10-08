import json
from collections import defaultdict
from distutils.version import LooseVersion as LV

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


@mapper('installed-rpms')
class InstalledRpms(Mapper):
    """
    A mapper for working with data containing a list of installed RPM files on the system and
    related information.

    The main data structure is defined as follows:
        {'packages': {'package_name_1': [InstalledRpm_1, InstalledRpm_2, ...], ...},
         'errors':   ['error_line_1', ...],
         'unparsed': ['unparsed line_1', ...],
        }
    """
    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Mapper context content

        Returns:
            dict: dictionary with parsed data
        """

        self.errors = []
        self.unparsed = []
        self.packages = defaultdict(list)
        for line in get_active_lines(content, comment_char='COMMAND>'):
            if line.startswith('error:') or line.startswith('warning:'):
                self.errors.append(line)
            else:
                try:
                    # Try to parse from JSON input
                    rpm = InstalledRpm.from_json(line)
                except Exception:
                    # If that fails, try to parse from line input
                    if line.strip():
                        try:
                            rpm = InstalledRpm.from_line(line)
                        except Exception:
                            # Both ways failed
                            self.unparsed.append(line)
                        else:
                            self.packages[rpm['name']].append(rpm)
                else:
                    self.packages[rpm['name']].append(rpm)

        self.data = {'packages': self.packages,
                     'errors': self.errors,
                     'unparsed': self.unparsed,
                     }

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.packages

    @property
    def corrupt(self):
        """
        Property shortcut for parsed data.

        Returns:
            bool: True if RPM database is corrupted, else False
        """
        return any('rpmdbNextIterator' in s for s in self.errors)

    def get_max(self, name):
        """
        Returns the highest version of the installed RPM with the given name.

        Args:
            name(str): Installed RPM package name

        Returns:
            InstalledRpm: Installed RPM with highest version
        """
        if name not in self.packages:
            return None
        else:
            return max(self.packages[name])

    def get_min(self, name):
        """
        Returns the lowest version of the installed RPM with the given name. This should be handy
        for checking against list of vulnerable versions.

        Args:
            name(str): Installed RPM package name

        Returns:
            InstalledRpm: Installed RPM with lowest version
        """
        if name not in self.packages:
            return None
        else:
            return min(self.packages[name])


class InstalledRpm(object):
    """
    Class for holding information about one installed RPM.

    The main data structure is defined as follows:
        {'name': 'package name',
         'version': 'package version',
         'release': 'package release,
         'arch': 'package architecture'
        }

    It may also contain supplementary information from SOS report.
    """
    SOSREPORT_KEYS = [
        'installtime', 'buildtime', 'vendor', 'buildserver', 'pgpsig', 'pgpsig-short'
    ]

    def __init__(self, data):
        self.data = data
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
            package_string (str): dash separated package string

        Returns:
            str: arch separator
        """
        return '.' if package_string.rfind('.') > package_string.rfind('-') else '-'

    @classmethod
    def _parse_package(cls, package_string):
        """
        Helper method for parsing package string.

        Args:
            package_string (str): dash separated package string

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
        return self.data[item]

    def __str__(self):
        return '{}:{}'.format(self.epoch, self.package)

    def __unicode__(self):
        return unicode(str(self))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return (
            self.name == other.name and
            LV(self.epoch) == LV(other.epoch) and
            LV(self.version) == LV(other.version) and
            LV(self.release) == LV(other.release)
        )

    def __lt__(self, other):
        if self.name != other.name:
            raise ValueError('Cannot compare packages with differing names {} != {}'
                             .format(self['name'], other['name']))
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
