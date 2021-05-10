"""
VirtUuidFacts - files ``/etc/rhsm/facts/virt_uuid.facts``
=========================================================

This module provides parsing for the ``/etc/rhsm/facts/virt_uuid.facts`` file.
The ``VirtUuidFacts`` class is based on a shared class which processes the JSON
information into a dictionary.

Sample input data looks like::

    {"virt.uuid": "4546B285-6C41-5D6R-86G5-0BFR4B3625FS", "uname.machine": "x86"}

Examples:

    >>> len(virt_uuid_facts.data)
    2
"""

from insights.specs import Specs

from .. import JSONParser, parser


@parser(Specs.virt_uuid_facts)
class VirtUuidFacts(JSONParser):
    pass
