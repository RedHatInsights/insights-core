"""
SapHanaPython - Commands
========================

Shared parser for parsing output of the SAP HANA python support scripts.

The following parsers are included in this module:

HanaLandscape - landscapeHostConfiguration.py
---------------------------------------------
"""
from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs


class SapHanaPython(CommandParser, list):
    """
    Base class for parsering the output of SAP HANA python support scripts.

    Attributes:
        overall_status(bool): The overall host status.

    Raises:
        SkipException: When nothing is parsered.
    """

    def parse_content(self, content):
        self.overall_status = None
        header = True
        keys = []
        for line in content:
            line = line.strip()
            if not line.startswith('|'):
                if line.startswith('overall host status:'):
                    self.overall_status = line.split(':')[-1].strip()
                continue
            # discard the empty head and tail in each line
            lsp = [i.strip() for i in line.split('|')][1:-1]
            if '--' in lsp[0]:
                header = False
                continue
            if header:
                keys = [' '.join(k).strip() for k in zip(keys, lsp)] if keys else lsp
            else:
                self.append(dict(zip(keys, lsp)))

        if len(self) == 0:
            raise SkipException


@parser(Specs.sap_hana_landscape)
class HanaLandscape(SapHanaPython):
    """
    Class for parsing the output of `/usr/sap/<SID>/HDB<nr>/exe/python_support/landscapeHostConfiguration.py` command.

    Typical output of is::

        | Host   | Host   | Host   | Failover | Remove | Storage   | Failover     | Failover     | NameServer  | NameServer  | IndexServer | IndexServer |
        |        | Active | Status | Status   | Status | Partition | Config Group | Actual Group | Config Role | Actual Role | Config Role | Actual Role |
        | ------ | ------ | ------ | -------- | ------ | --------- | ------------ | ------------ | ----------- | ----------- | ----------- | ----------- |
        | node1  | yes    | ok     |          |        |         1 | default      | default      | master 1    | master      | worker      | master      |
        overall host status: ok

    Attributes:
        scale_up(bool): True for 'Scale Up' HANA System
        scale_out(bool): True for 'Scale Out' HANA System

    Examples:
        >>> type(hana_sta)
        <class 'insights.parsers.sap_hana_python_script.HanaLandscape'>
        >>> hana_sta.scale_up
        True
        >>> len(hana_sta)
        1
        >>> hana_sta[0]['Host'] == 'node1'
        True
        >>> hana_sta.overall_status == 'ok'
        True
    """
    def __init__(self, *args, **kwargs):
        super(HanaLandscape, self).__init__(*args, **kwargs)
        self.scale_up = len(self) == 1
        self.scale_out = len(self) > 1
