"""
AzureInstanceType
=================

This parser simply reads the output of command
``curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/vmSize?api-version=2018-10-01&format=text``,
which is used to check the type of the Azure instance of the host.

For more details, See: https://docs.microsoft.com/en-us/azure/virtual-machines/linux/sizes

"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.azure_instance_type)
class AzureInstanceType(CommandParser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.azure_instance.AzureInstanceType` instead.

    Class for parsing the Azure Instance type returned by command
    ``curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/vmSize?api-version=2018-10-01&format=text``,


    Typical output of this command is::

        Standard_L64s_v2

    Raises:
        SkipComponent: When content is empty or no parse-able content.
        ParseException: When type cannot be recognized.

    Attributes:
        type (str): The type of VM instance in Azure, e.g: Standard
        size (str): The size of VM instance in Azure, e.g: L64s, NC12s
        version (str): The version of VM instance in Azure, e.g: v2, v3, `None` for non-version
        raw (str): The fully type string returned by the ``curl`` command

    Examples:
        >>> azure_inst.type
        'Standard'
        >>> azure_inst.size
        'L64s'
        >>> azure_inst.version
        'v2'
        >>> azure_inst.raw
        'Standard_L64s_v2'
    """
    def __init__(self, *args, **kwargs):
        deprecated(AzureInstanceType, "Import AzureInstanceType from insights.parsers.azure_instance instead", "3.2.25")
        super(AzureInstanceType, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        if not content or 'curl: ' in content[0]:
            raise SkipComponent()

        self.raw = self.type = self.size = self.version = None
        # Ignore any curl stats that may be present in data
        for l in content:
            l_strip = l.strip()
            if ' ' not in l_strip and '_' in l_strip:
                self.raw = l_strip
                type_sp = l_strip.split('_')
                self.type, self.size = type_sp[0], type_sp[1]
                if len(type_sp) >= 3:
                    self.version = type_sp[2]

        if not self.type:
            raise ParseException('Unrecognized type: "{0}"', content[0])

    def __repr__(self):
        return "<azure_type: {t}, size: {s}, version: {v},  raw: {r}>".format(
                t=self.type, s=self.size, v=self.version, r=self.raw)
