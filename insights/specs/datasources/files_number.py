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
    # filters = sorted(get_filters(Specs.files_number_filter))
    # print ("5050050505")
    # print (get_filters(Specs.files_number_filter))
    result = {}
    filters = ["/var/spool/postfix/maildrop/", "/var/spool/clientmqueue"]
    # print ("2020202020")
    if filters:
        for item in filters:
            if not item.endswith("/"):
                item = item + "/"
            result[item] = len([name for name in os.listdir(item) if os.path.isfile(item + name)])
        print ("30303030")
        print (result)
        print (json.dumps(result))
        return DatasourceProvider(content=json.dumps(result), relative_path='files_number')
    raise SkipComponent
