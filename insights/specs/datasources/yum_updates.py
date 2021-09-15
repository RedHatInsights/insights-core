"""
Custom datasource for collecting yum updates
"""
import json
import time

from insights import datasource, HostContext, SkipComponent
from insights.components.rhel_version import IsRhel7
from insights.core.spec_factory import DatasourceProvider

sorted_cmp = None
try:
    # cmp_to_key is not available in python 2.6, but it has sorted function which accepts cmp function
    def sorted_cmp(it, cmp):
        from functools import cmp_to_key
        return sorted(it, key=cmp_to_key(cmp))
except ImportError:
    sorted_cmp = sorted


class UpdatesManager:
    """ Performs package resolution on yum based systems """
    def __init__(self):
        import yum

        self.base = yum.YumBase()
        self.base.doGenericSetup(cache=1)
        self.releasever = self.base.conf.yumvar['releasever']
        self.basearch = self.base.conf.yumvar['basearch']
        self.packages = []
        self.repos = []
        self.updict = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

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
        self.base.doSackSetup()
        self.packages = self.base.pkgSack.returnPackages()
        self.repos = self.base.repos.repos
        self._build_updict()

    def _build_updict(self):
        self.updict = {}
        for pkg in self.packages:
            self.updict.setdefault(pkg.na, []).append(pkg)

    def enabled_repos(self):
        return [repo.id for repo in self.base.repos.listEnabled()]

    def installed_packages(self):
        return self.base.rpmdb.returnPackages()

    def updates(self, pkg):
        nevra = pkg.nevra
        updates_list = []
        for upg in self.updict[pkg.na]:
            if upg.verGT(pkg):
                updates_list.append(upg)
        return nevra, updates_list

    @staticmethod
    def pkg_nevra(pkg):
        return "{}-{}:{}-{}.{}".format(pkg.name, pkg.epoch, pkg.version, pkg.release, pkg.arch)

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


@datasource(HostContext, [IsRhel7])
def yum_updates(_broker):
    """
    This datasource provides a list of available updates on the system.
    It uses the yum python library installed locally, and collects list of
    available package updates, along with advisory info where applicable.
    """

    if not _broker.get(IsRhel7):
        raise SkipComponent("Yum updates currently only works on RHEL 7")

    with UpdatesManager() as umgr:
        umgr.load()

        response = {
            "releasever": umgr.releasever,
            "basearch": umgr.basearch,
            "update_list": {},
        }

        data = {'package_list': umgr.installed_packages()}
        updates = {}
        for pkg in data["package_list"]:
            (nevra, updates_list) = umgr.updates(pkg)
            updates[nevra] = updates_list
            for (nevra, update_list) in updates.items():
                if update_list:
                    out_list = []
                    for pkg in umgr.sorted_pkgs(update_list):
                        pkg_dict = {
                            "package": umgr.pkg_nevra(pkg),
                            "repository": umgr.pkg_repo(pkg),
                            "basearch": response["basearch"],
                            "releasever": response["releasever"],
                        }
                        erratum = umgr.advisory(pkg)
                        if erratum:
                            pkg_dict["erratum"] = erratum
                        out_list.append(pkg_dict)
                    response["update_list"][nevra] = {"available_updates": out_list}

        ts = umgr.last_update()
        if ts:
            response["metadata_time"] = time.strftime("%FT%TZ", time.gmtime(ts))
    return DatasourceProvider(content=json.dumps(response), relative_path='insights_commands/yum_updates_list')
