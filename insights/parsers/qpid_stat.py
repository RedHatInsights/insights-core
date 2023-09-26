"""
QPID statistics - command ``qpid-stat``
=======================================

This module contains parsers that check the QPID daemon statistics.  qpidd is
used by Satellite for communication between clients, capsules and servers.

Parsers provided by this module are:

QpidStatQ - command ``/usr/bin/qpid-stat -q --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671``
----------------------------------------------------------------------------------------------------------------------------------

QpidStatU - command ``/usr/bin/qpid-stat -u --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671``
----------------------------------------------------------------------------------------------------------------------------------

QpidStatG - command ``/usr/bin/qpid-stat -g --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671``
----------------------------------------------------------------------------------------------------------------------------------

"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsers import get_active_lines, keyword_search, parse_fixed_table
from insights.specs import Specs


class QpidStat(CommandParser):
    """Base class for parsing QpidStat command."""
    def __init__(self, context):
        self.data = []
        self.by_queue = {}
        super(QpidStat, self).__init__(context)

    def _check_content(self, content):
        self._content = get_active_lines(content, '=======')
        if len(self._content) <= 1:
            raise ParseException("Input content is empty or there is no useful parsed data.")

    def _parse_data(self, heading_ignore):
        self.data.extend(parse_fixed_table(self._content, heading_ignore=heading_ignore))

    def _parse_by_key(self, key):
        self.by_queue.update(dict(
            (q[key], q)
            for q in self.data
            if key in q
        ))

    def parse_content(self, content):
        self._check_content(content)
        self._parse_data('queue')
        self._parse_by_key('queue')
        del self._content

    def __iter__(self):
        return iter(self.data)

    def search(self, **kwargs):
        """
        Search for rows in the data matching keywords in the search.

        This method uses the :py:func:`insights.parsers.keyword_search`
        function - see its documentation for a complete description of its
        keyword recognition capabilities.

        Arguments:
            **kwargs: Key-value pairs of search parameters.

        Returns:
            (list): A list of subscriptions that matched the search criteria.

        """
        return keyword_search(self.data, parent=self, **kwargs)


@parser(Specs.qpid_stat_q)
class QpidStatQ(QpidStat):
    """
    This parser reads the output of the command ``qpid-stat -q
    --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b
    amqps://localhost:5671``

    Sample output::

        Queues
          queue                                                                      dur  autoDel  excl  msg   msgIn  msgOut  bytes  bytesIn  bytesOut  cons  bind
          ==========================================================================================================================================================
          00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0                                        Y        Y        0     2      2       0    486      486         1     2
          0f7f1a3d-daff-42a6-a994-29050a2eabde:1.0                                        Y        Y        0     8      8       0   4.88k    4.88k        1     2

    Attributes:
        data (list of dict): A list of dictionaries with the key-value data
            from the table.
        by_queue (dict of dict): A dictionary of the same data dictionaries
            stored by queue ID.

    Examples:
        >>> type(qpid_stat_q)
        <class 'insights.parsers.qpid_stat.QpidStatQ'>
        >>> type(qpid_stat_q.data) == type([])  # Queue data stored as it appears
        True
        >>> type(qpid_stat_q.data[0]) == type({}) # Each row is a dictionary formed from the table
        True
        >>> qpid_stat_q.data[0]['queue']
        '00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0'
        >>> qpid_stat_q.data[0]['dur']  # Blank columns are empty strings
        ''
        >>> qpid_stat_q.data[0]['autoDel']  # Flags are left as strings
        'Y'
        >>> qpid_stat_q.data[0]['msgOut']  # Numbers are left as strings
        '2'
        >>> qpid_stat_q.data[1]['bytesOut']  # No byte measure conversion
        '4.88k'
        >>> type(qpid_stat_q.by_queue) == type({}) # Dictionary lookup by queue ID
        True
        >>> qpid_stat_q.by_queue['00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0'] == qpid_stat_q.data[0]
        True
        >>> total_messages_in = 0
        >>> for queue in qpid_stat_q:  # Can be used as an iterator
        ...     total_messages_in += int(queue['msgIn'])
        ...
        >>> total_messages_in
        10
        >>> qpid_stat_q.search(queue__contains=':2.0')  # Keyword search
        []
    """
    pass


@parser(Specs.qpid_stat_u)
class QpidStatU(QpidStat):

    """
    This parser reads the output of the command ``qpid-stat -u
    --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b
    amqps://localhost:5671``

    Sample output::

        Subscriptions
          subscr               queue                                                                      conn                                    procName          procId  browse  acked  excl  creditMode  delivered  sessUnacked
          ===========================================================================================================================================================================================================================
          0                    00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0                                   qpid.10.20.1.10:5671-10.20.1.10:33787   celery            21409                        CREDIT      2          0
          0                    pulp.agent.c6a430bc-5ec7-42f8-99ce-f320ed0b9113                            qpid.10.20.1.10:5671-10.30.0.148:57423  goferd            32227           Y            CREDIT      0          0
          1                    server.example.com:event                                                   qpid.10.20.1.10:5671-10.20.1.10:33848   Qpid Java Client  21066           Y      Y     WINDOW      2,623      0
          0                    celeryev.4c77bd03-1cde-49eb-bdc0-b7c38f9ff93d                              qpid.10.20.1.10:5671-10.20.1.10:33777   celery            21356           Y            CREDIT      363,228    0
          1                    celery                                                                     qpid.10.20.1.10:5671-10.20.1.10:33786   celery            21409           Y            CREDIT      5          0

    Attributes:
        data (list of dict): A list of dictionaries with the key-value data
            from the table.
        by_queue (dict of dict): A dictionary of the same data dictionaries
            stored by queue ID.

    Examples:
        >>> type(qpid_stat_u)
        <class 'insights.parsers.qpid_stat.QpidStatU'>
        >>> type(qpid_stat_u.data) == type([]) # Subscription data stored as it appears
        True
        >>> type(qpid_stat_u.data[0]) == type({}) # Each row is a dictionary formed from the table
        True
        >>> qpid_stat_u.data[0]['queue']
        '00d6cc19-15fc-4b7c-af3c-6a38e7bb386d:1.0'
        >>> qpid_stat_u.data[0]['browse']  # Blank columns are empty strings
        ''
        >>> qpid_stat_u.data[1]['acked']  # Flags are left as strings
        'Y'
        >>> qpid_stat_u.data[1]['subscr']  # Numbers are left as strings
        '0'
        >>> qpid_stat_u.data[2]['delivered']  # Beware the commas
        '2,623'
        >>> type(qpid_stat_u.by_queue) == type({}) # Dictionary lookup by queue ID
        True
        >>> qpid_stat_u.by_queue['celery'] == qpid_stat_u.data[4]
        True
        >>> total_celery_queues = 0
        >>> for subscr in qpid_stat_u:  # Can be used as an iterator
        ...     if subscr['procName'] == 'celery':
        ...         total_celery_queues += 1
        ...
        >>> total_celery_queues
        3
        >>> event_queues = qpid_stat_u.search(queue__contains=':event')  # Keyword search
        >>> type(event_queues) == type([])
        True
        >>> len(event_queues)
        1
        >>> event_queues[0] == qpid_stat_u.data[2]  # List contains matching items
        True
    """

    def parse_content(self, content):
        self._check_content(content)
        self._parse_data('subscr')
        self._parse_by_key('queue')
        del self._content


@parser(Specs.qpid_stat_g)
class QpidStatG(QpidStat):

    """
    This parser reads the output of the command ``qpid-stat -g
    --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b
    amqps://localhost:5671``

    Sample output::

        Broker Summary:
          uptime           cluster       connections  sessions  exchanges  queues
          =========================================================================
          96d 23h 50m 41s  <standalone>  23           37        14         33

        Aggregate Broker Statistics:
          Statistic                   Messages    Bytes
          ========================================================
          queue-depth                 0           0
          total-enqueues              1,726,798   42,589,932,236
          total-dequeues              1,726,798   42,589,932,236
          persistent-enqueues         28,725      23,889,836
          persistent-dequeues         28,725      23,889,836
          transactional-enqueues      0           0
          transactional-dequeues      0           0
          flow-to-disk-depth          0           0
          flow-to-disk-enqueues       0           0
          flow-to-disk-dequeues       0           0
          acquires                    1,726,798
          releases                    0
          discards-no-route           41,163,896

    Attributes:
        data (list of dict): A list of dictionaries with the key-value data
            from the table.
        by_queue (dict of dict): A dictionary of the same data dictionaries
            stored by cluster name or queue name.

    Examples:
        >>> type(qpid_stat_g)
        <class 'insights.parsers.qpid_stat.QpidStatG'>
        >>> type(qpid_stat_g.data) == type([])
        True
        >>> type(qpid_stat_g.data[0]) == type({}) # Each row is a dictionary formed from the table
        True
        >>> qpid_stat_g.data[0]['uptime']
        '97d 0h 16m 24s'
        >>> qpid_stat_g.data[0]['cluster']
        '<standalone>'
        >>> qpid_stat_g.data[1]['Statistic']
        'queue-depth'
        >>> qpid_stat_g.data[1]['Messages']
        '0'
        >>> qpid_stat_g.data[11]['Bytes']
        ''
        >>> type(qpid_stat_g.by_queue) == type({}) # Dictionary lookup by queue ID
        True
        >>> qpid_stat_g.by_queue['queue-depth'] == qpid_stat_g.data[1]
        True
        >>> enqueues = qpid_stat_g.search(Statistic__contains='enqueues')  # Keyword search
        >>> type(enqueues) == type([])
        True
        >>> len(enqueues)
        4
        >>> enqueues[0] == qpid_stat_g.data[2]  # List contains matching items
        True
    """
    def _split_content(self):
        index = [i for i, l in enumerate(self._content) if l.startswith("Aggregate Broker Statistics")]
        if not index:
            raise ParseException("Incorrect Content without \"Aggregate Broker Statistics\" in ")
        self._index = index[0]

    def parse_content(self, content):
        self._check_content(content)
        self._split_content()
        self.__content = self._content
        self._content = self.__content[0:self._index]
        self._parse_data('uptime')
        self._content = self.__content[self._index:]
        self._parse_data('Statistic')
        self._parse_by_key('cluster')
        self._parse_by_key('Statistic')
        del self._index
        del self.__content
        del self._content
