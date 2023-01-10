"""
JBoss version
=============
Provide information about the versions of all running Jboss on a system.
"""

import json

from insights import Parser, parser
from insights.specs import Specs
from insights.core.context import Context


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
        product, _, version_name = [v.strip() for v in content[0].partition("- Version")]
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
        self._parsed = {
            "product": product,
            "version": version,
            "code_name": code_name,
            "major": int(major),
            "minor": int(minor),
            "release": int(release)
        }

    @property
    def product(self):
        """string: the version of this running JBoss progress."""
        return self._parsed["product"]

    @property
    def version(self):
        """string: the version of this running JBoss progress."""
        return self._parsed["version"]

    @property
    def major(self):
        """int: the major version of this running JBoss progress."""
        return self._parsed["major"]

    @property
    def minor(self):
        """int: the minor version of this running JBoss progress."""
        return self._parsed["minor"]

    @property
    def release(self):
        """int: release of this running JBoss progress."""
        return self._parsed["release"]

    @property
    def code_name(self):
        """string: code name of this running JBoss progress."""
        return self._parsed["code_name"]


@parser(Specs.jboss_runtime_versions)
class JbossRuntimeVersions(Parser):
    """
     This class is to access to file ``data/insights_commands/jboss_versions``

     Typical content of file ``data/insights_commands/jboss_versions`` is::

         {"/opt/jboss-datagrid-7.3.0-server": "Red Hat Data Grid - Version 7.3.0"}

     This class parses the file content and stores data in the dict ``self.versions``.

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
        self._versions = []
        jboss_version_dict = json.loads(' '.join(content))
        for j_path, version_content in jboss_version_dict.items():
            lines = version_content.strip().splitlines()
            new_context = Context(content=lines, path=j_path)
            self._versions.append(JbossVersion(new_context))
        self._iterVersions = iter(self._versions)

    def __len__(self):
        return len(self._versions)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._iterVersions)

    next = __next__   # For Python 2

    def __getitem__(self, item):
        return self._versions[item]
