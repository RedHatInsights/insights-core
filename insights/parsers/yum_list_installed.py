"""
YumListInstalled - Command ``yum list installed``
===================================

Sample input data::
    NetworkManager-bluetooth.x86_64           1:1.10.10-1.fc28              @updates
    NetworkManager-config-connectivity-fedora.noarch
                                              1:1.10.10-1.fc28              @updates
    NetworkManager-glib.x86_64                1:1.10.10-1.fc28              @updates
"""
from collections import defaultdict
from insights import parser, Parser
from insights.parsers.installed_rpms import InstalledRpm, RpmList
from insights.specs import Specs


class YumInstalledRpm(InstalledRpm):
    def __init__(self, data):
        self.repo = None
        """str: yum / dnf repository name, if available."""

        super(YumInstalledRpm, self).__init__(data)


@parser(Specs.yum_list_installed)
class YumListInstalled(Parser, RpmList):
    """
    A parser for working with data containing a list of installed RPM files on
    the system and related information.
    """
    def _get_rows(self, content):
        """
        "yum list installed" output is basically tabular with an ignorable row
        at the top, but each column after has a maximum width. If any column
        overflows, the following columns wrap to the next line and indent to
        their usual starting positions. We sidestep the wrapping by collapsing
        all the lines into a single line, splitting on whitespace, and
        collecting records as groups of three.
        """
        if content[0] == "Installed Packages":
            content = content[1:]
        content = "\n".join(content).split()
        return zip(*(iter(content),) * 3)

    def _make_record(self, package, ver_rel, repo):
        """
        Given the fields of a ``yum list installed`` row, return a dictionary
        of name, version, release, epoch, arch, and repo.
        """
        name, _, arch = package.rpartition(".")
        repo = repo.lstrip("@")

        # Kept as string in InstalledRpm. Duplicating here for consistency.
        epoch = "0"
        if ":" in ver_rel:
            epoch, ver_rel = ver_rel.split(":", 1)
        version, release = ver_rel.split("-")

        # This is special cased for InstalledRpm. Duplicating here for
        # consistency.
        if name.startswith('oracleasm') and name.endswith('.el5'):
            name, version2 = name.split('-', 1)
            version = version2 + '-' + version

        return {"name": name, "version": version, "release": release, "epoch":
                epoch, "arch": arch, "repo": repo}

    def parse_content(self, content):
        packages = defaultdict(list)
        for row in self._get_rows(content):
            rec = self._make_record(*row)
            packages[rec["name"]].append(YumInstalledRpm(rec))
        self.packages = dict(packages)
