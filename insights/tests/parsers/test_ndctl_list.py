import doctest

from insights.parsers import ndctl_list
from insights.parsers.ndctl_list import NdctlListNi
from insights.tests.parsers import skip_component_check
from insights.tests import context_wrap

NDCTL_OUTPUT = """
[
    {
        "dev":"namespace1.0",
        "mode":"fsdax",
        "map":"mem",
        "size":811746721792,
        "uuid":"6a7d93f5-60c4-461b-8d19-0409bd323a94",
        "sector_size":512,
        "align":2097152,
        "blockdev":"pmem1"
    },
    {
        "dev":"namespace1.1",
        "mode":"raw",
        "size":0,
        "uuid":"00000000-0000-0000-0000-000000000000",
        "sector_size":512,
        "state":"disabled"
    },
    {
        "dev":"namespace0.0",
        "mode":"raw",
        "size":0,
        "uuid":"00000000-0000-0000-0000-000000000000",
        "sector_size":512,
        "state":"disabled"
    }
]
""".strip()


def test_ndctl_list_doc_examples():
    env = {
        'ndctl_list': NdctlListNi(context_wrap(NDCTL_OUTPUT))
    }
    failed, total = doctest.testmod(ndctl_list, globs=env)
    assert failed == 0


def test_get_dev_attr():
    ndctl = NdctlListNi(context_wrap(NDCTL_OUTPUT))
    assert ndctl.blockdev_list == ['pmem1']
    assert 'map' in ndctl.get_blockdev('pmem1')
    assert ndctl.get_blockdev('pmem1').get('map') == 'mem'
    assert ndctl.get_blockdev('pmem2') == {}


def test_empty():
    assert 'Empty output.' in skip_component_check(NdctlListNi)
