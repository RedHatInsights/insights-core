"""
PackageProvides - Combiner for packages which provide the specified command
===========================================================================

The following combiners are included in this module:

PackageProvidesHttpdAll - Combiner for packages of Httpd
--------------------------------------------------------
PackageProvidesJavaAll - Combiner for packages of Java
------------------------------------------------------
"""

from insights.core.plugins import combiner
from insights.parsers.package_provides import PackageProvidesHttpd, PackageProvidesJava
from insights.util import deprecated


class PackageProvides(dict):
    """
    Base class to combiner the PackageProvidesCMD parsers.
    """
    def __init__(self, *args):
        super(PackageProvides, self).__init__()

        for pkg in args[0]:
            self.update({pkg.command: pkg.package})

    @property
    def data(self):
        """
        .. warn::
            This is to keep backward compatibility. This combiner works as a
            dict, please use the built-in attributes of `dict` instead.
        """
        deprecated(PackageProvides.data, 'Deprecated, the combiner is a dict now.')
        return self

    @property
    def running_cmds(self):
        """
        Returns the list of the commands of the specific `cmd` running on the system.
        """
        return sorted(self.keys())

    @property
    def packages(self):
        """
        Returns the list of RPM packages of the specific `cmd` running on the system.
        """
        return sorted(self.values())


@combiner(PackageProvidesHttpd)
class PackageProvidesHttpdAll(PackageProvides):
    """
    This combiner will receive a list of
    :py:class:`insights.parsers.package_provides.PackageProvidesHttpd`, one for
    each running instance of httpd and each parser instance will contain the
    command information and the RPM package information.

    It works as a ``dict`` with the httpd command information as the key and
    the corresponding RPM package information as the value.

    Examples:
        >>> httpd_packages.running_httpds
        ['/opt/rh/httpd24/root/usr/sbin/httpd', '/usr/sbin/httpd']
        >>> httpd_packages["/usr/sbin/httpd"]
        'httpd-2.4.6-88.el7.x86_64'
        >>> httpd_packages.get("/opt/rh/httpd24/root/usr/sbin/httpd")
        'httpd24-httpd-2.4.34-7.el7.x86_64'
    """
    @property
    def running_httpds(self):
        """
        Returns the list of httpd commands which are running on the system.
        """
        return self.running_cmds


@combiner(PackageProvidesJava)
class PackageProvidesJavaAll(PackageProvides):
    """
    This combiner will receive a list of
    :py:class:`insights.parsers.package_provides.PackageProvidesJava`, one for
    each running instance of java and each parser instance will contain the
    command information and the RPM package information.

    It works as a ``dict`` with the java command information as the key and
    the corresponding RPM package information as the value.

    Examples:
        >>> java_packages.running_javas
        ['/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java', '/usr/lib/jvm/jre/bin/java']
        >>> java_packages.get("/usr/lib/jvm/jre/bin/java")
        'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'
        >>> java_packages["/usr/lib/jvm/jre/bin/java"]
        'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'
    """
    @property
    def running_javas(self):
        """
        Returns the list of java commands which are running on the system.
        """
        return self.running_cmds
