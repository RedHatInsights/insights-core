"""
subscription-manager commands
=============================

Parsers for parsing output of the ``subscription-manager`` commands.

SubscriptionManagerID - command ``subscription-manager identity``
-----------------------------------------------------------------

SubscriptionManagerFacts - command ``subscription-manager facts``
-----------------------------------------------------------------

SubscriptionManagerStatus - command ``subscription-manager status``
-------------------------------------------------------------------
"""
import uuid

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.specs import Specs

add_filter(
    Specs.subscription_manager_facts, [
        'conversions.activity',
        'image-builder.osbuild-composer.api-type',
        'instance_id',
    ]
)


def _local_kv_split(lines):
    ret = dict()
    for line in lines:
        if ': ' in line:
            key, val = [_l.strip() for _l in line.split(': ', 1)]
            ret[key] = val
    if ret:
        return ret
    raise SkipComponent


@parser(Specs.subscription_manager_id)
class SubscriptionManagerID(CommandParser, dict):
    """
    Reads the output of subscription-manager identity and retrieves the UUID

    Example output::

        system identity: 6655c27c-f561-4c99-a23f-f53e5a1ef311
        name: rhel7.localdomain
        org name: 1234567
        org ID: 1234567

    Examples::
        >>> type(subman_id)
        <class 'insights.parsers.subscription_manager.SubscriptionManagerID'>
        >>> subman_id.identity == '6655c27c-f561-4c99-a23f-f53e5a1ef311'
        True
        >>> subman_id.get('org ID') == '1234567'
        True
        >>> subman_id.uuid == '6655c27c-f561-4c99-a23f-f53e5a1ef311'
        True
    """
    def parse_content(self, content):
        self.update(_local_kv_split(content))

    @property
    def identity(self):
        """Returns the value of 'system identity'."""
        return self.get('system identity')

    @property
    def uuid(self):
        """Returns the value of 'system identity'."""
        if 'system identity' in self:
            return str(uuid.UUID(self.get('system identity')))


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
        self.update(_local_kv_split(content))


@parser(Specs.subscription_manager_status)
class SubscriptionManagerStatus(CommandParser, dict):
    """
    Reads the output of subscription-manager status

    Example output::

        +-------------------------------------------+
           System Status Details
        +-------------------------------------------+
        Overall Status: Disabled
        Content Access Mode is set to Simple Content Access. This host has access to content, regardless of subscription status.

        System Purpose Status: Disabled

    Examples::
        >>> type(subman_status)
        <class 'insights.parsers.subscription_manager.SubscriptionManagerStatus'>
        >>> subman_status['Overall Status'] == 'Disabled'
        True
        >>> subman_status['Content Access Mode'] == 'Simple Content Access'
        True
        >>> subman_status['System Purpose Status'] == 'Disabled'
        True
    """
    def parse_content(self, content):
        for line in content:
            if ': ' in line:
                key, val = [_l.strip() for _l in line.split(': ', 1)]
                self[key] = val
            elif line.startswith('Content Access Mode is set to'):
                self['Content Access Mode'] = line.split('.', 1)[0].split('Content Access Mode is set to')[1].strip()

        if not self:
            raise SkipComponent
