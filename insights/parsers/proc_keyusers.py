"""
ProcKeyUsers - File ``/proc/key-users``
=======================================

This parser reads the content of ``/proc/key-users``.

"""
from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.proc_keyusers)
class ProcKeyUsers(Parser, list):
    """
    Class ``ProcKeyUsers`` parses the content of the ``/proc/key-users`` file.

    This file lists various information for each user ID that has at least
    one key on the system. The fields in each line are in format::

        uid:    usage nkeys/nikeys qnkeys/maxkeys qnbytes/maxbytes

    The fields shown in each line will be parsed as follows::

        uid (string):   The user ID.
        usage (int):    This is a kernel-internal usage count for the
                        kernel structure used to record key users.
        nkeys (int):    The total number of keys owned by the user.
        nikeys (int):   The number of those keys that have been instantiated.

        qnkeys (int):   The number of keys owned by the user.
        maxkeys (int):  The maximum number of keys that the user may own.

        qnbytes (int):  The number of bytes consumed in payloads of the
                        keys owned by this user.
        maxbytes (int): The upper limit on the number of bytes in key
                        payloads for that user.

    Sample data::

            0:   106 105/105 95/1000000 1909/25000000
          862:     4 4/4 4/200 40/20000
          980:     9 9/9 9/200 138/20000
          983:     1 1/1 1/200 9/20000
         5090:   192 192/192 192/200 990/20000
         7502:     8 8/8 8/200 66/20000
         7563:     4 4/4 4/200 46/20000
         7637:     4 4/4 4/200 46/20000

    Examples:
        >>> type(proc_keyusers)
        <class 'insights.parsers.proc_keyusers.ProcKeyUsers'>
        >>> proc_keyusers[4]['uid']
        '5090'
        >>> proc_keyusers[4]['qnkeys']
        192
        >>> proc_keyusers[4]['maxkeys']
        200
        >>> proc_keyusers[4]['usage']
        192
        >>> len(proc_keyusers)
        8
    """

    def parse_content(self, content):

        fields = tuple(["usage", "nkeys", "nikeys", "qnkeys", "maxkeys", "qnbytes", "maxbytes"])

        for line in content:

            spl_colon = [_.strip() for _ in line.split(':')]
            value_pairs = spl_colon[-1].split()

            if not (len(spl_colon) == 2 and len(value_pairs) == 4 and spl_colon[0].isdigit()):
                raise ParseException("Unparsable line: {0}".format(line))

            try:
                field_values = [int(v) for vp in value_pairs for v in vp.split('/', 1)]
            except ValueError:
                raise ParseException("Unparsable line: not int value: {0}".format(line))

            if not len(field_values) == 7:
                raise ParseException("Unparsable line: unexpected value count: {0}".format(line))

            parsed_line = dict(zip(fields, field_values))
            parsed_line['uid'] = spl_colon[0]
            self.append(parsed_line)

        if len(self) == 0:
            raise SkipComponent
