"""
Alibaba InstanceType
====================

This parser simply reads the output of command
``curl http://100.100.100.200/latest/meta-data/instance/instance-type``,
which is used to check the type of the instance type of the host running on
Alibaba Cloud.

For more details, See: https://www.alibabacloud.com/help/doc-detail/49122.htm

"""

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException


@parser(Specs.alibaba_instance_type)
class AlibabaInstanceType(CommandParser):
    """
    Class for parsing the Alibaba Instance type returned by command
    ``curl http://100.100.100.200/latest/meta-data/instance/instance-type``,


    Typical output of this command is::

        ecs.ebmg5s.24xlarge

    Raises:
        SkipException: When content is empty or no parse-able content.
        ParseException: When type cannot be recognized.

    Attributes:
        type (str): The type of VM instance in Alibaba, e.g: ebmg5s
        size (str): The size of VM instance in Alibaba, e.g: 24xlarge
        raw (str): The fully type string returned by the ``curl`` command

    Examples:
        >>> alibaba_inst.type
        'ebmg5s'
        >>> alibaba_inst.size
        '24xlarge'
        >>> alibaba_inst.raw
        'ecs.ebmg5s.24xlarge'
    """

    def parse_content(self, content):
        if not content or 'curl: ' in content[0]:
            raise SkipException()

        self.raw = self.type = self.size = None
        # Ignore any curl stats that may be present in data
        for l in content:
            l_strip = l.strip()
            if ' ' not in l_strip and '.' in l_strip:
                self.raw = l_strip
                type_sp = l_strip.split('.')
                if len(type_sp) == 3:
                    self.type, self.size = type_sp[1], type_sp[2]

        if not self.type:
            raise ParseException('Unrecognized type: "{0}"', content[0])

    def __repr__(self):
        return "<alibaba_instance_type: {t}, size: {s},  raw: {r}>".format(
                t=self.type, s=self.size, r=self.raw)
