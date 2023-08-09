"""
Cloud Instance
==============

Combiner for the basic information of a cloud instance. It combines the
results of the following combiners and parsers:

* :py:class:`insights.combiners.cloud_provider.CloudProvider`
* :py:class:`insights.parsers.aws_instance_id.AWSInstanceIdDoc`
* :py:class:`insights.parsers.azure_instance.AzureInstanceID`
* :py:class:`insights.parsers.azure_instance.AzureInstanceType`
* :py:class:`insights.parsers.gcp_instance_type.GCPInstanceType`
* :py:class:`insights.parsers.subscription_manager.SubscriptionManagerFacts`

"""
from insights.combiners.cloud_provider import CloudProvider
from insights.core.exceptions import ContentException, SkipComponent
from insights.core.plugins import combiner
from insights.parsers.aws_instance_id import AWSInstanceIdDoc
from insights.parsers.azure_instance import AzureInstanceID, AzureInstanceType
from insights.parsers.gcp_instance_type import GCPInstanceType
from insights.parsers.subscription_manager import SubscriptionManagerFacts


@combiner(
    CloudProvider,
    [
        AWSInstanceIdDoc,
        AzureInstanceID,
        AzureInstanceType,
        GCPInstanceType,
        SubscriptionManagerFacts,
    ]
)
class CloudInstance(object):
    """
    Class to provide the basic information of a cloud instance.

    Attributes:
        provider (str): The cloud provider, e.g. "aws", "azure", "ibm",
                "google", or "alibaba". It's from the value of
                :class:`insights.combiners.cloud_provider.CloudProvider.cloud_provider`
        id (str): The ID of the cloud instance
        type (str): The type of the cloud instance.
                Different cloud providers have different illustration of the
                `type` and `size`, here for this Combiner, we treat the `type` and
                `size` as the same.  E.g.::

                    - "Standard_L64s_v2" for Azure
                    - "x1.16xlarge" for AWS
                    - "m1-megamem-96" for GCP

        size (str): Alias of the `type`

    Examples:
        >>> ci.provider
        'aws'
        >>> ci.id == 'i-1234567890abcdef0'
        True
        >>> ci.type == 't2.micro'
        True
        >>> ci.size == 't2.micro'
        True
    """
    def __init__(self, cp, aws=None, azure_id=None, azure_type=None,
                 gcp=None, facts=None):
        self.provider = cp.cloud_provider
        self.id = None
        # 1. Get from the Cloud REST API at first
        if aws:
            self.id = aws.get('instanceId')
            self.type = aws.get('instanceType')
        elif azure_id and azure_type:
            self.id = azure_id.id
            self.type = azure_type.raw
        elif gcp:
            self.type = gcp.raw
        # 2. Check the "subscription-manager facts"
        if self.id is None and facts:
            key = "{0}_instance_id".format(self.provider)
            if key not in facts:
                raise ContentException("Unmatched/unsupported types!")
            self.id = facts[key]
        # The instance id is the key attribute of this Combiner
        if self.id is None:
            raise SkipComponent
        # 'size' is the alias of 'type'
        self.size = self.type
