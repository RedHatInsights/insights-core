import doctest

from insights.parsers import ls_var_cache_pulp
from insights.parsers.ls_var_cache_pulp import LsVarCachePulp
from insights.tests import context_wrap

LS_VAR_CACHE_PULP = """
total 0
drwxrwxr-x.  5 48 1000 216 Jan 21 12:56 .
drwxr-xr-x. 10  0    0 121 Jan 20 13:57 ..
lrwxrwxrwx.  1  0    0  19 Jan 21 12:56 cache -> /var/lib/pulp/cache
drwxr-xr-x.  2 48   48   6 Jan 21 13:03 reserved_resource_worker-0@dhcp130-202.gsslab.pnq2.redhat.com
drwxr-xr-x.  2 48   48   6 Jan 21 02:03 reserved_resource_worker-1@dhcp130-202.gsslab.pnq2.redhat.com
drwxr-xr-x.  2 48   48   6 Jan 20 14:03 resource_manager@dhcp130-202.gsslab.pnq2.redhat.com
"""


def test_ls_var_cache_pulp():
    ls_var_cache_pulp = LsVarCachePulp(context_wrap(LS_VAR_CACHE_PULP, path="insights_commands/ls_-lan_.var.cache.pulp"))
    assert ls_var_cache_pulp.files_of('/var/cache/pulp') == ['cache']
    cache_item = ls_var_cache_pulp.dir_entry('/var/cache/pulp', 'cache')
    assert cache_item is not None
    assert '/var/lib/pulp/' in cache_item['link']


def test_ls_var_lib_mongodb_doc_examples():
    env = {
        'ls_var_cache_pulp': LsVarCachePulp(context_wrap(LS_VAR_CACHE_PULP, path="insights_commands/ls_-lan_.var.cache.pulp")),
    }
    failed, total = doctest.testmod(ls_var_cache_pulp, globs=env)
    assert failed == 0
