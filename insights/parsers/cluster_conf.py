"""
ClusterConf - file ``/etc/cluster/cluster.conf``
================================================

Stores a filtered set of lines from the cluster config file.  Because of the
filtering, the content as a whole will not parse as XML.  We use a
:class:`insights.core.LogFileOutput` parser class because, sadly, it's
easiest.
"""
from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.cluster_conf)
class ClusterConf(LogFileOutput):
    """
    Parse the ``/etc/cluster/cluster.conf`` file as a list of lines.  ``get``
    can be used to find lines containing one or more keywords.  Because of
    filters used on this file, we cannot parse this as XML.
    """
    pass
