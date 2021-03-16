"""
InsightsClientConf - file ``/etc/insights-client/insights-client.conf``
=======================================================================

"""
from insights import IniConfigFile, parser, add_filter
from insights.specs import Specs

add_filter(Specs.insights_client_conf, "[")


@parser(Specs.insights_client_conf)
class InsightsClientConf(IniConfigFile):
    """
    This class provides parsing for the file ``/etc/insights-client/insights-client.conf``.

    Sample input data is in the format::

        [insights-client]
        auto_update=False

    See the :class:`insights.core.IniConfigFile` class for examples.
    """
    pass
