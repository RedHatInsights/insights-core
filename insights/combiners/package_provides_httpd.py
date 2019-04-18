"""
PackageProvidesHttpdAll - Combiner for packages which provide httpd
===================================================================

Combiner for collecting all the httpd command and the corresponding package name
which is parsed by the PackageProvidesHttpd parser.

"""

from insights.core.plugins import combiner
from insights.parsers.package_provides_httpd import PackageProvidesHttpd
from .. import LegacyItemAccess


@combiner(PackageProvidesHttpd)
class PackageProvidesHttpdAll(LegacyItemAccess):
    """
    Combiner for collecting all the httpd command and the corresponding package
    name which is parsed by the PackageProvidesJava parser.
    It works as a ``dict`` with the httpd command as the key and the
    corresponding package name as the value.

    Examples:
        >>> PACKAGE_COMMAND_MATCH_1 = '''/usr/sbin/httpd httpd-2.4.6-88.el7.x86_64'''
        >>> PACKAGE_COMMAND_MATCH_2 = '''/opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64'''
        >>> pack1 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_1))
        >>> pack2 = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH_2))
        >>> packages = PackageProvidesHttpdAll([pack1, pack2])
        >>> packages.running_httpd
        ['/usr/sbin/httpd',
         '/opt/rh/httpd24/root/usr/sbin/httpd']
        >>> packages.get_package("/usr/sbin/httpd")
        'httpd-2.4.6-88.el7.x86_64'
        >>> packages.get("/opt/rh/httpd24/root/usr/sbin/httpd")
        'httpd24-httpd-2.4.34-7.el7.x86_64'
        >>> packages["/usr/sbin/httpd"]
        'httpd-2.4.6-88.el7.x86_64'

    """

    def __init__(self, package_provides_httpd):
        self.data = {}
        for pkg in package_provides_httpd:
            self.data[pkg.command] = pkg.package
        super(PackageProvidesHttpdAll, self).__init__()

    @property
    def running_httpds(self):
        """
        Returns the list of httpd commands which are running on the system.
        """
        return self.data.keys()

    def get_package(self, httpd_command):
        """
        Returns the installed httpd package that provides the specified `httpd_command`.

        Parameters:
            httpd_command (str): The specified httpd command, e.g. found in ``ps`` command.

        Returns:
            (str): The package that provides the httpd command.
        """

        return self.data.get(httpd_command)
