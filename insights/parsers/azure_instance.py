"""
AzureInstance
=============

The following Azure Instance related parsers are placed in this module:

AzureInstanceID - 'vmId' of Azure Instance
------------------------------------------

AzureInstanceType - 'vmSize' of Azure Instance
----------------------------------------------

AzureInstancePlan - 'plan' of Azure Instance
--------------------------------------------
"""
import json

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


def validate_content(content):
    if not content or 'curl: ' in content[0]:
        raise SkipComponent()


@parser(Specs.azure_instance_id)
class AzureInstanceID(CommandParser):
    """
    Class for parsing the Azure Instance type returned by command
    ``curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/vmId?api-version=2021-12-13&format=text``,


    Typical output of this command is::

        f904ece8-c6c1-4b5c-881f-309b50f25e50

    Raises:
        SkipComponent: When content is empty or no parse-able content.

    Attributes:
        id (str): The instance ID of the VM instance in Azure.

    Examples:
        >>> azure_id.id
        'f904ece8-c6c1-4b5c-881f-309b50f25e50'
    """

    def parse_content(self, content):
        validate_content(content)

        self.id = content[0].strip()

    def __repr__(self):
        return "<instance_id: {i}>".format(i=self.id)


@parser(Specs.azure_instance_type)
class AzureInstanceType(CommandParser):
    """
    Class for parsing the Azure Instance type returned by command
    ``curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/vmSize?api-version=2021-12-13&format=text``,


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
        >>> azure_type.type
        'Standard'
        >>> azure_type.size
        'L64s'
        >>> azure_type.version
        'v2'
        >>> azure_type.raw
        'Standard_L64s_v2'
    """
    def parse_content(self, content):
        validate_content(content)

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


@parser(Specs.azure_instance_plan)
class AzureInstancePlan(CommandParser):
    """
    Class for parsing the Azure Instance Plan returned by command
    ``curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/plan?api-version=2021-12-13&format=json``,


    Typical Output of this command is::

        {
            "name": "planName",
            "product": "planProduct",
            "publisher": "planPublisher"
        },

    Raises:
        SkipComponent: When content is empty or no parse-able content.

    Attributes:
        name (str): The name of the plan for the VM Instance in Azure, e.g: rhel7
        product (str): The product of the plan for the VM Instance in Azure, e.g: RHEL
        publisher (str): The publisher of the plan for the VM Instance in Azure, e.g: Red hat
        raw (str): The full JSON of the plan returned by the ``curl`` command

    Examples:
        >>> azure_plan.name == 'planName'
        True
        >>> azure_plan.product == 'planProduct'
        True
        >>> azure_plan.publisher == 'planPublisher'
        True
    """
    def parse_content(self, content):
        validate_content(content)

        try:
            plan = json.loads(content[0])
        except:
            raise ParseException("Unable to parse JSON")

        self.raw = content[0]
        self.name = plan["name"] if plan["name"] != "" else None
        self.product = plan["product"] if plan["product"] != "" else None
        self.publisher = plan["publisher"] if plan["publisher"] != "" else None

    def __repr__(self):
        return "<azure_plan_name: {n}, product: {pr}, publisher: {pu}, raw: {r}".format(
            n=self.name, pr=self.product, pu=self.publisher, r=self.raw
        )
