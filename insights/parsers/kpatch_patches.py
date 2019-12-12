"""
KpatchPatches - report locally stored kpatch patches
====================================================

This parser creates a list of the module names of locally
stored kpatch modules. If no modules are installed, a
ContentException will be raised.

"""

from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.kpatch_patch_files)
class KpatchPatches(CommandParser):
    """
    A parser for getting modules names of locally stored kpatch-patch files.
    """

    def parse_content(self, content):
        # convert dashes to underscores, remove file suffixes, remove duplicates
        self.patches = list(set([p.split('.')[0].replace("-", "_") for p in content]))
