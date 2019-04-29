"""
Partitions - file ``/proc/partitions``
======================================

This parser reads the ``/proc/partitions`` file, which contains
partition block allocation information.

"""
from insights import Parser, parser
from insights.parsers import SkipException, parse_delimited_table
from insights.specs import Specs


@parser(Specs.partitions)
class Partitions(Parser):
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
       >>> sorted(partitions_info['hda'].items(), key=lambda x: x[0])
       [('blocks', '19531250'), ('major', '3'), ('minor', '0'), ('name', 'hda')]
       >>> 'hda' in partitions_info
       True
       >>> partitions_info['dm-0'].get('major')
       '253'
       >>> partitions_list = [p for p in partitions_info]
       >>> sorted(partitions_list[-1].items(), key=lambda x: x[0])
       [('blocks', '524288'), ('major', '253'), ('minor', '1'), ('name', 'dm-1')]

    Attributes:
        partitions (:obj:`dict`): Dictionary with each partition name as index and
            its information from the block allocation table.

    Raises:
        SkipException: When input is empty.

    """
    def parse_content(self, content):
        if not content:
            raise SkipException('Empty content')

        self.partitions = {}

        self.partitions = dict(
            (row['name'], row)
            for row in parse_delimited_table(
                    content,
                    heading_ignore=['major', 'minor'],
                    header_substitute=[('#blocks', 'blocks')]
            )
            if 'name' in row
        )

    def __getitem__(self, item):
        """Fetch the information by name in partition table.

        Args:
            item (string): Name of the partition.

        Returns:
            dict: The information for the given partition name.
        """
        return self.partitions[item]

    def __contains__(self, item):
        return item in self.partitions

    def __iter__(self):
        for partition in self.partitions.values():
            yield partition
