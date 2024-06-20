"""
Subscription manager list outputs - command ``subscription-manager list``
=========================================================================

This module provides parsers for various list outputs of ``subscription-manager``.

Parsers provided by this module are:

SubscriptionManagerListConsumed - command ``subscription-manager list --consumed``
----------------------------------------------------------------------------------

SubscriptionManagerListInstalled - command ``subscription-manager list --installed``
------------------------------------------------------------------------------------
"""
import re
from datetime import datetime
import six
from insights.specs import Specs
from .. import parser, CommandParser
from . import keyword_search


class SubscriptionManagerList(CommandParser):
    """
    A general object for parsing the output of ``subscription-manager list``.
    This should be subclassed to read the specific output - e.g. ``--consumed``
    or ``--installed``.

    Attributes:
        records (list): A list of dict with the output info, it's empty when the ``error`` occurs
        error (str): The raised exception when there is traceback
    """
    def parse_content(self, content):
        self.records = []
        current_record = {}
        record_start_key = ''
        key = ''  # The key currently in use

        key_val_re = re.compile('^(?P<key>\w[\w\s]+\w):\s+(?P<value>\w.*)$')
        cont_val_re = re.compile('^\s+(?P<value>\w.*)$')

        # The first line that matches the key_val_re is treated as the start
        # of a record.  The header doesn't match because it doesn't have a
        # colon.  Once that's read, if the record start key is seen again
        # it starts a new record.

        for line in content:
            if 'Traceback' in line:
                self.error = content[-1]
                break
            # Check for match of key/value line
            match = key_val_re.search(line)
            if match:
                key, value = match.group('key', 'value')
                if not record_start_key:
                    record_start_key = key
                # Have we started a new record
                if key == record_start_key:
                    # If we have an existing record, save it
                    if current_record:
                        self.records.append(current_record)
                    current_record = {}
                current_record[key] = value
                # Do some type conversions and add-ons
                if key == 'Active' and value in ('True', 'False'):
                    current_record[key] = (value == 'True')
                elif key in ('Starts', 'Ends'):
                    try:
                        current_record[key + ' timestamp'] = datetime.strptime(
                            value, '%m/%d/%y'
                        )
                    except ValueError:
                        pass
            elif not record_start_key:
                # Ignore any lines before the first record key.
                continue
            # Check for value continuations
            match = cont_val_re.search(line)
            if match:
                # Add this value to the current key:
                if isinstance(current_record[key], six.string_types):
                    # Convert the single string into a list
                    current_record[key] = [
                        current_record[key], match.group('value')
                    ]
                else:
                    current_record[key].append(match.group('value'))

        # Save the last read record if we had one.
        if current_record:
            self.records.append(current_record)

    def search(self, *args, **kwargs):
        """
        Search for records that match the given keys and values.  See the
        :func:`insights.parsers.keyword_search` function for more details
        on usage.

        Arguments:
            **kwargs: Key-value pairs of search parameters.

        Returns:
            (list): A list of records that matched the search criteria.

        Examples:
            >>> len(consumed.search(Service_Level='PREMIUM'))
            1
            >>> consumed.search(Provides__contains='Red Hat Enterprise Virtualization')
            []
        """
        return keyword_search(self.records, parent=self, **kwargs)


@parser(Specs.subscription_manager_list_consumed)
class SubscriptionManagerListConsumed(SubscriptionManagerList):
    """
    Read the output of ``subscription-manager list --consumed``.

    Sample input file::

        +-------------------------------------------+
           Consumed Subscriptions
        +-------------------------------------------+
        Subscription Name: Red Hat Enterprise Linux Server, Premium (1-2 sockets) (Up to 1 guest)
        Provides:          Oracle Java (for RHEL Server)
                           Red Hat Software Collections Beta (for RHEL Server)
                           Red Hat Enterprise Linux Server
                           Red Hat Beta
        SKU:               RH0155783S
        Contract:          12345678
        Account:           1000001
        Serial:            0102030405060708090
        Pool ID:           8a85f981477e5284014783abaf5d4dcd
        Active:            True
        Quantity Used:     1
        Service Level:     PREMIUM
        Service Type:      L1-L3
        Status Details:    Subscription is current
        Subscription Type: Standard
        Starts:            11/14/14
        Ends:              07/06/15
        System Type:       Physical

    Examples:
        >>> type(consumed)
        <class 'insights.parsers.subscription_manager_list.SubscriptionManagerListConsumed'>
        >>> len(consumed.records)
        1
        >>> sub1 = consumed.records[0]
        >>> sub1['SKU']
        'RH0155783S'
        >>> sub1['Active']  # Type conversion on Active field
        True
        >>> sub1['Status Details']  # Keys appear as given
        'Subscription is current'
        >>> sub1['Provides'][1]
        'Red Hat Software Collections Beta (for RHEL Server)'
        >>> sub1['Starts']  # Basic field as text - note month/day/year
        '11/14/14'
        >>> sub1['Starts timestamp'].year
        2014
        >>> consumed.all_current  # Are all subscriptions listed as current?
        True
    """
    @property
    def all_current(self):
        """
        (bool) Does every subscription record have the Status Details value
        set to 'Subscription is current'?
        """
        return all(
            sub['Status Details'] == 'Subscription is current'
            for sub in self.records
        )


@parser(Specs.subscription_manager_list_installed)
class SubscriptionManagerListInstalled(SubscriptionManagerList):
    """
    Read the output of ``subscription-manager list --installed``.

    Sample input file::

        +-------------------------------------------+
        Installed Product Status
        +-------------------------------------------+
        Product Name:   Red Hat Software Collections (for RHEL Server)
        Product ID:     201
        Version:        2
        Arch:           x86_64
        Status:         Subscribed
        Status Details:
        Starts:         04/27/15
        Ends:           04/27/16

        Product Name:   Red Hat Enterprise Linux Server
        Product ID:     69
        Version:        7.1
        Arch:           x86_64
        Status:         Subscribed
        Status Details:
        Starts:         04/27/15
        Ends:           04/27/16

    Examples:
        >>> type(installed)
        <class 'insights.parsers.subscription_manager_list.SubscriptionManagerListInstalled'>
        >>> len(installed.records)
        2
        >>> prod1 = installed.records[0]
        >>> prod1['Product ID']  # Note - not converted to number
        '201'
        >>> prod1['Starts']  # String date as is
        '04/27/15'
        >>> prod1['Starts timestamp'].year  # Extra converted to date
        2015
        >>> installed.all_subscribed
        True

    """
    @property
    def all_subscribed(self):
        """
        (bool) Does every product record have the Status value set to
        'Subscribed'?
        """
        return all(
            sub['Status'] == 'Subscribed'
            for sub in self.records
        )
