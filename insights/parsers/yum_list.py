"""
Yum List Command
================

The parsers contains in this module are:

YumListInstalled - Command ``yum list installed``
-------------------------------------------------

YumListAvailable - Command ``yum list available``
-------------------------------------------------

"""
from collections import defaultdict

from insights import CommandParser, parser, SkipComponent
from insights.specs import Specs
from insights.parsers.installed_rpms import InstalledRpm, RpmList


class YumListRpm(InstalledRpm):
    """
    The same as :py:class:`insights.parsers.installed_rpms.InstalledRpm` but
    with an additional ``.repo`` attribute.
    """
    def __init__(self, data):
        self.repo = None
        """str: yum / dnf repository name, if available."""

        super(YumListRpm, self).__init__(data)


class YumListBase(CommandParser, RpmList):
    """
    Base class for the ``yum list [installed|available]`` commands.  Each line
    is parsed and stored in a ``YumListRpm`` object.

    .. note::

        ``YumListBase`` shares the :py:class:`insights.parsers.installed_rpms.RpmList`
        interface with :py:class:`insights.parsers.installed_rpms.InstalledRpms`.
        The only difference is ``YumListBase`` takes the output of ``yum list`` as
        its source data, and the :py:class:`YumListRpm` instances it produces
        contain a ``.repo`` attribute.
    """

    def __init__(self, context, package_status):
        self.expired_cache = False
        """bool: Indicates if the yum repo cache is expired."""

        self.package_status = package_status
        """str: Indicates if the list is of installed or available packages."""

        super(YumListBase, self).__init__(context)

    def _find_start(self, content):
        for i, c in enumerate(content):
            if 'Repodata is over 2 weeks old' in c:
                self.expired_cache = True
            elif c == self.package_status + " Packages":
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
        Given the fields of a ``yum list`` row, return a dictionary
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
        ``yum list`` output is basically tabular with an ignorable
        set of rows at the top and a line "Installed Packages" that designates
        the following rows as data. Each column has a maximum width, and if any
        column overflows, the following columns wrap to the next line and
        indent to their usual starting positions. It's also possible for the
        data rows to be followed by more lines that should be ignored. Since
        ``yum list`` is for human consumption, the footer lines can be
        syntactically ambiguous with data lines. We use heuristics to check for
        an invalid row to signal the end of data.
        """

        packages = defaultdict(list)
        for row in self._get_rows(content):
            if self._unknown_row(row):
                break
            rec = self._make_record(*row)
            packages[rec["name"]].append(YumListRpm(rec))
        self.packages = dict(packages)


@parser(Specs.yum_list_installed)
class YumListInstalled(YumListBase):
    """
    The ``YumListInstalled`` class parses the output of the ``yum list installed``
    command. Each line is parsed and stored in a ``YumListRpm`` object.

    Sample input data::

        Repodata is over 2 weeks old. Install yum-cron? Or run: yum makecache fast
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
        >>> type(installed_rpms)
        <class 'insights.parsers.yum_list.YumListInstalled'>
        >>> 'GeoIP' in installed_rpms
        True
        >>> installed_rpms.get_max('GeoIP')
        0:GeoIP-1.5.0-11.el7
        >>> installed_rpms.expired_cache
        True
        >>> type(installed_rpms.get_max('GeoIP'))
        <class 'insights.parsers.yum_list.YumListRpm'>
        >>> rpm1 = installed_rpms.get_max('GeoIP')
        >>> rpm1.package == 'GeoIP-1.5.0-11.el7'
        True
        >>> rpm1.nvr == 'GeoIP-1.5.0-11.el7'
        True
        >>> rpm1.source
        >>> rpm1.name
        'GeoIP'
        >>> rpm1.version
        '1.5.0'
        >>> rpm1.release
        '11.el7'
        >>> rpm1.arch
        'x86_64'
        >>> rpm1.epoch
        '0'
        >>> from insights.parsers.yum_list import YumListRpm
        >>> rpm2 = YumListRpm.from_package('GeoIP-1.6.0-11.el7.x86_64')
        >>> rpm1 == rpm2
        False
        >>> rpm1 > rpm2
        False
        >>> rpm1 < rpm2
        True
    """
    def __init__(self, context):
        super(YumListInstalled, self).__init__(context, "Installed")


@parser(Specs.yum_list_available)
class YumListAvailable(YumListBase):
    """
    The ``YumListAvailable`` class parses the output of the ``yum list available``
    command. Each line is parsed and stored in a ``YumListRpm`` object.

    Input and usage examples are identical to ``YumListInstalled`` but with
    "Installed" replaced with "Available" wherever applicable.
    """
    def __init__(self, context):
        super(YumListAvailable, self).__init__(context, "Available")
