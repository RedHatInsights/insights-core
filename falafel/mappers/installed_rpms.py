import json
from collections import defaultdict
from distutils.version import LooseVersion as LV

from ..util import rsplit
from .. import MapperOutput, mapper, computed, get_active_lines

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


@mapper('installed-rpms')
class InstalledRpms(MapperOutput):

    @computed
    def corrupt(self):
        return any("rpmdbNextIterator" in s for s in self.get("__error", []))

    @computed
    def unparsed_lines(self):
        return self.get("__unparsed", [])

    def get_max(self, name):
        """
        Returns the highest version of the installed RPM with the given name
        """
        return max(self[name]) if name in self else None

    def __len__(self):
        return len(self.data)

    @classmethod
    def parse_content(cls, content):
        packages = defaultdict(list)
        content = get_active_lines(content, comment_char="COMMAND>")
        try:
            for line in content:
                if line.startswith("error:") or line.startswith("warning:"):
                    packages["__error"].append(line)
                else:
                    rpm = json.loads(line)
                    packages[rpm["name"]].append(InstalledRpm(rpm))
        except:
            for line in content:
                if line.startswith("error:") or line.startswith("warning:"):
                    packages["__error"].append(line)
                else:
                    try:
                        name, rpm = parse_line(line)
                        packages[name].append(InstalledRpm(rpm))
                    except Exception:
                        packages["__unparsed"].append(line)
        return packages


class InstalledRpm(MapperOutput):

    @computed
    def package(self):
        return "%s-%s-%s" % (
            self["name"],
            self["version"],
            self["release"]
        )

    @property
    def name(self):
        return self.get('name')

    @property
    def version(self):
        return self.get('version')

    @property
    def release(self):
        return self.get('release')

    @property
    def epoch(self):
        return self.get('epoch', '0')

    @property
    def source(self):
        if "srpm" in self.data:
            r = InstalledRpm.from_package(self.data["srpm"])
            r.data["epoch"] = self.epoch
            return r

    def __str__(self):
        return "%s:%s" % (self.epoch, self.package)

    def __unicode__(self):
        return str(self)

    def __repr__(self):
        return str(self)

    @classmethod
    def from_package(cls, package_string):
        return InstalledRpm(parse_package(package_string))

    def __eq__(self, other):
        return (
            self.name == other.name and
            LV(self.epoch) == LV(other.epoch) and
            LV(self.version) == LV(other.version) and
            LV(self.release) == LV(other.release)
        )

    def __lt__(self, other):
        if self.name != other.name:
            raise ValueError("Cannot compare packages with differing names %s != %s" % (self.name, other.name))

        if self == other:
            return False

        self_v, other_v = LV(self.version), LV(other.version)
        self_ep, other_ep = LV(self.epoch), LV(other.epoch)

        if self_ep != other_ep:
            return self_ep < other_ep

        if self_v != other_v:
            return self_v < other_v

        return LV(self.release) < LV(other.release)

    def __gt__(self, other):
        return other.__lt__(self)

    def __le__(self, other):
        return self == other or self.__lt__(other)

    def __ge__(self, other):
        return self == other or self.__gt__(other)


SOSREPORT_KEYS = [
    "installtime", "buildtime", "vendor",
    "buildserver", "pgpsig", "pgpsig-short"
]


def arch_sep(s):
    return "." if s.rfind(".") > s.rfind("-") else "-"


def parse_package(package_string):
    pkg, arch = rsplit(package_string, arch_sep(package_string))
    if arch not in KNOWN_ARCHITECTURES:
        pkg, arch = (package_string, None)
    pkg, release = rsplit(pkg, "-")
    name, version = rsplit(pkg, "-")
    return {
        "name": name,
        "version": version,
        "release": release,
        "arch": arch
    }


def parse_line(line):
    try:
        pkg, rest = line.split(None, 1)
    except ValueError:
        rpm = parse_package(line.strip())
        return rpm["name"], rpm
    rpm = parse_package(pkg)
    rest = rest.split("\t")
    for i, value in enumerate(rest):
        rpm[SOSREPORT_KEYS[i]] = value
    return rpm["name"], rpm
