import re
import pkg_resources
from setuptools import find_packages


class MetaPattern(object):
    """
    The class provides functionality for
    searching key-value pair in long text.

    >>> mp = MetaPattern('Author', 'Red Hat')
    >>> mp.present("This is raw string\nAuthor: Red Hat\nEnd of string")
    True
    >>> mp = MetaPattern('sbrs', ['kernel', 'shell'])
    >>> mp.present('sbrs: shell')
    True
    """

    def __init__(self, key, values):
        if not isinstance(values, list):
            values = [values]
        self.key = key
        self.values = values
        self.set_pattern()

    def set_pattern(self):
        regex_string = r'^({key}): .*({values_str}).*'
        values_str = '|'.join(self.values)
        regex = regex_string.format(key=self.key, values_str=values_str)
        self.pattern = re.compile(regex, re.MULTILINE)

    def present(self, metadata):
        if self.pattern.search(metadata):
            return True

        return False


class InstalledPackage(object):
    """
    The class provides extended functions
    for Distribution class in pkg_resources
    module
    """

    def __init__(self, dist):
        self.package = dist

    def has_metapair(self, meta_pattern):
        """
        See if the given meta_pattern (key-value
        pair) is present in the package's metadata
        """
        metapair_present = False

        pkg_info = self.package.PKG_INFO
        if self.package.has_metadata(pkg_info):
            metadata = self.package.get_metadata(pkg_info)
            metapair_present = meta_pattern.present(metadata)

        return metapair_present

    def list_modules(self):
        """
        List loadable modules in the package
        """
        location = self.package.location
        modules_to_exclude = ["*.tests", "*.tests.*", "tests.*", "tests"]

        modules = find_packages(location, exclude=modules_to_exclude)
        sorted_modules = sorted(modules)
        return sorted_modules

    @classmethod
    def all(cls):
        """
        Give all the installed python packages
        """
        packages = []
        for pkg in pkg_resources.working_set:
            installed_package = cls(pkg)
            packages.append(installed_package)

        return packages

    @classmethod
    def by_metadata(cls, key, values):
        """
        Get a list of packages which have given key-values pair
        in their metadata
        """
        meta_pattern = MetaPattern(key, values)
        all_packages = InstalledPackage.all()

        packages = [pkg for pkg in all_packages if pkg.has_metapair(meta_pattern)]
        return packages


def get_plugin_modules():
    """
    Get a list of loadable modules from the installed
    Insights plugin packages

    A package is an Insights package if it has `insights-rules`
    tag in the `Keywords` metadata
    """
    plugin_packages = InstalledPackage.by_metadata('Keywords', 'insights-rules')

    plugin_modules = []
    for pkg in plugin_packages:
        plugin_modules.extend(pkg.list_modules())

    return plugin_modules
