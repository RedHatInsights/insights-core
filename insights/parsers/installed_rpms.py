"""
InstalledRpms - Command ``rpm -qa``
===================================


InstalledRpms - command ``rpm -qa``
-----------------------------------
ContainerInstalledRpms - command ``rpm -qa`` for containers
-----------------------------------------------------------
"""

import json
import re
import six
import warnings

from collections import defaultdict

from insights import ContainerParser, parser, CommandParser
from insights.core.exceptions import SkipComponent
from insights.parsers.rpm_vercmp import rpm_version_compare
from insights.specs import Specs
from insights.util import rsplit


# This list of architectures is taken from PDC (Product Definition Center):
# https://pdc.fedoraproject.org/rest_api/v1/arches/
KNOWN_ARCHITECTURES = [
    # Common architectures
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
    # Less common
    'alpha',
    'alphaev4',
    'alphaev45',
    'alphaev5',
    'alphaev56',
    'alphaev6',
    'alphaev67',
    'alphaev68',
    'alphaev7',
    'alphapca56',
    'arm64',
    'armv5tejl',
    'armv5tel',
    'armv6l',
    'armv7hl',
    'armv7hnl',
    'armv7l',
    'athlon',
    'armhfp',
    'geode',
    'ia32e',
    'nosrc',
    'ppc64iseries',
    'ppc64le',
    'ppc64p7',
    'ppc64pseries',
    'sh3',
    'sh4',
    'sh4a',
    'sparc',
    'sparc64',
    'sparc64v',
    'sparcv8',
    'sparcv9',
    'sparcv9v',
    'aarch64',
]
"""list: List of recognized architectures.

This list is taken from the PDC (Product Definition Center) available
here https://pdc.fedoraproject.org/rest_api/v1/arches/.
"""


