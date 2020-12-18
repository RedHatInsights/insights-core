"""
PackageProvidesHttpdAll - Combiner for packages which provide httpd
===================================================================

.. warning::

    This module is deprecated, please use
    :mod:`insights.parsers.package_provides` instead.

Combiner for collecting all the running httpd command and the corresponding RPM package name
which is parsed by the PackageProvidesHttpd parser.

"""

from insights.core.plugins import combiner
from insights.parsers.package_provides_httpd import PackageProvidesHttpd
from .. import LegacyItemAccess
from insights.util import deprecated


@combiner(PackageProvidesHttpd)
class PackageProvidesHttpdAll(LegacyItemAccess):
    """
    .. warning::

        This Combiner is deprecated, please use
        :class:`insights.parsers.package_provides.PackageProvidesCommand`
        Parsers instead.

    This combiner will receive a list of parsers named PackageProvidesHttpd, one for each running instance of httpd
    and each parser instance will contain the command information and the RPM package information.
    It works as a ``dict`` with the httpd command information as the key and the
    corresponding RPM package information as the value.

    Examples:
        >>> sorted(packages.running_httpds)
        ['/opt/rh/httpd24/root/usr/sbin/httpd', '/usr/sbin/httpd']
        >>> packages.get_package("/usr/sbin/httpd")
        'httpd-2.4.6-88.el7.x86_64'
        >>> packages.get("/opt/rh/httpd24/root/usr/sbin/httpd")
        'httpd24-httpd-2.4.34-7.el7.x86_64'
        >>> packages["/usr/sbin/httpd"]
        'httpd-2.4.6-88.el7.x86_64'

    """

    def __init__(self, package_provides_httpd):
        deprecated(
            PackageProvidesHttpdAll,
            'Please use the :class:`insights.parsers.package_provides.PackageProvidesCommand` instead.'
        )
        self.data = {}
        for pkg in package_provides_httpd:
            self.data[pkg.command] = pkg.package
        super(PackageProvidesHttpdAll, self).__init__()

    @property
    def running_httpds(self):
        """
        Returns the list of httpd commands which are running on the system.
        """
        return list(self.data.keys())

    def get_package(self, httpd_command):
        """
        Returns the installed httpd package that provides the specified `httpd_command`.

        Parameters:
            httpd_command (str): The specified httpd command, e.g. found in ``ps`` command.

        Returns:
            (str): The package that provides the httpd command.
        """

        return self.data.get(httpd_command)

    @property
    def packages(self):
        """
        Returns the list of corresponding httpd RPM packages which are running on the system.
        """
        return list(self.data.values())
