"""
JBoss version
=============
Provide information about the versions of all running Jboss on a system.
"""
import json

from collections import namedtuple
from insights import Parser, parser
from insights.specs import Specs

# define namedtuple to store the property of version
_VersionNameTuple = namedtuple("_VersionNameTuple", ["file_path", "product", "version", "code_name", "major", "minor", "release"])


def _get_version_tuple(version_line, i_file_path):
    """
    Perform the version line parsing, returning a nametuple of the values of one jboss version
    """
    product, _, version_name = [v.strip() for v in version_line.partition("- Version")]
    if " GA" in version_name:
        # handle Red Hat JBoss Web Server - Version 5.6 GA
        version = version_name.split(' GA')[0]
        code_name = "GA"
        updated_version = version + ".0"
        major, minor, release = updated_version.split('.')[0:3]
    else:
        # add empty code name for Red Hat Data Grid - Version 7.3.0
        version_name = version_name.strip() + "."
        major, minor, release, code_name = version_name.split(".")[0:4]
        version = '.'.join([major, minor, release])

    return _VersionNameTuple(i_file_path, product, version, code_name, int(major), int(minor), int(release))


@parser(Specs.jboss_version)
class JbossVersion(Parser):
    """
    This class is to access to file ``$JBOSS_HOME/version.txt``

    Typical content of file ``$JBOSS_HOME/version.txt`` is::

        Red Hat JBoss Enterprise Application Platform - Version 6.4.3.GA

    This class parses the file content and stores data in the dict ``self.parsed``.
    The version info can also be got via ``obj.major`` and ``obj.minor``, etc.

    Examples:
        >>> jboss_version.file_path
        '/home/test/jboss/jboss-eap-6.4/version.txt'
        >>> jboss_version.raw
        'Red Hat JBoss Enterprise Application Platform - Version 6.4.3.GA'
        >>> jboss_version.major
        6
        >>> jboss_version.minor
        4
        >>> jboss_version.release
        3
        >>> jboss_version.version
        '6.4.3'
        >>> jboss_version.code_name
        'GA'
    """

    def parse_content(self, content):
        self.raw = content[0]
        self._parsed = _get_version_tuple(content[0], self.file_path)

    @property
    def product(self):
        """string: the version of this running JBoss progress."""
        return self._parsed.product

    @property
    def version(self):
        """string: the version of this running JBoss progress."""
        return self._parsed.version

    @property
    def major(self):
        """int: the major version of this running JBoss progress."""
        return self._parsed.major

    @property
    def minor(self):
        """int: the minor version of this running JBoss progress."""
        return self._parsed.minor

    @property
    def release(self):
        """int: release of this running JBoss progress."""
        return self._parsed.release

    @property
    def code_name(self):
        """string: code name of this running JBoss progress."""
        return self._parsed.code_name


@parser(Specs.jboss_runtime_versions)
class JbossRuntimeVersions(Parser, list):
    """
     This class is to access to file ``data/insights_commands/jboss_versions``

     Typical content of file ``data/insights_commands/jboss_versions`` is::

         {"/opt/jboss-datagrid-7.3.0-server": "Red Hat Data Grid - Version 7.3.0"}

     This class parses the file content and stores data in the list.

     Examples:
         >>> len(all_jboss_versions)
         1
         >>> all_jboss_versions[0].major
         7
         >>> all_jboss_versions[0].minor
         3
         >>> all_jboss_versions[0].release
         0
     """

    def parse_content(self, content):
        jboss_version_dict = json.loads(' '.join(content))
        for j_path, version_content in jboss_version_dict.items():
            lines = version_content.strip().splitlines()
            self.append(_get_version_tuple(lines[0], j_path))
