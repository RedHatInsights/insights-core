"""
NginxConfTree - Combiner for nginx configuration
================================================
"""
from insights.core import ConfigCombiner, ContainerConfigCombiner
from insights.core.plugins import combiner
from insights.parsers.nginx_conf import NginxConfPEG, ContainerNginxConfPEG
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


@combiner(ContainerNginxConfPEG)
class ContainerNginxConfTree(list):
    """
    This module models the nginx configuration of the same running containers
    as a tree and wrap the `tree` of containers into a list.
    Within the tree, It correctly handles include directives by splicing
    individual document trees into their parents until one document tree is
    left.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, ctn_confs):
        containers = {}
        for ctn in ctn_confs:
            if ctn.container_id not in containers:
                containers[ctn.container_id] = [ctn]
            else:
                containers[ctn.container_id].append(ctn)

        for ctn_id, confs in containers.items():
            self.append(ContainerConfigCombiner(
                    confs, "nginx.conf", eq("include"),
                    confs[0].engine, confs[0].image, ctn_id))