class RpmList(object):
    """
    Mixin class providing ``__contains__``, ``get_max``, ``get_min``,
    ``newest``, and ``oldest`` implementations for components that handle rpms.
    """

    def __contains__(self, package_name):
        """
        Checks if package name is in list of installed RPMs.

        .. note::
            The :attr:`packages` could be empty, e.g. when rpm database corrupt.
            When doing exclusion check, make sure the ``packages`` is NOT
            empty, e.g.::

                if rpms.packages and "pkg_name" not in rpms:
                    pass

        Args:
            package_name (str): RPM package name such as 'bash'

        Returns:
            bool: True if package name is in list of installed packages, otherwise False
        """
        return package_name in self.packages

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
            package_name (str): Installed RPM package name such as 'bash'.

        Returns:
            InstalledRpm: Installed RPM with lowest version
        """
        if package_name not in self.packages:
            return None
        else:
            return min(self.packages[package_name])

    @property
    def is_hypervisor(self):
        """
        .. warning::
           This method is deprecated, and will be removed from 3.3.0. Please use
           :py:class:`insights.parsers.virt_what.VirtWhat` which uses the command `virt-what` to check the hypervisor type.

        bool: True if ".el[6|7]ev" exists in "vdsm".release, else False.
        """
        warnings.warn("`is_hypervisor` is deprecated and will be removed from 3.3.0: Use `virt_what.VirtWhat` which uses the command `virt-what` to check the hypervisor type.", DeprecationWarning)
        rpm = self.get_max("vdsm")
        return (True if rpm and rpm.release.endswith((".el6ev", ".el7ev")) else
                False)

    # re-export get_max/min with more descriptive names
    newest = get_max
    oldest = get_min


@parser(Specs.installed_rpms)
class InstalledRpms(CommandParser, RpmList):
    """
    The ``InstalledRpms`` class parses the output of the ``rpm -qa`` command.
    Each line is parsed and stored in an ``InstalledRpm`` object.  The ``rpm -qa``
    command may output data in different formats and each format can be
    handled by the parsing routines of this class. The basic format of command is
    the package and is shown in the Examples.

    A parser for working with data containing a list of installed RPM files on the system
    and related information.

    Sample input data::

        a52dec-0.7.4-18.el7.nux.x86_64  Tue 14 Jul 2015 09:25:38 AEST   1398536494
        aalib-libs-1.4.0-0.22.rc5.el7.x86_64    Tue 14 Jul 2015 09:25:40 AEST   1390535634
        abrt-2.1.11-35.el7.x86_64       Wed 09 Nov 2016 14:52:01 AEDT   1446193355
        ...
        kernel-3.10.0-267.el7.x86_64    Sat 24 Oct 2015 09:56:17 AEDT   1434466402
        kernel-3.10.0-327.36.3.el7.x86_64       Wed 09 Nov 2016 14:53:25 AEDT   1476954923
        kernel-headers-3.10.0-327.36.3.el7.x86_64       Wed 09 Nov 2016 14:20:59 AEDT   1476954923
        kernel-tools-3.10.0-327.36.3.el7.x86_64 Wed 09 Nov 2016 15:09:42 AEDT   1476954923
        kernel-tools-libs-3.10.0-327.36.3.el7.x86_64    Wed 09 Nov 2016 14:52:13 AEDT   1476954923
        kexec-tools-2.0.7-38.el7_2.1.x86_64     Wed 09 Nov 2016 14:48:21 AEDT   1452845178
        ...
        zlib-1.2.7-15.el7.x86_64        Wed 09 Nov 2016 14:21:19 AEDT   1431443476
        zsh-5.0.2-14.el7_2.2.x86_64     Wed 09 Nov 2016 15:13:19 AEDT   1464185248


    Examples:
        >>> type(rpms)
        <class 'insights.parsers.installed_rpms.InstalledRpms'>
        >>> 'kernel' in rpms
        True
        >>> rpms.corrupt
        False
        >>> rpms.get_max('kernel')
        0:kernel-3.10.0-327.36.3.el7
        >>> type(rpms.get_max('kernel'))
        <class 'insights.parsers.installed_rpms.InstalledRpm'>
        >>> rpms.get_min('kernel')
        0:kernel-3.10.0-267.el7
        >>> rpm = rpms.get_max('kernel')
        >>> rpm
        0:kernel-3.10.0-327.36.3.el7
        >>> type(rpm)
        <class 'insights.parsers.installed_rpms.InstalledRpm'>
        >>> rpm.package == 'kernel-3.10.0-327.36.3.el7'
        True
        >>> rpm.nvr == 'kernel-3.10.0-327.36.3.el7'
        True
        >>> rpm.source
        >>> rpm.name
        'kernel'
        >>> rpm.version
        '3.10.0'
        >>> rpm.release
        '327.36.3.el7'
        >>> rpm.arch
        'x86_64'
        >>> rpm.epoch
        '0'
        >>> from insights.parsers.installed_rpms import InstalledRpm
        >>> rpm2 = InstalledRpm.from_package('kernel-3.10.0-267.el7')
        >>> rpm == rpm2
        False
        >>> rpm > rpm2
        True
        >>> rpm < rpm2
        False

    """
    def __init__(self, *args, **kwargs):
        self.errors = list()
        """list: List of input lines that indicate an error acquiring the data on the client."""
        self.unparsed = list()
        """list: List of input lines that raised an exception during parsing."""
        self.packages = dict()
        """
        dict (InstalledRpm): Dictionary of RPMs keyed by package name.

        .. note::
            The ``packages`` could be empty, e.g. when rpm database corrupt.
            When doing exclusion check, make sure the ``packages`` is NOT
            empty, e.g.::

                >>> if rpms.packages and "pkg_name" not in rpms.packages:
                >>>     pass
        """
        super(InstalledRpms, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        if content and (not content[0].strip() or "COMMAND>" in content[0]):
            content = content[1:]
        if not content:
            raise SkipComponent("The content of rpm command is empty!")
        parse_func = InstalledRpm.from_json if any(
                '"name":' in _l for _l in content) else InstalledRpm.from_line
        packages = defaultdict(list)
        for line in content:
            if not line.strip():
                continue
            if line.startswith('error:') or line.startswith('warning:'):
                self.errors.append(line)
            else:
                try:
                    rpm = parse_func(line)
                    packages[rpm.name].append(rpm)
                except Exception:
                    self.unparsed.append(line)
        self.packages = dict(packages)

    @property
    def corrupt(self):
        """bool: True if RPM database is corrupted, else False."""
        _corrupts = [
            'error: rpmdbNextIterator',
            'error: rpmdb: BDB0113',
            'error: db5 error',
        ]
        return any(c in s for s in self.errors for c in _corrupts)


p = re.compile(r"(\d+|[a-z]+|\.|-|_)")


def _int_or_str(c):
    try:
        return int(c)
    except ValueError:
        return c


def vcmp(s):
    return [_int_or_str(c) for c in p.split(s) if c and c not in (".", "_", "-")]


def pad_version(left, right):
    """Returns two sequences of the same length so that they can be compared.
    The shorter of the two arguments is lengthened by inserting extra zeros
    before non-integer components.  The algorithm attempts to align character
    components."""
    pair = vcmp(left), vcmp(right)

    mn, mx = min(pair, key=len), max(pair, key=len)

    for idx, c in enumerate(mx):

        try:
            a = mx[idx]
            b = mn[idx]
            if type(a) != type(b):
                mn.insert(idx, 0)
        except IndexError:
            if type(c) is int:
                mn.append(0)
            elif isinstance(c, six.string_types):
                mn.append('')
            else:
                raise Exception("pad_version failed (%s) (%s)" % (left, right))

    return pair


class InstalledRpm(object):
    """
    Class for holding information about one installed RPM.

    This class is usually created from dictionary with following structure::

         {
            'name': 'package name',
            'version': 'package version',
            'release': 'package release',
            'arch': 'package architecture'
          }

    It may also contain supplementary information from SOS report or epoch
    information from JSON.

    When comparing rpms whose epoch is not ``null``, it is necessary to create
    InstalledRpm object with epoch information like following example::

        InstalledRpm.from_json('{"name":"microcode_ctl","epoch":"4","version":"20200609","release":"2.20201027.1.el8_3"}'

    Factory methods are provided such as ``from_package`` to create an object from a
    short package string::

        kernel-devel-3.10.0-327.36.1.el7.x86_64

    ``from_json`` to create an object from JSON::

       {"name": "kernel-devel",
        "version": "3.10.0",
        "release": "327.36.1.el7",
        "arch": "x86_64"}

    and ``from_line`` to create an object from a long package string:

        .. code:: python

            ('kernel-devel-3.10.0-327.36.1.el7.x86_64'
             '                                '
             'Wed May 18 14:16:21 2016' '\t'
             '1410968065' '\t'
             'Red Hat, Inc.' '\t'
             'hs20-bc2-4.build.redhat.com' '\t'
             '8902150305004...b3576ff37da7e12e2285358267495ac48a437d4eefb3213' '\t'
             'RSA/8, Mon Aug 16 11:14:17 2010, Key ID 199e2f91fd431d51')
    """
    PRODUCT_SIGNING_KEYS = [
        # NOTE: All In lower cases
        # RELEASE PACKAGE SIGNING
        '199e2f91fd431d51', '1ac4971355a34a82', '5054e4a45a6340b3',
        'e1a4bd708a828aad', 'f76f66c3d4082792', '5326810137017186',
        '45689c882fa658e0', '219180cddb42a60e', '7514f77d8366b0d9',
        '08dd962c1c711042',
        # BETA PACKAGE SIGNING
        'fd372689897da07a', '938a80caf21541eb'
        # DEVELOPMENT PACKAGE SIGNING
        '08b871e6a5787476',
        # OTHER PRODUCTS
        'e191ddb2c509e861',
        # CERTIFICATES
        '66e8f8a29c65f85c', '680b9144769a9f8f', '8ed29db42a2898c8'
    ]
    """
    list: List of package-signing keys in all lower cases. Should be updated
          timely according to https://access.redhat.com/security/team/key/
    """
    SOSREPORT_KEYS = [
        'installtime', 'buildtime', 'vendor', 'buildserver', 'pgpsig', 'pgpsig_short'
    ]
    """list: List of keys for SOS Report RPM information."""

    def __init__(self, data):
        self.name = None
        """str: RPM package name."""
        self.version = None
        """str: RPM package version."""
        self.release = None
        """str: RPM package release."""
        self.arch = None
        """str: RPM package architecture."""
        self.redhat_signed = None
        """bool: True when RPM package is signed by Red Hat, False when RPM package is not signed by Red Hat,
        None when no sufficient info to determine"""
        self.vendor = None
        """str: RPM package vendor. `None` when no 'vendor' info"""

        if isinstance(data, six.string_types):
            data = self._parse_package(data)

        for k, v in data.items():
            setattr(self, k, v)
        self.epoch = data['epoch'] if 'epoch' in data and data['epoch'] != '(none)' else '0'
        self.vendor = data['vendor'] if 'vendor' in data else None
        _gpg_key_pos = data.get('sigpgp', data.get('rsaheader', data.get('pgpsig_short', data.get('pgpsig', data.get('vendor', '')))))
        if _gpg_key_pos:
            self.redhat_signed = any(key in _gpg_key_pos.lower()
                                     for key in self.PRODUCT_SIGNING_KEYS)

    @classmethod
    def from_package(cls, package_string):
        """
        The object of this class is usually created from dictionary. Alternatively it can be
        created from package string.

        Args:
            package_string (str): package string in the following format (shown as Python string)::

                'kernel-devel-3.10.0-327.36.1.el7.x86_64'
        """
        return cls(cls._parse_package(package_string))

    @classmethod
    def from_json(cls, json_line):
        """
        The object of this class is usually created from dictionary. Alternatively it can be
        created from JSON line.

        Args:
            json_line (str): JSON string in the following format (shown as Python string)::

                '{"name": "kernel-devel", "version": "3.10.0", "release": "327.36.1.el7", "arch": "x86_64"}'
        """
        return cls(json.loads(json_line))

    @classmethod
    def from_line(cls, line):
        """
        The object of this class is usually created from dictionary. Alternatively it can be
        created from package line.

        Args:
            line (str): package line in the following format (shown as Python string):

                .. code-block:: python

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
            package_string (str): dash separated package string such as 'bash-4.2.39-3.el7'.

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
            dict: dictionary containing 'name', 'version', 'release' and 'arch' keys
        """
        pkg, arch = rsplit(package_string, cls._arch_sep(package_string))
        if arch not in KNOWN_ARCHITECTURES:
            pkg, arch = (package_string, None)
        pkg, release = rsplit(pkg, '-')
        name, version = rsplit(pkg, '-')
        epoch, version = version.split(':', 1) if ":" in version else ['0', version]
        # oracleasm packages have a dash in their version string, fix that
        if name.startswith('oracleasm') and name.endswith('.el5'):
            name, version2 = name.split('-', 1)
            version = version2 + '-' + version
        return {
            'name': name,
            'version': version,
            'release': release,
            'arch': arch,
            'epoch': epoch
        }

    @classmethod
    def _parse_line(cls, line):
        """
        Helper method for parsing package line with or without SOS report information.

        Args:
            line (str): package line with or without SOS report information

        Returns:
            dict: dictionary containing 'name', 'version', 'release' and 'arch' keys plus
                  additionally 'installtime', 'buildtime', 'vendor', 'buildserver', 'pgpsig',
                  'pgpsig_short' if these are present.
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
        """str: Package `name-version-release` string."""
        return u'{0}-{1}-{2}'.format(self.name,
                                     self.version,
                                     self.release)

    @property
    def package_with_epoch(self):
        """
        str: Package string in the format::

            name-epoch:version-release
        """
        return u'{0}-{1}:{2}-{3}'.format(self.name,
                                         self.epoch,
                                         self.version,
                                         self.release)

    @property
    def nvr(self):
        """str: Package `name-version-release` string."""
        return self.package

    @property
    def nvra(self):
        """str: Package `name-version-release.arch` string."""
        return ".".join([self.package, self.arch])

    @property
    def nevra(self):
        """
        str: Package string in the format::

            name-epoch:version-release.arch
        """
        return ".".join([self.package_with_epoch, self.arch])

    @property
    def source(self):
        """InstalledRpm: Returns source RPM of this RPM object."""
        if hasattr(self, 'srpm'):
            rpm = self.from_package(self.srpm)
            # Source RPMs don't have epoch for some reason
            rpm.epoch = self.epoch
            return rpm

    def __getitem__(self, item):
        """
        Allows to use `rpm["element"]` instead of `rpm.element`. Dot notation should be preferred,
        however it is especially useful for values containing dash, such as "pgpsig_short".
        """
        return getattr(self, item)

    def __str__(self):
        return '{0}:{1}'.format(self.epoch, self.package)

    def __unicode__(self):
        return str(self)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, InstalledRpm):
            return False

        if self.name != other.name:
            raise ValueError('Cannot compare packages with differing names {0} != {1}'
                             .format(self.name, other.name))

        return rpm_version_compare(self, other) == 0

    def __lt__(self, other):
        if not isinstance(other, InstalledRpm):
            return False

        if self == other:
            return False

        return rpm_version_compare(self, other) < 0

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        return isinstance(other, InstalledRpm) and other.__lt__(self)

    def __ge__(self, other):
        return isinstance(other, InstalledRpm) and not self.__lt__(other)

    def __le__(self, other):
        return isinstance(other, InstalledRpm) and not other.__lt__(self)

    def __hash__(self):
        # Python 3 requires hash implementation to have hashable object.
        try:
            # Just NVR is not enouch for uniqueness. Try NVRA first.
            value = self.nvra
        except TypeError:
            value = self.nvr
        return hash(value)


