"""
PcsQuorumStatus - Commands ``pcs quorum status``
================================================
"""
from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException, parse_fixed_table
from insights.specs import Specs


@parser(Specs.pcs_quorum_status)
class PcsQuorumStatus(CommandParser):
    """
    Class for parsing the output of `pcs quorum status` command.

    Typical output of the command is::

        Quorum information
        ------------------
        Date:             Wed Jun 29 13:17:02 2016
        Quorum provider:  corosync_votequorum
        Nodes:            2
        Node ID:          1
        Ring ID:          1/8272
        Quorate:          Yes

        Votequorum information
        ----------------------
        Expected votes:   3
        Highest expected: 3
        Total votes:      3
        Quorum:           2
        Flags:            Quorate Qdevice

        Membership information
        ----------------------
            Nodeid      Votes    Qdevice Name
                 1          1    A,V,NMW node1 (local)
                 2          1    A,V,NMW node2
                 0          1            Qdevice

    Attributes:
        quorum_info (dict): Dicts where keys are the feature name of quorum information and
            values are the corresponding feature value.
        votequorum_info (dict): Dicts where keys are the feature name of votequorum information and
            values are the corresponding feature value.
        membership_info (list): List of dicts where keys are the feature name of each node and
            values are the corresponding feature value.
    Raises:
        SkipException: When input is empty.
        ParseException: When input cannot be parsed.

    Examples:
        >>> type(pcs_quorum_status)
        <class 'insights.parsers.pcs_quorum_status.PcsQuorumStatus'>
        >>> pcs_quorum_status.quorum_info['Node ID']
        '1'
        >>> pcs_quorum_status.votequorum_info['Expected votes']
        '3'
        >>> pcs_quorum_status.membership_info[0]['Name']
        'node1 (local)'
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty content")
        if len(content) < 21 or not ('Quorum information' in content[0] and
                                     'Votequorum information' in content[9] and
                                     'Membership information' in content[17]):
            raise ParseException("Incorrect content: '{0}'".format(content))

        self.quorum_info = {}
        for line in content[2:7]:
            key, value = line.split(':', 1)
            self.quorum_info[key.strip()] = value.strip()

        self.votequorum_info = {}
        for line in content[11:15]:
            key, value = line.split(':', 1)
            self.votequorum_info[key.strip()] = value.strip()

        self.membership_info = parse_fixed_table(content[19:])
