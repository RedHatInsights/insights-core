"""
CloudInit
=========

Parsers related to "cloud-init" can be placed in this module.

CloudInitQuery - cmd `cloud-init query -f '{{ cloud_name, platform }}'`
-----------------------------------------------------------------------
"""

from insights import CommandParser, parser
from insights.core.exceptions import SkipComponent
from insights.specs import Specs


@parser(Specs.cloud_init_query)
class CloudInitQuery(CommandParser):
    """
    Parse the ``cloud-init query -f '{{ cloud_name, platform }}'`` output.

    Sample input::

        ('azure', 'azure')

    Examples:
        >>> cloud_query.cloud_name == 'azure'
        True
        >>> cloud_query.platform == 'azure'
        True
    """

    def parse_content(self, content):
        try:
            if (
                len(content) == 1
                and content[0][0] == '('
                and content[0][-1] == ')'
                and ', ' in content[0]
            ):
                line = content[0].strip("()")
                self.cloud_name, self.platform = [
                    v.lstrip('u').strip('\'"') for v in line.split(', ')
                ]
            else:
                raise
        except Exception:
            raise SkipComponent("Invalid content: '{0}'".format(content))
