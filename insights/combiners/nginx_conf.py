"""
NginxConfTree - Combiner for nginx configuration
================================================
"""
from insights.core import ConfigCombiner, flatten
from insights.core.plugins import combiner
from insights.parsers.nginx_conf import NginxConfPEG, DockerNginxConfPEG
from insights.parsr.query import eq
import operator
from fnmatch import fnmatch
from os.path import dirname
from insights.parsr.query import Directive, Entry, Result, Section, compile_queries


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


@combiner(DockerNginxConfPEG)
class DockerNginxConfTree(ConfigCombiner):
    """

    """
    def __init__(self, dockernginxconfs):
        all_containers = {}
        self.doc = {}
        for conf in dockernginxconfs:
            container_id = conf.file_name.split("_")[2]
            if container_id in all_containers:
                all_containers[container_id].append(conf)
            else:
                all_containers[container_id] = [conf]
        # print ("9090909090")
        # print (all_containers)

        for id, confs in all_containers.items():
            main = self.find_main(confs, "nginx.conf")
            for conf in confs:
                for node in conf.find(eq("include")):
                    pattern = node.string_value.replace("/", ".")
                    includes = self.find_matches(confs, pattern)
                    for inc in includes:
                        node.children.extend(inc.doc.children)
                        # print ("222222222222222")
                        # print (node)
            self.doc[id] = Entry(children=flatten(main.doc.children, eq("include")))
            # print ("505050505050")
            # print (self.doc)


    def find_matches(self, confs, pattern):
        results = [c for c in confs if fnmatch(c.file_name.split("cat_")[-1], pattern)]
        return sorted(results, key=operator.attrgetter("file_name"))

    def find_main(self, confs, name):
        for c in confs:
            if c.file_name.endswith(name):
                return c



