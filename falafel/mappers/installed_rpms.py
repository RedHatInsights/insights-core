import logging
from falafel.core.plugins import mapper
from falafel.util.rpm import RpmPackage
from falafel.core import MapperOutput

logger = logging.getLogger("rpm")


class RpmPackageList(MapperOutput):

    def get(self, pkg):
        return self.data.get(pkg)

    def __contains__(self, pkg):
        return pkg in self.data


@mapper('installed-rpms')
def installed_rpms(context):
    """
    Returns a RpmPackageList object which contains RpmPackage objects
    --- Usage ---
    rpms = shared.get(installed_rpms)
    if 'yum' in rpms:
        print ...
    yum_pkg = rpms.get('yum')

    if yum_pkg:
        ver = yum_pkg.version
        rel = yum_pkg.release
        nvr = get_package_nvr(yum.pkg.package)
    -------------
    """
    rpms = {}
    for line in context.content:
        line_split = line.split(None, 1)
        try:
            pkg_obj = RpmPackage(line_split[0])
            rpms[pkg_obj.name] = pkg_obj
        except ValueError:
            logger.debug("Error parsing RPM package %s" % line_split[0])
    if rpms:
        return RpmPackageList(rpms)
