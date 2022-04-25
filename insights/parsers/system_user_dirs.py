"""
SystemUserDirs - datasource ``system_user_dirs``
================================================
"""

from insights import JSONParser, parser
from insights.specs import Specs


@parser(Specs.system_user_dirs)
class SystemUserDirs(JSONParser):
    """
    Class for parsing the ``system_user_dirs`` datasource.

    Sample output of this datasource is::

        '{"pcp-testsuite-5.3.3-1.fc33.x86_64": ["/var/lib/pcp/testsuite"]}'

    Examples:

        >>> type(system_user_dirs)
        <class 'insights.parsers.system_user_dirs.SystemUserDirs'>
        >>> system_user_dirs.data
        {'pcp-testsuite-5.3.3-1.fc33.x86_64': ['/var/lib/pcp/testsuite']}
    """
    pass
