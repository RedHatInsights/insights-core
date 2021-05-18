"""
AzureInstancePlan
=================

This parser reads the output of a command
``curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/plan?api-version=2018-10-01&format=json``,
which is used to check whether the instance is a marketplace image.

For more details, See: https://docs.microsoft.com/en-us/rest/api/compute/virtualmachines/createorupdate#plan

"""
import json

from insights.parsers import SkipException, ParseException
from insights import parser, CommandParser
from insights.specs import Specs


@parser(Specs.azure_instance_plan)
class AzureInstancePlan(CommandParser):
    """
    Class for parsing the Azure Instance Plan returned by command
    ``curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/plan?api-version=2018-10-01&format=json``,


    Typical Output of this command is::

        {
            "name": "planName",
            "product": "planProduct",
            "publisher": "planPublisher"
        },

    Raises:
        SkipException: When content is empty or no parse-able content.

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
        if not content or 'curl: ' in content[0]:
            raise SkipException()
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
