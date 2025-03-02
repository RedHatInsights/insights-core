"""
Custom datasources to get dict of file numbers
"""
import json
import os
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs


@datasource(HostContext)
def files_number_dir(broker):
    """ Return a dict of file numbers from the spec filter """
    filters = sorted(get_filters(Specs.files_number_filter), reverse=False)
    result = {}
    if filters:
        for item in filters:
            if not item.endswith("/"):
                item = item + "/"
            if os.path.exists(item):
                result[item] = len([name for name in os.listdir(item) if os.path.isfile(item + name)])
        return DatasourceProvider(content=json.dumps(result), relative_path='files_number')
    raise SkipComponent
