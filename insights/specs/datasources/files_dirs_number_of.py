"""
Custom datasources to get dict of file or dir numbers
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
def files_dirs_number(broker):
    """ Return a dict of file numbers from the spec filter """
    filters = sorted(get_filters(Specs.files_dirs_number_filter))
    result = {}
    if filters:
        for item in filters:
            if not item.endswith("/"):
                item = item + "/"
            if os.path.exists(item):
                files_number = 0
                dirs_number = 0
                result[item] = {}
                for name in os.listdir(item):
                    if os.path.isfile(item + name):
                        files_number = files_number + 1
                    elif os.path.isdir(item + name):
                        dirs_number = dirs_number + 1
                result[item]["files_number"] = files_number
                result[item]["dirs_number"] = dirs_number
        if result:
            return DatasourceProvider(content=json.dumps(result, sort_keys=True), relative_path='files_dirs_number')
    raise SkipComponent
