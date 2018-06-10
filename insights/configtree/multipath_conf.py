#!/usr/bin/env python
"""
This module models nginx configuration as a tree. It correctly handles include
directives by splicing individual document trees into their parents and
flattening the final structure into one document.

A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
from insights import parser, run
from insights.configtree import ConfigParser
from insights.configtree.dictlike import parse_doc
from insights.specs import Specs


@parser(Specs.multipath_conf)
class MultipathConf(ConfigParser):
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self, line_end="\n")


def get_conf(root=None):
    return run(MultipathConf, root=root).get(MultipathConf)