# re-exports
from_package = InstalledRpm.from_package
Rpm = InstalledRpm
Installed = InstalledRpms


@parser(Specs.container_installed_rpms)
class ContainerInstalledRpms(ContainerParser, InstalledRpms):
    """
    Parses the data for list of installed rpms of the running
    containers which are based on RHEL images.

    Sample output::

        a52dec-0.7.4-18.el7.nux.x86_64                  Tue 14 Jul 2015 09:25:38 AEST   1398536494
        aalib-libs-1.4.0-0.22.rc5.el7.x86_64            Tue 14 Jul 2015 09:25:40 AEST   1390535634
        abrt-2.1.11-35.el7.x86_64                       Wed 09 Nov 2016 14:52:01 AEDT   1446193355
        kernel-3.10.0-267.el7.x86_64                    Sat 24 Oct 2015 09:56:17 AEDT   1434466402
        kernel-3.10.0-327.36.3.el7.x86_64               Wed 09 Nov 2016 14:53:25 AEDT   1476954923
        kernel-headers-3.10.0-327.36.3.el7.x86_64       Wed 09 Nov 2016 14:20:59 AEDT   1476954923
        kernel-tools-3.10.0-327.36.3.el7.x86_64         Wed 09 Nov 2016 15:09:42 AEDT   1476954923
        kernel-tools-libs-3.10.0-327.36.3.el7.x86_64    Wed 09 Nov 2016 14:52:13 AEDT   1476954923
        kexec-tools-2.0.7-38.el7_2.1.x86_64             Wed 09 Nov 2016 14:48:21 AEDT   1452845178
        zlib-1.2.7-15.el7.x86_64                        Wed 09 Nov 2016 14:21:19 AEDT   1431443476
        zsh-5.0.2-14.el7_2.2.x86_64                     Wed 09 Nov 2016 15:13:19 AEDT   1464185248

    Examples:
        >>> type(container_rpms)
        <class 'insights.parsers.installed_rpms.ContainerInstalledRpms'>
        >>> container_rpms.container_id
        'cc2883a1a369'
        >>> container_rpms.image
        'quay.io/rhel8'
        >>> container_rpms.engine
        'podman'
        >>> container_rpms.get_min('kernel').package == 'kernel-3.10.0-267.el7'
        True
        >>> container_rpms.get_max("kernel").name
        'kernel'
        >>> container_rpms.get_max("kernel").version
        '3.10.0'
    """
    pass
