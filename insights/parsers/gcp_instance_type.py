"""
GCPInstanceType
===============

This parser simply reads the output of command
``curl http://metadata.google.internal/computeMetadata/v1/instance/machine-type -H 'Metadata-Flavor: Google'``,
which is used to check the machine type of the Google instance of the host.

For more details, See:
- https://cloud.google.com/compute/docs/machine-types
- https://cloud.google.com/compute/docs/storing-retrieving-metadata#api_4

"""

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException


@parser(Specs.gcp_instance_type)
class GCPInstanceType(CommandParser):
    """
    Class for parsing the GCP Instance type returned by command
    ``curl -s -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/machine-type``,


    Typical output of this command is::

        projects/123456789/machineTypes/n2-highcpu-16


    Raises:
        SkipException: When content is empty or no parse-able content.
        ParseException: When type cannot be recognized.

    Attributes:
        type (str): The type of VM instance in GCP, e.g: n2
        size (str): The size of VM instance in GCP, e.g: highcpu-16
        raw (str): The fully type string, e.g. 'n2-highcpu-16'
        raw_line (str): The fully type string returned by the ``curl`` command

    Examples:
        >>> gcp_inst.type
        'n2'
        >>> gcp_inst.size
        'highcpu-16'
        >>> gcp_inst.raw
        'n2-highcpu-16'
    """

    def parse_content(self, content):
        if not content or 'curl: ' in content[0]:
            raise SkipException()

        self.raw_line = self.raw = self.type = self.size = None
        # Ignore any curl stats that may be present in data
        for l in content:
            l_strip = l.strip()
            if ' ' not in l_strip and '-' in l_strip:
                self.raw_line = l_strip
                self.raw = l_strip.split('/')[-1]
                type_sp = self.raw.split('-', 1)
                self.type, self.size = type_sp[0], type_sp[1]

        if not self.type:
            raise ParseException('Unrecognized type: "{0}"', content[0])

    def __repr__(self):
        return "<gcp_type: {t}, size: {s}, raw: {r}>".format(
                t=self.type, s=self.size, r=self.raw_line)
