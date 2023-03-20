"""
Custom datasources related to ``md5``
"""
from insights.core.context import HostContext
from insights.core.plugins import datasource


#
# This function is quite simple, do not need to test
#
@datasource(HostContext)
def files(broker):
    """
    Return a list of files to be processed by the ``md5chk_files`` spec
    """
    return [
        "/etc/pki/product/69.pem",
        "/etc/pki/product-default/69.pem",
        "/usr/lib/libsoftokn3.so",
        "/usr/lib64/libsoftokn3.so",
        "/usr/lib/libfreeblpriv3.so",
        "/usr/lib64/libfreeblpriv3.so"
    ]
