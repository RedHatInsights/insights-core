"""
subscription-manager commands
=============================

Parsers for parsing output of the ``subscription-manager`` commands.

SubscriptionManagerID - command ``subscription-manager identity``
-----------------------------------------------------------------

SubscriptionManagerFacts - command ``subscription-manager facts``
-----------------------------------------------------------------
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipException
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

add_filter(Specs.subscription_manager_facts, ['instance_id'])


@parser(Specs.subscription_manager_id)
class SubscriptionManagerID(CommandParser):
    """
    Reads the output of `subscription-manager identity` and retrieves the UUID

    Sample output::

        system identity: 00000000-8f8c-4cb1-8023-111111111111
        name: rhel7.localdomain
        org name: 1234567
        org ID: 1234567

    Examples:
        >>> type(rhsm_id)
        <class 'insights.parsers.subscription_manager.SubscriptionManagerID'>
        >>> rhsm_id.id
        '00000000-8f8c-4cb1-8023-111111111111'
    """

    def parse_content(self, content):
        if not content:
            raise SkipException()
        if 'system identity' not in content[0]:
            raise ParseException()

        self.id = content[0].split(":")[-1].strip()

    @property
    def data(self):
        """Provide `self.data` to keep backward compatible."""
        return self.id


@parser(Specs.subscription_manager_facts)
class SubscriptionManagerFacts(CommandParser, dict):
    """
    Class for parsing the output of `subscription-manager facts` command.

    Typical output of the command is::

        aws_instance_id: 567890567890
        network.ipv6_address: ::1
        uname.sysname: Linux
        uname.version: #1 SMP PREEMPT Fri Sep 2 16:07:40 EDT 2022
        virt.host_type: rhev, kvm
        virt.is_guest: True

    Examples:
        >>> type(rhsm_facts)
        <class 'insights.parsers.subscription_manager.SubscriptionManagerFacts'>
        >>> rhsm_facts['aws_instance_id']
        '567890567890'
    """
    def parse_content(self, content):
        for line in content:
            if ': ' not in line:
                raise ParseException('Incorrect line: {0}'.format(line))
            key, val = [_l.strip() for _l in line.split(': ', 1)]
            self[key] = val

        if len(self) == 0:
            raise SkipException
