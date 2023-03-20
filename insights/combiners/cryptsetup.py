"""
Cryptsetup - combine metadata about LUKS devices
================================================

Combine outputs of LuksDump and LuksMeta parsers (with the same UUID) into a
single dictionary.
"""

import copy

from insights import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.cryptsetup_luksDump import LuksDump
from insights.parsers.luksmeta import LuksMeta


@combiner(LuksDump, optional=[LuksMeta])
class LuksDevices(list):
    """
    Combiner for LUKS encrypted devices information. It uses the results of
    the ``LuksDump`` and ``LuksMeta`` parser (they are matched based UUID of
    the device they were collected from).


    Examples:
        >>> luks_devices[0]["header"]["Version"]
        '1'
        >>> "luksmeta" in luks_devices[0]
        True
        >>> "luksmeta" in luks_devices[1]
        False
        >>> luks_devices[0]["luksmeta"][0]
        Keyslot on index 0 is 'active' with no embedded metadata
    """

    def __init__(self, luks_dumps, luks_metas):
        luksmeta_by_uuid = {}

        if luks_metas:
            for luks_meta in luks_metas:
                if "device_uuid" not in luks_meta:
                    continue

                luksmeta_by_uuid[luks_meta["device_uuid"].lower()] = luks_meta

        for luks_dump in luks_dumps:
            uuid = luks_dump.dump["header"]["UUID"].lower()
            luks_dump_copy = copy.deepcopy(luks_dump.dump)

            if luks_metas and uuid in luksmeta_by_uuid:
                luks_dump_copy["luksmeta"] = luksmeta_by_uuid[uuid]

            self.append(luks_dump_copy)

        if not self:
            raise SkipComponent
