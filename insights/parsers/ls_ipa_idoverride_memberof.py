"""
LsIPAIdoverrideMemberof - command ``ls -lan /usr/share/ipa/ui/js/plugins/idoverride-memberof``
==============================================================================================

The ``ls -lan /usr/share/ipa/ui/js/plugins/idoverride-memberof`` command provides information for the listing of the
``/usr/share/ipa/ui/js/plugins/idoverride-memberof`` files. See the ``FileListing`` class for a more complete description
of the available features of the class.

Sample ``ls -lan /usr/share/ipa/ui/js/plugins/idoverride-memberof`` output::

    /usr/share/ipa/ui/js/plugins/idoverride-memberof:
    total 0
    drwxr-xr-x. 2 0 0 0 Nov 11 11:44 .
    drwxr-xr-x. 4 0 0 0 Nov 11 11:44 ..
    -rw-rw-r--. 1 0 0 0 Nov 11 11:44 idoverride-memberof.js
    -rw-rw-r--. 1 0 0 0 Nov 11 11:44 idoverride-admemberof.js

Examples:
    >>> '/usr/share/ipa/ui/js/plugins/idoverride-memberof' in ls_ipa_idoverride_memberof
    True
    >>> ls_ipa_idoverride_memberof.files_of('/usr/share/ipa/ui/js/plugins/idoverride-memberof') == ['idoverride-memberof.js', 'idoverride-admemberof.js']
    True
"""

from insights.specs import Specs
from .. import parser, CommandParser, FileListing


@parser(Specs.ls_ipa_idoverride_memberof)
class LsIPAIdoverrideMemberof(CommandParser, FileListing):
    """Parses output of ``ls -lan /usr/share/ipa/ui/js/plugins/idoverride-memberof`` command."""
    pass
