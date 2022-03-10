"""
Custom datasource for collecting yum updates
"""
import json
import time

from insights import datasource, HostContext, SkipComponent
from insights.components.rhel_version import IsRhel7, IsRhel8, IsRhel9
from insights.core.spec_factory import DatasourceProvider
from distutils.version import LooseVersion as version

try:
    from functools import cmp_to_key

    # cmp_to_key is not available in python 2.6, but it has sorted function which accepts cmp function
    def sorted_cmp(it, cmp):
        return sorted(it, key=cmp_to_key(cmp))
except ImportError:
    sorted_cmp = sorted


class DnfManager:
    """ Performs package resolution on dnf based systems """
    def __init__(self):
        self.base = dnf.base.Base()
        self.releasever = dnf.rpm.detect_releasever("/")
        self.basearch = dnf.rpm.basearch(hawkey.detect_arch())
        self.packages = []
        self.repos = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    @staticmethod
    def pkg_cmp(a, b):
        if a.name != b.name:
            return -1 if a.name < b.name else 1
        vercmp = rpm.labelCompare((str(a.e), a.v, a.r), (str(b.e), b.v, b.r))
        if vercmp != 0:
            return vercmp
        if a.reponame != b.reponame:
            return -1 if a.reponame < b.reponame else 1
        return 0

    def sorted_pkgs(self, pkgs):
        # if package is installed more than once (e.g. kernel)
        # don't report other installed (i.e. with @System repo) as updates
        return sorted_cmp([pkg for pkg in pkgs if pkg.reponame != "@System"], self.pkg_cmp)

    def load(self):
        self.base.conf.read()
        self.base.conf.cacheonly = True
        self.base.read_all_repos()
        self.packages = hawkey.Query(hawkey.Sack())
        if version(dnf.VERSION) >= version("4.7.0"):
            try:
                # do not use standard self.base.fill_sack() it does not respect cacheonly
                self.base.fill_sack_from_repos_in_cache(load_system_repo=True)
                self.packages = self.base.sack.query()
            except dnf.exceptions.RepoError:
                # RepoError is raised when cache is empty
                pass
        self.repos = self.base.repos

    def installed_packages(self):
        return self.packages.installed().run()

    def updates(self, pkg):
        name = pkg.name
        evr = "{0}:{1}-{2}".format(pkg.epoch, pkg.version, pkg.release)
        arch = pkg.arch
        nevra = "{0}-{1}.{2}".format(name, evr, arch)
        updates_list = []
        for upd in self.packages.filter(name=name, arch=arch, evr__gt=evr):
            updates_list.append(upd)
        return nevra, updates_list

    @staticmethod
    def pkg_nevra(pkg):
        return "{0}-{1}:{2}-{3}.{4}".format(pkg.name, pkg.epoch, pkg.version, pkg.release, pkg.arch)

    @staticmethod
    def pkg_repo(pkg):
        return pkg.reponame

    @staticmethod
    def advisory(pkg):
        errata = pkg.get_advisories(hawkey.EQ)
        return errata[0].id if len(errata) > 0 else None

    def last_update(self):
        last_ts = 0
        for repo in self.base.repos.iter_enabled():
            repo_ts = repo._repo.getTimestamp()
            if repo_ts > last_ts:
                last_ts = repo_ts
        return last_ts


class YumManager(DnfManager):
    """ Performs package resolution on yum based systems """
    def __init__(self):
        self.base = yum.YumBase()
        self.base.doGenericSetup(cache=1)
        self.releasever = self.base.conf.yumvar['releasever']
        self.basearch = self.base.conf.yumvar['basearch']
        self.packages = []
        self.repos = []
        self.updict = {}

    @staticmethod
    def pkg_cmp(a, b):
        vercmp = a.verCMP(b)
        if vercmp != 0:
            return vercmp
        if a.repoid != b.repoid:
            return -1 if a.repoid < b.repoid else 1
        return 0

    def sorted_pkgs(self, pkgs):
        return sorted_cmp(pkgs, self.pkg_cmp)

    def load(self):
        self.base.doRepoSetup()
        try:
            self.base.doSackSetup()
            self.packages = self.base.pkgSack.returnPackages()
        except yum.Errors.RepoError:
            # RepoError is raised when cache is empty
            pass
        self.repos = self.base.repos.repos
        self._build_updict()

    def _build_updict(self):
        self.updict = {}
        for pkg in self.packages:
            self.updict.setdefault(pkg.na, []).append(pkg)

    def installed_packages(self):
        return self.base.rpmdb.returnPackages()

    def updates(self, pkg):
        nevra = pkg.nevra
        updates_list = []
        for upg in self.updict.get(pkg.na, []):
            if upg.verGT(pkg):
                updates_list.append(upg)
        return nevra, updates_list

    @staticmethod
    def pkg_repo(pkg):
        return pkg.repoid

    def advisory(self, pkg):
        adv = self.base.upinfo.get_notice(pkg.nvr)
        if adv:
            return adv.get_metadata()['update_id']
        return None

    @staticmethod
    def last_update():
        return 0


# Select which manager to use based on the available system libraries.
try:
    import dnf
    import hawkey
    import rpm
    UpdatesManager = DnfManager
except ImportError:
    try:
        import yum
        UpdatesManager = YumManager
    except ImportError:
        UpdatesManager = None


@datasource(HostContext, [IsRhel7, IsRhel8, IsRhel9])
def yum_updates(_broker):
    """
    This datasource provides a list of available updates on the system.
    It uses the yum python library installed locally, and collects list of
    available package updates, along with advisory info where applicable.

    Sample data returned::

        {
          "releasever": "8",
          "basearch": "x86_64",
          "update_list": {
            "NetworkManager-1:1.22.8-4.el8.x86_64": {
              "available_updates": [
                {
                  "package": "NetworkManager-1:1.22.8-5.el8_2.x86_64",
                  "repository": "rhel-8-for-x86_64-baseos-rpms",
                  "basearch": "x86_64",
                  "releasever": "8",
                  "erratum": "RHSA-2020:3011"
                }
              ]
            }
          },
          "metadata_time": "2021-01-01T09:39:45Z"
        }

    Returns:
        list: List of available updates
    Raises:
        SkipComponent: Raised when neither dnf nor yum is found
    """
    if UpdatesManager is None:
        raise SkipComponent()

    with UpdatesManager() as umgr:
        umgr.load()

        response = {
            "releasever": umgr.releasever,
            "basearch": umgr.basearch,
            "update_list": {},
        }

        for pkg in umgr.installed_packages():
            nevra, updates_list = umgr.updates(pkg)
            if updates_list:
                out_list = []
                update_list = umgr.sorted_pkgs(updates_list)

                for p in update_list:
                    pkg_dict = {
                        "package": umgr.pkg_nevra(p),
                        "repository": umgr.pkg_repo(p),
                        "basearch": response["basearch"],
                        "releasever": response["releasever"],
                    }

                    erratum = umgr.advisory(p)
                    if erratum:
                        pkg_dict["erratum"] = erratum

                    out_list.append(pkg_dict)

                response["update_list"][nevra] = {"available_updates": out_list}

        ts = umgr.last_update()
        if ts:
            response["metadata_time"] = time.strftime("%FT%TZ", time.gmtime(ts))

    return DatasourceProvider(content=json.dumps(response), relative_path='insights_commands/yum_updates_list')
