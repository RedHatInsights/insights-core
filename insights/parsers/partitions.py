"""
Partitions - file ``/proc/partitions``
======================================

This parser reads the ``/proc/partitions`` file, which contains
partition block allocation information.

"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import parse_delimited_table
from insights.specs import Specs


@parser(Specs.partitions)
class Partitions(Parser, dict):
    """A class for parsing the ``/proc/partitions`` file.

    Sample input::

        major minor  #blocks  name

           3     0   19531250 hda
           3     1     104391 hda1
           3     2   19422585 hda2
         253     0   22708224 dm-0
         253     1     524288 dm-1

    Examples:
       >>> type(partitions_info)
       <class 'insights.parsers.partitions.Partitions'>
       >>> 'hda' in partitions_info
       True
       >>> partitions_info['dm-0'].get('major')
       '253'
       >>> sorted(partitions_info['hda'].items(), key=lambda x: x[0])
       [('blocks', '19531250'), ('major', '3'), ('minor', '0'), ('name', 'hda')]

    Raises:
        SkipComponent: When input is empty.

    """
    def parse_content(self, content):
        if not content:
            raise SkipComponent('Empty content')

        self.update(dict(
            (row['name'], row)
            for row in parse_delimited_table(
                    content,
                    heading_ignore=['major', 'minor'],
                    header_substitute=[('#blocks', 'blocks')]
            )
            if 'name' in row)
        )

    @property
    def partitions(self):
        """
        (:obj:`dict`): Dictionary with each partition name as index and
            its information from the block allocation table.
        """
        return self
