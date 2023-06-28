"""
AzureInstancePlan
=================

This parser reads the output of a command
``curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/plan?api-version=2018-10-01&format=json``,
which is used to check whether the instance is a marketplace image.

For more details, See: https://docs.microsoft.com/en-us/rest/api/compute/virtualmachines/createorupdate#plan

"""
import json

from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.azure_instance_plan)
class AzureInstancePlan(CommandParser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.azure_instance.AzureInstancePlan` instead.

    Class for parsing the Azure Instance Plan returned by command
    ``curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/plan?api-version=2018-10-01&format=json``,


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
    def __init__(self, *args, **kwargs):
        deprecated(AzureInstancePlan, "Import AzureInstancePlan from insights.parsers.azure_instance instead.", "3.3.0")
        super(AzureInstancePlan, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        if not content or 'curl: ' in content[0]:
            raise SkipComponent()
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
