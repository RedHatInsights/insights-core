"""
Ceph status commands
====================

This module provides processing for the output of the following ceph related
commands with ``-f json-pretty`` parameter.

CephOsdDump - command ``ceph osd dump -f json-pretty``
------------------------------------------------------

CephOsdDf - command ``ceph osd df -f json-pretty``
--------------------------------------------------

CephS - command ``ceph -s -f json-pretty``
------------------------------------------

CephDfDetail - command ``ceph df detail -f json-pretty``
--------------------------------------------------------

CephHealthDetail - command ``ceph health detail -f json-pretty``
--------------------------------------------------------------------------

CephECProfileGet - command ``ceph osd erasure-code-profile get default -f json-pretty``
---------------------------------------------------------------------------------------

CephCfgInfo - command ``ceph daemon {ceph_socket_files} config show``
---------------------------------------------------------------------

CephOsdTree - command ``ceph osd tree -f json-pretty``
------------------------------------------------------

CephReport - command ``ceph report``
------------------------------------

All these parsers are based on a shared class which processes the JSON
information into a dictionary.
"""
import json

from insights.core import CommandParser, JSONParser, LegacyItemAccess
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ceph_osd_dump)
class CephOsdDump(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph osd dump -f json-pretty``.

    Examples:

    >>> type(ceph_osd_dump)
    <class 'insights.parsers.ceph_cmd_json_parsing.CephOsdDump'>
    >>> ceph_osd_dump['pools'][0]['min_size']
    2
    """
    pass


@parser(Specs.ceph_osd_df)
class CephOsdDf(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph osd df -f json-pretty``.

    Examples:

    >>> type(ceph_osd_df)
    <class 'insights.parsers.ceph_cmd_json_parsing.CephOsdDf'>
    >>> ceph_osd_df['nodes'][0]['pgs']
    945
    """
    pass


@parser(Specs.ceph_s)
class CephS(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph -s -f json-pretty``.

    Examples:

    >>> type(ceph_s)
    <class 'insights.parsers.ceph_cmd_json_parsing.CephS'>
    >>> ceph_s['pgmap']['pgs_by_state'][0]['state_name'] == 'active+clean'
    True
    """
    pass


@parser(Specs.ceph_df_detail)
class CephDfDetail(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph df detail -f json-pretty``.

    Examples:

    >>> type(ceph_df_detail)
    <class 'insights.parsers.ceph_cmd_json_parsing.CephDfDetail'>
    >>> ceph_df_detail['stats']['total_avail_bytes']
    16910123008
    """
    pass


@parser(Specs.ceph_health_detail)
class CephHealthDetail(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph health detail -f json-pretty``.

    Examples:

    >>> type(ceph_health_detail)
    <class 'insights.parsers.ceph_cmd_json_parsing.CephHealthDetail'>
    >>> ceph_health_detail["overall_status"] ==   'HEALTH_OK'
    True
    """
    pass


@parser(Specs.ceph_osd_ec_profile_get)
class CephECProfileGet(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph osd erasure-code-profile get default -f json-pretty``.

    Examples:

    >>> type(ceph_osd_ec_profile_get)
    <class 'insights.parsers.ceph_cmd_json_parsing.CephECProfileGet'>
    >>> ceph_osd_ec_profile_get['k'] == '2'
    True
    """
    pass


@parser(Specs.ceph_config_show)
class CephCfgInfo(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph daemon .. config show``

    Examples:

    >>> type(ceph_cfg_info)
    <class 'insights.parsers.ceph_cmd_json_parsing.CephCfgInfo'>
    >>> ceph_cfg_info.max_open_files == '131072'
    True
    """
    @property
    def max_open_files(self):
        """
        str: Return the value of max_open_files
        """
        return self.data["max_open_files"]


@parser(Specs.ceph_osd_tree)
class CephOsdTree(CommandParser, JSONParser):
    """
    Class to parse the output of the command "ceph osd tree -f json-pretty

    Examples:

    >>> type(ceph_osd_tree)
    <class 'insights.parsers.ceph_cmd_json_parsing.CephOsdTree'>
    >>> ceph_osd_tree['nodes'][0]['children']
    [-5, -4, -3, -2]
    """
    pass


@parser(Specs.ceph_report)
class CephReport(CommandParser, LegacyItemAccess):
    """
    Class to parse the output of the command ``ceph report``.

    Examples:
    >>> type(ceph_report_content)
    <class 'insights.parsers.ceph_cmd_json_parsing.CephReport'>
    >>> ceph_report_content["version"] == '12.2.8-52.el7cp'
    True
    """
    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty output.")
        if not content[0].startswith('report ') or len(content) < 10:
            raise ParseException("Invalid Content: ", content[0])

        try:
            self.data = json.loads(''.join(content[1:]))
        except:
            raise ParseException("Could not parse json.", content[1:])
