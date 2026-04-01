"""
Custom datasources for azure information
"""

import json

from insights.components.cloud_provider import IsAzure
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """Local specs used only by azure datasources"""

    azure_instance_compute_metadata_raw = simple_command(
        "/usr/bin/curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute?api-version=2021-12-13&format=json --connect-timeout 5",
        deps=[IsAzure],
    )
    """ Returns the Azure instance compute metadata from Azure Instance Metadata Service """


@datasource(LocalSpecs.azure_instance_compute_metadata_raw, HostContext)
def azure_instance_compute_metadata(broker):
    """
    This datasource provides Azure instance compute metadata from the Azure Instance Metadata Service.

    .. note::
        This datasource filters the full compute metadata JSON to include only the fields
        specified in the filters. The filters are added to the
        :mod:`insights.specs.Specs.azure_instance_compute_metadata` Spec.

    Typical content returned by the Azure Instance Metadata Service::

        {"licenseType": "", "plan": {"name": "", "product": "", "publisher": ""}, "tagsList": [], "vmId": "3c29e210-0669-496f-812a-2fffffffffff", ...}

    Returns:
        DatasourceProvider: JSON string containing only the filtered fields from Azure compute metadata.

    Raises:
        SkipComponent: When content is empty, curl error occurs, no filters defined,
                       invalid JSON format, JSON parsing fails, or no matching filters found.
    """

    filters = get_filters(Specs.azure_instance_compute_metadata)
    if not filters:
        raise SkipComponent("No filters defined")

    raw_content = broker[LocalSpecs.azure_instance_compute_metadata_raw].content
    if not raw_content or 'curl: ' in raw_content[0]:
        raise SkipComponent("Empty content or curl error")

    try:
        content = json.loads(raw_content[0])
    except Exception as e:
        raise SkipComponent("Failed to parse metadata: {0}".format(e))

    if not isinstance(content, dict):
        raise SkipComponent("Invalid JSON format")

    result = {key: content[key] for key in filters if key in content}
    if not result:
        raise SkipComponent("No matching filters found in metadata")

    return DatasourceProvider(
        content=json.dumps(result, sort_keys=True),
        relative_path='insights_datasources/azure_instance_compute_metadata',
        ds=Specs.azure_instance_compute_metadata,
        ctx=broker.get(HostContext),
        cleaner=broker.get("cleaner"),
    )
