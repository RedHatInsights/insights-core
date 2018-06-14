#!/usr/bin/env python
"""
This module models nginx configuration as a tree. It correctly handles include
directives by splicing individual document trees into their parents and
flattening the final structure into one document.

A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
import os
from insights import combiner, parser, run
from insights.configtree import ConfigCombiner, ConfigParser, eq
from insights.configtree.dictlike import parse_doc
from insights.specs import Specs


@parser(Specs.nginx_conf)
class _NginxConf(ConfigParser):
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)


@combiner(_NginxConf)
class NginxConfAll(ConfigCombiner):
    def __init__(self, confs):
        super(NginxConfAll, self).__init__(confs, "nginx.conf", eq("include"))

    @property
    def conf_path(self):
        return os.path.dirname(self.main.file_path)


def get_conf(root=None):
    return run(NginxConfAll, root=root).get(NginxConfAll)


if __name__ == "__main__":
    run(NginxConfAll, print_summary=True)
