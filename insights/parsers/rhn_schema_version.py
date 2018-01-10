"""
rhn_schema_version - Command ``/usr/bin/rhn-schema-version``
============================================================
Parse the output of command ``/usr/bin/rhn-schema-version``.

"""
from .. import parser
from insights.specs import Specs


@parser(Specs.rhn_schema_version)
def rhn_schema_version(context):
    """
    Function to parse the output of command ``/usr/bin/rhn-schema-version``.

    Sample input::

        5.6.0.10-2.el6sat

    Examples:
        >>> db_ver = shared[rhn_schema_version]
        >>> db_ver
        '5.6.0.10-2.el6sat'

    """
    if context.content:
        content = context.content
        if len(content) == 1 and 'No such' not in content[0]:
            ver = content[0].strip()
            if ver:
                return ver
