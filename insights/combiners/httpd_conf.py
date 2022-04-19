"""
Combiner for httpd configurations
=================================

Combiner for parsing part of httpd configurations. It collects all HttpdConf
generated from each configuration file and combines them to expose a
consolidated configuration tree.

.. note::
    At this point in time, you should **NOT** filter the httpd configurations
    to avoid finding directives in incorrect sections.
"""
from insights.core import ConfigCombiner
from insights.core.plugins import combiner
from insights.parsr.query import startswith
from insights.parsers.httpd_conf import HttpdConf, HttpdConfSclHttpd24, HttpdConfSclJbcsHttpd24


@combiner(HttpdConf)
class HttpdConfTree(ConfigCombiner):
    """
    Exposes httpd configuration through the parsr query interface. Correctly
    handles all include directives.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, confs):
        includes = startswith("Include")
        super(HttpdConfTree, self).__init__(confs, "httpd.conf", includes)

    @property
    def conf_path(self):
        res = self.main.find("ServerRoot")
        return res.value if res else "/etc/httpd"


@combiner(HttpdConfSclHttpd24)
class HttpdConfSclHttpd24Tree(ConfigCombiner):
    """
    Exposes httpd configuration Software Collection httpd24 through the parsr query
    interface. Correctly handles all include directives.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, confs):
        includes = startswith("Include")
        super(HttpdConfSclHttpd24Tree, self).__init__(confs, "httpd.conf", includes)

    @property
    def conf_path(self):
        res = self.main.find("ServerRoot")
        return res.value if res else "/opt/rh/httpd24/root/etc/httpd"


@combiner(HttpdConfSclJbcsHttpd24)
class HttpdConfSclJbcsHttpd24Tree(ConfigCombiner):
    """
    Exposes httpd configuration Software Collection jbcs-httpd24 through the parsr query
    interface. Correctly handles all include directives.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, confs):
        includes = startswith("Include")
        super(HttpdConfSclJbcsHttpd24Tree, self).__init__(confs, "httpd.conf", includes)

    @property
    def conf_path(self):
        res = self.main.find("ServerRoot")
        return res.value if res else "/opt/rh/jbcs-httpd24/root/etc/httpd"
