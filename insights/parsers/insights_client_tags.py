"""
SatelliteYaml - file ``/etc/insights-client/tags.yaml``
=======================================================

Parses the file ``/etc/insights-client/tags.yaml``.
"""

from insights.core.plugins import parser
from insights.core import YAMLParser
from insights.specs import Specs


@parser(Specs.insights_client_tags)
class InsightsClientTags(YAMLParser):
    """
    Sample input::

        group: user_test
        location: Brisbane/Australia
        description:
        - RHEL8
        - qa_env
        security: sensitive

    Examples::

        >>> type(tags_yaml)
        <class 'insights.parsers.insights_client_tags.InsightsClientTags'>
        >>> 'group' in tags_yaml
        True
        >>> tags_yaml['group']
        'user_test'
    """
    pass
