"""
This module provides the version of Ansible Tower intalled.

Attributes::

    version (string): Ansible Tower version string i.e. "3.4.1"
"""
from insights.specs import Specs
from insights import Parser, parser


@parser(Specs.tower_version)
class TowerVersion(Parser):
    def parse_content(self, content):
        # TODO: break up the versoin into major, minor
        self.version = "".join(content).strip()

