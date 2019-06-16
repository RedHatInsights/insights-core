#!/usr/bin/env python
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
NginxConfTree - Combiner for nginx configuration
=======================================================
This module models nginx configuration as a tree. It correctly handles include
directives by splicing individual document trees into their parents until one
document tree is left.

A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
import os
from insights import combiner, parser, run
from insights.core import ConfigCombiner, ConfigParser
from insights.configtree import eq
from insights.configtree.dictlike import parse_doc
from insights.specs import Specs


@parser(Specs.nginx_conf)
class _NginxConf(ConfigParser):
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)


@combiner(_NginxConf)
class NginxConfTree(ConfigCombiner):
    """
    Exposes nginx configuration through the configtree interface.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, confs):
        super(NginxConfTree, self).__init__(confs, "nginx.conf", eq("include"))

    @property
    def conf_path(self):
        return os.path.dirname(self.main.file_path)


def get_tree(root=None):
    """
    This is a helper function to get an nginx configuration component for your
    local machine or an archive. It's for use in interactive sessions.
    """
    return run(NginxConfTree, root=root).get(NginxConfTree)


if __name__ == "__main__":
    run(NginxConfTree, print_summary=True)
