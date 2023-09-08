"""
Custom datasource for collecting yum updates
"""
import json
import logging
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
    def __init__(self, build_pkgcache=False):
        self.base = dnf.base.Base()
        self.base.conf.cacheonly = not build_pkgcache
        # releasever and basearchs are correctly set after calling load()
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
        logging.disable(logging.WARNING)
        cli = dnf.cli.Cli(self.base)
        cli._read_conf_file()
        subst = self.base.conf.substitutions
        if subst.get("releasever"):
            self.releasever = subst["releasever"]
        if subst.get("basearch"):
            self.basearch = subst["basearch"]

        self.base.read_all_repos()

        self.packages = hawkey.Query(hawkey.Sack())
        try:
            if version(dnf.VERSION) >= version("4.7.0") and self.base.conf.cacheonly:
                self.base.fill_sack_from_repos_in_cache(load_system_repo=True)
                self.packages = self.base.sack.query()
            elif not self.base.conf.cacheonly:
                self.base.fill_sack()
                self.packages = self.base.sack.query()
        except dnf.exceptions.RepoError:
            # RepoError is raised when cache is empty
            pass

        self.repos = self.base.repos
        logging.disable(logging.NOTSET)

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
    def sorted_advisories(pkg):
        advisories = pkg.get_advisories(hawkey.EQ)
        if advisories:
            advisories_ids = map(lambda advisory: advisory.id, advisories)
            return sorted(advisories_ids)
        return []

    def last_update(self):
        last_ts = 0
        for repo in self.base.repos.iter_enabled():
            repo_ts = repo._repo.getTimestamp()
            if repo_ts > last_ts:
                last_ts = repo_ts
        return last_ts


class YumManager(DnfManager):
    """ Performs package resolution on yum based systems """
    def __init__(self, build_pkgcache=False):
        self.base = yum.YumBase()
        self.base.doGenericSetup(cache=0 if build_pkgcache else 1)
        self.releasever = self.base.conf.yumvar['releasever']
        self.basearch = self.base.conf.yumvar['basearch']
        self.naevr_to_repo = {}
        self.pkg_tup_to_advisories = {}

    @staticmethod
    def pkg_cmp(a_tup, b_tup):
        a_n, a_a, a_e, a_v, a_r = a_tup[0]
        b_n, b_a, b_e, b_v, b_r = b_tup[0]
        a_repoid = a_tup[1]
        b_repoid = b_tup[1]

        if a_n != b_n:
            return -1 if a_n < b_n else 1
        vercmp = rpmUtils.miscutils.compareEVR((a_e, a_v, a_r,), (b_e, b_v, b_r,))
        if vercmp != 0:
            return vercmp
        if a_repoid != b_repoid:
            return -1 if a_repoid < b_repoid else 1
        return 0

    def sorted_pkgs(self, pkg_tups):
        # Sorting on top of array of naevr tuple [(n,a,e,v,r), repo_id]
        return sorted_cmp(pkg_tups, self.pkg_cmp)

    def load(self):
        try:
            self.base.doRepoSetup()
            self.base.doSackSetup()
        except yum.Errors.RepoError:
            # RepoError is raised when cache is empty
            pass
        except AttributeError:
            # backwards compatibility, because yum is removing these setup functions in future
            # and moving the setups to be getters (https://github.com/rpm-software-management/yum/blob/master/yum/__init__.py#L1099)
            pass

        try:
            pkgs = self.base.pkgSack.returnPackages()
            for pkg in pkgs:
                naevr = (pkg.name, pkg.arch, pkg.epoch, pkg.version, pkg.release,)
                self.naevr_to_repo.setdefault(naevr, set()).add(pkg.repoid)
        except yum.Errors.RepoError:
            # RepoError is raised when cache is empty
            pass

    def installed_packages(self):
        return self.base.rpmdb.returnPackages()

    def updates(self, pkg):
        updates = self.base.upinfo.get_applicable_notices((pkg.name, pkg.arch, pkg.epoch, pkg.version, pkg.release,))
        updates_list = set()
        # updates are returnes in format [((name, arch, epoch, version, release), UpdateNotice)]
        for naevr, update_notice in updates:
            for repoid in self.naevr_to_repo[naevr]:
                # pkg_tup is composed from ((n,a,e,v,r), repoid)
                pkg_tup = (naevr, repoid,)
                update_id = update_notice.get_metadata().get("update_id")
                if update_id:
                    self.pkg_tup_to_advisories.setdefault(pkg_tup, set()).add(update_id)
                updates_list.add(pkg_tup)
        return pkg.nevra, updates_list

    @staticmethod
    def pkg_nevra(pkg_tup):
        # tuple of [(n,a,e,v,r), repo_id] -> nevra
        naevr = pkg_tup[0]
        return "{0}-{1}:{2}-{3}.{4}".format(naevr[0], naevr[2], naevr[3], naevr[4], naevr[1])

    @staticmethod
    def pkg_repo(pkg_tup):
        return pkg_tup[1]

    def sorted_advisories(self, pkg_tup):
        advisories = self.pkg_tup_to_advisories.get(pkg_tup, set())
        return sorted(advisories)

    @staticmethod
    def last_update():
        return 0


# Select which manager to use based on the available system libraries.
try:
    import dnf
    import dnf.cli
    import hawkey
    import rpm
    UpdatesManager = DnfManager
except ImportError:
    try:
        import yum
        import rpmUtils.miscutils
        UpdatesManager = YumManager
    except ImportError:
        UpdatesManager = None


@datasource(HostContext, [IsRhel7, IsRhel8, IsRhel9], timeout=0)
def yum_updates(broker):
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
          "build_pkgcache": false,
          "metadata_time": "2021-01-01T09:39:45Z"
        }

    Returns:
        list: List of available updates
    Raises:
        SkipComponent: Raised when neither dnf nor yum is found
    """
    if UpdatesManager is None:
        raise SkipComponent()

    build_pkgcache = getattr(broker.get('client_config', object), 'build_packagecache', False)

    with UpdatesManager(build_pkgcache=build_pkgcache) as umgr:
        umgr.load()

        response = {
            "releasever": umgr.releasever,
            "basearch": umgr.basearch,
            "update_list": {},
            "build_pkgcache": build_pkgcache,
        }

        for pkg in umgr.installed_packages():
            nevra, updates_list = umgr.updates(pkg)
            if updates_list:
                out_list = []
                updates_list = umgr.sorted_pkgs(updates_list)

                for p in updates_list:
                    pkg = {
                        "package": umgr.pkg_nevra(p),
                        "repository": umgr.pkg_repo(p),
                        "basearch": response["basearch"],
                        "releasever": response["releasever"],
                    }

                    advisories = umgr.sorted_advisories(p)
                    if advisories:
                        for advisory in advisories:
                            pkg_errata = pkg.copy()
                            pkg_errata["erratum"] = advisory
                            out_list.append(pkg_errata)
                    else:
                        out_list.append(pkg)

                response["update_list"][nevra] = {"available_updates": out_list}

        ts = umgr.last_update()
        if ts:
            response["metadata_time"] = time.strftime("%FT%TZ", time.gmtime(ts))

    return DatasourceProvider(content=json.dumps(response), relative_path='insights_commands/yum_updates_list')
