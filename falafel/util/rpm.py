from falafel.util import rsplit

FEDORA_RELEASE = '.fc'
RHEL_RELEASE = '.el'

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
    'noarch'
]


class RpmPackage(object):
    '''
    Represents a RPM package, providing parsing of the fields of
    the package (name, version, release, arch) and allowing
    comparision of RPM package versions.

    Consider the example package label ::

        bind-libs-9.8.2-0.17.rc1.el6_4.6.x86_64

    Here we expect to break the package label into dictionary of the form::

        {
            "name": "bind-libs",
            "version": "9.8.2",
            "release": "0.17.rc1.el6_4.6",
            "arch": "x86_64",
            "build": "0.17.rc1",
            "dist": "el6_4.6"
        }

    There is lots of variation in the release.  To make the
    parsing more tractable we assume that the build number part
    of the release will always be followed by an "el" of "fc"
    identifier.

    The only field that can contain '-' characters is the package name.

    As much as possible, package labels that are formatted in a
    manner contrary to the assumptions in the parsing will
    raise a ValueError.
    '''

    def __init__(self, package, ignore_arch=True):
        '''
        Construct the class using the package label string
        specified in 'package.'  'ignore_arch' indicates if
        the arch field should be ignored when comparing two
        RpmPackages.
        '''
        self.package = package.encode("utf-8")
        self.ignore_arch = ignore_arch
        release_error = False
        try:
            if any([a in package for a in KNOWN_ARCHITECTURES]):
                lhs, self.arch = rsplit(package, "-.")
                self.name, self.version, self.release = lhs.rsplit('-', 2)
            else:
                self.arch = None
                self.name, self.version, self.release = package.rsplit('-', 2)

            if RHEL_RELEASE in self.release:
                release_parts = self.release.partition(RHEL_RELEASE)
            elif FEDORA_RELEASE in self.release:
                release_parts = self.release.partition(FEDORA_RELEASE)
            else:
                release_error = True

            if not release_error:
                self.build, self.dist = RpmPackage._get_build_dist(release_parts)

        except ValueError:
            raise ValueError("Improper package name: {0}".format(package))

        if release_error:
            raise ValueError("Package not from a RHEL or Fedora release {0}".format(package))

    @staticmethod
    def _get_build_dist(parts):
        build = parts[0]
        dist = parts[1][1:] + parts[2]
        return (build, dist)

    def __str__(self):
        return "%s" % self.package

    def name_dist_match(self, other):
        if not isinstance(other, RpmPackage):
            other = RpmPackage(other)

        return self.name == other.name and self.dist == other.dist

    @staticmethod
    def pad_version(version1, version2):
        """
        Pad out versions fields so that the two versions specified can
        be properly compared using ``distutils.version.LooseVersion``.

        The number of fields is determined by the version containing
        the largest number of fields.  The other version is then
        expanded by appending fields with value '0' to the end
        of the version string.

        For example, suppose ``version1`` is ``3.3`` and
        ``version2`` is ``3.3.2``.  The result returned would be the
        tuple ``( '3.3.0', '3.3.2')``.
        """
        version1_len = len(version1.split('.'))
        version2_len = len(version2.split('.'))

        pad_length = max(version1_len, version2_len)
        version1 += '.0' * (pad_length - version1_len)
        version2 += '.0' * (pad_length - version2_len)
        return (version1, version2)


def get_package_nvr(installed_rpms_line):
    """
    Given a line from an ``installed-rpms`` file, this method will
    extract out and return the NVR without the architecture.

    For example, given, ::

        xorg-x11-server-common-1.13.0-23.1.el6_5.x86_64             Wed Jan 15 20:30:24 2014

    The method will return ::

        xorg-x11-server-common-1.13.0-23.1.el6_5
    """
    nvr, arch = rsplit(installed_rpms_line.split()[0], "-.")
    if arch in KNOWN_ARCHITECTURES:
        return nvr
