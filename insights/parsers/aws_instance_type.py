"""
AWSInstanceType
===============

This parser simply reads the output of command
``curl -s http://169.254.169.254/latest/meta-data/instance-type``,
which is used to check the type of the AWS instance on the host.

"""

from insights.parsers import SkipException, ParseException
from insights import parser, CommandParser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.aws_instance_type)
class AWSInstanceType(CommandParser):
    """
    .. note::
        This parser is deprecated, please use
        :py:class:`insights.parsers.aws_instance_id.AWSInstanceIdDoc` instead.

    Class for parsing the AWS Instance type returned by command
    ``curl -s http://169.254.169.254/latest/meta-data/instance-type``

    Typical output of this command is::

        r3.xlarge

    Raises:
        SkipException: When content is empty or no parse-able content.
        ParseException: When type cannot be recognized.

    Attributes:
        type (str): The name of AWS instance type in all uppercase letters. E.g. R3, R4, R5, or X1.
        raw (str): The fully type string returned by the ``curl`` command.

    Examples:
        >>> aws_inst.type
        'R3'
        >>> aws_inst.raw
        'r3.xlarge'
    """

    def __init__(self, *args, **kwargs):
        deprecated(AWSInstanceType, "Use AWSInstanceIdDoc in insights.insights.aws_instance_id instead.")
        super(AWSInstanceType, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        if not content or 'curl: ' in content[0]:
            raise SkipException()

        self.raw = self.type = None

        # Ignore any curl stats that may be present in data
        for l in content:
            if ' ' not in l.strip() and len(l.strip()) > 0:
                self.raw = l.strip()
                if '.' in self.raw:
                    self.type = self.raw.split('.')[0].upper()

        if not self.type:
            raise ParseException('Unrecognized type: "{0}"'.format(content))

    def __repr__(self):
        return "<aws_type: {t}, raw: {r}>".format(t=self.type, r=self.raw)
