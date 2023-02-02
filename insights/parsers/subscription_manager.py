"""
subscription-manager commands
=============================

Parsers for parsing output of the ``subscription-manager`` commands.

SubscriptionManagerFacts - command ``subscription-manager facts``
-----------------------------------------------------------------
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

add_filter(Specs.subscription_manager_facts, ['instance_id'])


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
            raise SkipComponent
