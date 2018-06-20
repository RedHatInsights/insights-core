#!/usr/bin/env python
"""
This module models nginx configuration as a tree. It correctly handles include
directives by splicing individual document trees into their parents until one
document tree is left.

A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
import os
import six
from insights.contrib.ipaddress import ip_address, ip_network
from insights import combiner, parser, run
from insights.core import ConfigCombiner, ConfigParser
from insights.configtree import eq, BinaryBool, UnaryBool
from insights.configtree.dictlike import parse_doc
from insights.specs import Specs


@parser(Specs.nginx_conf)
class _NginxConf(ConfigParser):
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)


@combiner(_NginxConf)
class NginxConfTree(ConfigCombiner):
    def __init__(self, confs):
        super(NginxConfTree, self).__init__(confs, "nginx.conf", eq("include"))

    @property
    def conf_path(self):
        return os.path.dirname(self.main.file_path)


def get_tree(root=None):
    return run(NginxConfTree, root=root).get(NginxConfTree)


is_private = UnaryBool(lambda xs: any(ip_address(six.u(x)).is_private for x in xs))
in_network = BinaryBool(lambda x, y: (ip_address(six.u(x)) in ip_network(six.u(y))))


if __name__ == "__main__":
    run(NginxConfTree, print_summary=True)
