"""
NginxConfTree - Combiner for nginx configuration
================================================
"""
from insights.core import ConfigCombiner
from insights.core.plugins import combiner
from insights.parsers.nginx_conf import NginxConfPEG
from insights.parsr.query import eq
from os.path import dirname


@combiner(NginxConfPEG)
class NginxConfTree(ConfigCombiner):
    """
    This module models nginx configuration as a tree. It correctly handles include
    directives by splicing individual document trees into their parents until one
    document tree is left.

    A DSL is provided to query the tree through a select function or brackets [].
    The brackets allow a more conventional lookup feel but aren't quite as powerful
    as using select directly.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, confs):
        super(NginxConfTree, self).__init__(confs, "nginx.conf", eq("include"))

    @property
    def conf_path(self):
        return dirname(self.main.file_path)
