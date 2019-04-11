"""
AWSInstanceType
===============

This parser simply reads the output of command
``curl http://169.254.169.254/latest/meta-data/instance-type``,
which is used to check the type of the AWS instance on the host.

"""

from insights.parsers import SkipException
from insights import parser, CommandParser
from insights.specs import Specs


@parser(Specs.aws_instance_type)
class AWSInstanceType(CommandParser):
    """
    Class for parsing the AWS Instance type returned by command
    ``curl http://169.254.169.254/latest/meta-data/instance-type``

    Typical output of this command is::

        r3.xlarge

    Raises:
        SkipException: When content is empty or no parse-able content.

    Attributes:
        type: The name of AWS instance type in all uppercase lettes. E.g. R3, R4, R5, or X1.
        raw: The fully type string returned by the ``curl`` command.

    Examples:
        >>> aws_inst.type
        'R3'
        >>> aws_inst.raw
        'r3.xlarge'
    """

    def parse_content(self, content):
        if not content:
            raise SkipException('Empty content.')

        self.type = self.raw = None
        for line in content:
            if 'xlarge' in line:
                self.raw = [i for i in line.split() if 'xlarge' in i and '.' in i][0]
                self.type = self.raw.split('.')[0].upper()

        if self.raw is None:
            raise SkipException('Not AWS.')

    def __str__(self):
        return "<aws_type: {t}, raw: {r}>".format(t=self.type, r=self.raw)
