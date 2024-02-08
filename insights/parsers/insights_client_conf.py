"""
InsightsClientConf - file ``/etc/insights-client/insights-client.conf``
=======================================================================
"""
from insights.core import IniConfigFile, JSONParser
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

# "ros_collect" is added for troubleshooting convenience
add_filter(Specs.insights_client_conf, ["[", "ros_collect"])


@parser(Specs.insights_client_conf)
class InsightsClientConf(IniConfigFile):
    """
    This class provides parsing for the file ``/etc/insights-client/insights-client.conf``.

    Sample input data is in the format::

        [insights-client]
        # Change log level, valid options DEBUG, INFO, WARNING, ERROR, CRITICAL. Default DEBUG
        loglevel=INFO
        # Log each line executed
        trace=False
        # Attempt to auto configure with Satellite server
        auto_config=True
        # Automatically update the dynamic configuration
        auto_update=False
        # Obfuscate IP addresses
        obfuscate=False

    Examples:
        >>> type(conf)
        <class 'insights.parsers.insights_client_conf.InsightsClientConf'>
        >>> conf.sections()
        ['insights-client']
        >>> conf.get("insights-client", "loglevel")
        'INFO'
        >>> conf.getboolean("insights-client", "obfuscate")
        False
    """
    pass


@parser(Specs.basic_auth_insights_client)
class BasicAuthInsightsClient(JSONParser):
    """
    Class for parsing the content of ``basic_conf``.

    Typical content::

        {"username_set": true, "pass_set": true}

    Examples:
        >>> type(basic_conf)
        <class 'insights.parsers.insights_client_conf.BasicAuthInsightsClient'>
        >>> basic_conf['username_set']
        True
    """
    pass
