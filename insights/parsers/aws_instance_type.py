"""
AWSInstanceType
===============

This parser simply reads the output of command
``curl http://169.254.169.254/latest/meta-data/instance-type``,
which is used to check the type of the AWS instance on the host.

"""

from insights.parsers import SkipException, ParseException
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
        ParseException: When type cannot be recognized.

    Attributes:
        type: The name of AWS instance type in all uppercase letters. E.g. R3, R4, R5, or X1.
        raw: The fully type string returned by the ``curl`` command.

    Examples:
        >>> aws_inst.type
        'R3'
        >>> aws_inst.raw
        'r3.xlarge'
    """

    def parse_content(self, content):
        if (not content or len(content) > 1 or 'curl: ' in content[0]):
            raise SkipException()

        self.raw = self.type = None
        if '.' in content[0]:
            self.raw = content[0].strip()
            self.type = self.raw.split('.')[0].upper()

        if not self.type:
            raise ParseException('Unrecognized type: "{0}"', content[0])

    def __str__(self):
        return "<aws_type: {t}, raw: {r}>".format(t=self.type, r=self.raw)
