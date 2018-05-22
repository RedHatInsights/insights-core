"""
Tuned-adm - command ``/usr/sbin/tuned-adm active``
==================================================
This parser reads the output of the ``/usr/sbin/tuned-adm active`` command and
reads it into a simple dictionary in the ``data`` property.

Sample data::

    Current active profile: default
    Service tuned: disabled, stopped
    Service ktune: disabled, stopped

Examples::

    >>> 'Service tuned' in tuned_adm_active.data
    True
    >>> tuned_adm_active.data['Service ktune']
    'disabled, stopped'
    >>> tuned_adm_active['Service ktune']
    'disabled, stopped'
"""

from insights.specs import Specs

from .. import LegacyItemAccess
from .. import Parser
from .. import parser
from ..parsers import split_kv_pairs


@parser(Specs.tuned_adm_active)
class TunedAdmActive(LegacyItemAccess, Parser):
    def parse_content(self, content):
        data = {}
        for line in content:
            if 'command not found' in line or 'No such file or directory' in line:
                content = []
                break
        data = split_kv_pairs(content, use_partition=False, split_on=":")
        self.data = dict((k, v) for k, v in data.items() if not v == '')
