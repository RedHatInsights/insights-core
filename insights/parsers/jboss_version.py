#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
JBoss version - File ``$JBOSS_HOME/version.txt``
================================================

This module provides plugins access to file ``$JBOSS_HOME/version.txt``

Typical content of file ``$JBOSS_HOME/version.txt`` is::

    Red Hat JBoss Enterprise Application Platform - Version 6.4.3.GA

This module parses the file content and stores data in the dict ``self.parsed``.
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
from .. import Parser, parser
from ..specs import Specs


@parser(Specs.jboss_version)
class JbossVersion(Parser):
    """Parses the content of file ``$JBOSS_HOME/version.txt``."""

    def parse_content(self, content):
        self.raw = content[0]
        product, _, version_name = [v.strip() for v in content[0].partition("- Version")]
        version, code_name = version_name.strip().rsplit(".", 1)
        major, minor, release = version.split(".")
        self.parsed = {
            "product": product,
            "version": version,
            "code_name": code_name,
            "major": int(major),
            "minor": int(minor),
            "release": int(release)
        }

    @property
    def version(self):
        """string: the version of this running JBoss progress."""
        return self.parsed["version"]

    @property
    def major(self):
        """int: the major version of this running JBoss progress."""
        return self.parsed["major"]

    @property
    def minor(self):
        """int: the minor version of this running JBoss progress."""
        return self.parsed["minor"]

    @property
    def release(self):
        """int: release of this running JBoss progress."""
        return self.parsed["release"]

    @property
    def code_name(self):
        """string: code name of this running JBoss progress."""
        return self.parsed["code_name"]
