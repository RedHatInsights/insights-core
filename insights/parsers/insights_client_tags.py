"""
InsightsClientTags - file ``/etc/insights-client/tags.yaml``
=======================================================================
"""

from insights import parser
from insights.core import YAMLParser
from insights.specs import Specs


@parser(Specs.insights_client_tags)
class InsightsClientTags(YAMLParser):
    """
    This class parses the YAML-formatted file `/etc/insights-client/tags.yaml`.
    The file is created by the user after running this command:

    `insights-client --group=<group-name>`

    The command above creates the file and adds an initial group tag
    as defined by the `--group` option.
    Other tags are added manually by the user.

    Sample input data:

        group: eastern-sap
        location: Boston
        description:
        - RHEL8
        - SAP
        key 4: value

    Examples:
        >>> type(tags)
        <class 'insights.parsers.insights_client_tags.InsightsClientTags'>
        >>> tags.data
        {'group': 'eastern-sap', 'location': 'Boston', 'description': ['RHEL8', 'SAP'], 'key 4': 'value'}
        >>> tags.group
        'eastern-sap'
        >>> tags.get('location')
        'Boston'
        >>> tags.get('key 1', 'not defined')
        'not defined'
    """

    @property
    def group(self):
        """
        Return value of the group tag or None if the group tag is missing.
        Missing group tag indicates that the `tags.yaml` file was not created
        by the `insights-client` command.
        """
        return self.get('group')
