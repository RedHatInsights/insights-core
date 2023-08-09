"""
Components identify Cloud Provider
===================================

The ``Is*`` component in this module is valid if the
:py:class:`insights.combiners.cloud_provider.CloudProvider` combiner indicates
the host is from the specific Cloud Provider.  Otherwise, it raises a
:py:class:`insights.core.exceptions.SkipComponent` to prevent dependent components from
executing.

"""
from insights.combiners.cloud_provider import CloudProvider
from insights.core.exceptions import SkipComponent
from insights.core.plugins import component


@component(CloudProvider)
class IsAWS(object):
    """
    This component uses ``CloudProvider`` combiner to determine the cloud
    provider of the instance.
    It checks if AWS, if not AWS it raises ``SkipComponent``.

    Raises:
        SkipComponent: When it's not an instance from AWS.
    """
    def __init__(self, cp):
        if not cp or cp.cloud_provider != CloudProvider.AWS:
            raise SkipComponent("Not AWS instance")


@component(CloudProvider)
class IsAzure(object):
    """
    This component uses ``CloudProvider`` combiner to determine the cloud
    provider of the instance.
    It checks if Azure, if not Azure it raises ``SkipComponent``.

    Raises:
        SkipComponent: When it's not an instance from Azure.
    """
    def __init__(self, cp):
        if not cp or cp.cloud_provider != CloudProvider.AZURE:
            raise SkipComponent("Not Azure instance")


@component(CloudProvider)
class IsGCP(object):
    """
    This component uses ``CloudProvider`` combiner to determine the cloud
    provider of the instance.
    It checks if Google Cloud Platform (GCP), if not GCP it raises ``SkipComponent``.

    Raises:
        SkipComponent: When it's not an instance from GCP.
    """
    def __init__(self, cp):
        if not cp or cp.cloud_provider != CloudProvider.GOOGLE:
            raise SkipComponent("Not Google Cloud Platform instance")
