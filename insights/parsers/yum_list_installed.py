"""
YumListInstalled - Command ``yum list installed``
=================================================
The ``YumListInstalled`` class parses the output of the ``yum list installed``
command. Each line is parsed and stored in a ``YumInstalledRpm`` object.

Sample input data::

    Loaded plugins: product-id, search-disabled-repos, subscription-manager
    Installed Packages
    GConf2.x86_64                    3.2.6-8.el7             @rhel-7-server-rpms
    GeoIP.x86_64                     1.5.0-11.el7            @anaconda/7.3
    ImageMagick.x86_64               6.7.8.9-15.el7_2        @rhel-7-server-rpms
    NetworkManager.x86_64            1:1.4.0-17.el7_3        installed
    NetworkManager.x86_64            1:1.8.0-9.el7           installed
    NetworkManager-config-server.noarch
                                     1:1.8.0-9.el7           installed
    Uploading Enabled Repositories Report
    Loaded plugins: priorities, product-id, rhnplugin, rhui-lb, subscription-
                  : manager, versionlock

Examples:
    >>> type(rpms)
    <class 'insights.parsers.yum_list_installed.YumListInstalled'>
    >>> 'GeoIP' in rpms
    True
    >>> rpms.get_max('GeoIP')
    0:GeoIP-1.5.0-11.el7
    >>> rpms.expired_cache
    True
    >>> type(rpms.get_max('GeoIP'))
    <class 'insights.parsers.yum_list_installed.YumInstalledRpm'>
    >>> rpm = rpms.get_max('GeoIP')
    >>> rpm.package
    'GeoIP-1.5.0-11.el7'
    >>> rpm.nvr
    'GeoIP-1.5.0-11.el7'
    >>> rpm.source
    >>> rpm.name
    'GeoIP'
    >>> rpm.version
    '1.5.0'
    >>> rpm.release
    '11.el7'
    >>> rpm.arch
    'x86_64'
    >>> rpm.epoch
    '0'
    >>> from insights.parsers.yum_list_installed import YumInstalledRpm
    >>> rpm2 = YumInstalledRpm.from_package('GeoIP-1.6.0-11.el7.x86_64')
    >>> rpm == rpm2
    False
    >>> rpm > rpm2
    False
    >>> rpm < rpm2
    True
"""
from collections import defaultdict

from insights import CommandParser, parser, SkipComponent
from insights.specs import Specs
from insights.parsers.installed_rpms import InstalledRpm, RpmList


class YumInstalledRpm(InstalledRpm):
    """
    The same as :py:class:`insights.parsers.installed_rpms.InstalledRpm` but
    with an additional ``.repo`` attribute.
    """
    def __init__(self, data):
        self.repo = None
        """str: yum / dnf repository name, if available."""

        super(YumInstalledRpm, self).__init__(data)


@parser(Specs.yum_list_installed)
class YumListInstalled(CommandParser, RpmList):
    """
    ``YumListInstalled`` shares the :py:class:`insights.parsers.installed_rpms.RpmList` interface with
    :py:class:`insights.parsers.installed_rpms.InstalledRpms`. The only difference is ``YumListInstalled``
    takes the output of ``yum list installed`` as its source data, and the
    :py:class:`YumInstalledRpm` instances it produces contain a ``.repo``
    attribute.
    """

    def __init__(self, context):
        self.expired_cache = False
        """bool: Indicates if the yum repo cache is expired."""

        super(YumListInstalled, self).__init__(context)

    def _find_start(self, content):
        for i, c in enumerate(content):
            if 'Repodata is over 2 weeks old' in c:
                self.expired_cache = True
            elif c == "Installed Packages":
                break
        return i + 1

    def _get_rows(self, content):
        """
        Yields:
            a list per row of the following form:

            .. code:: python

                [
                    <name.arch>,
                    <[epoch:]version-release>,
                    <repo or @installed-from-repo>
                ]
        """
        start = self._find_start(content)
        if start == len(content):
            raise SkipComponent()

        # join hanging wrapped lines together into a single line.
        # see https://bugzilla.redhat.com/show_bug.cgi?id=584525
        cur = []
        for line in content[start:]:
            if not cur:
                cur.append(line.strip())
            elif line.startswith(" "):
                cur.append(line.strip())
            else:
                yield " ".join(cur).split()
                cur = [line.strip()]

        if cur:
            yield " ".join(cur).split()

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

    def _unknown_row(self, row):
        """
        Heuristic to tell us we've hit the bottom of the Installed
        Packages stanza.
        """
        return len(row) != 3 or row[:2] == ["Loaded", "plugins:"]

    def parse_content(self, content):
        """
        ``yum list installed`` output is basically tabular with an ignorable
        set of rows at the top and a line "Installed Packages" that designates
        the following rows as data. Each column has a maximum width, and if any
        column overflows, the following columns wrap to the next line and
        indent to their usual starting positions. It's also possible for the
        data rows to be followed by more lines that should be ignored. Since
        ``yum list installed`` is for human consumption, the footer lines can be
        syntactically ambiguous with data lines. We use heuristics to check for
        an invalid row to signal the end of data.
        """

        packages = defaultdict(list)
        for row in self._get_rows(content):
            if self._unknown_row(row):
                break
            rec = self._make_record(*row)
            packages[rec["name"]].append(YumInstalledRpm(rec))
        self.packages = dict(packages)
