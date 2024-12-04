import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import cloud_init
from insights.tests import context_wrap

CLOUD_INIT_QUERY_OUTPUT1 = """
(u'azure', u'azure')
""".strip()

CLOUD_INIT_QUERY_OUTPUT2 = """
('aws', 'ec2')
""".strip()

CLOUD_INIT_QUERY_OUTPUT3 = """
2024-11-19 03:14:38,741 - query.py[WARNING]: Missing root-readable /run/cloud-init/instance-data-sensitive.json. Using redacted /run/cloud-init/instance-data.json instead.
2024-11-19 03:14:38,741 - query.py[ERROR]: Missing instance-data file: /run/cloud-init/instance-data.json
""".strip()

CLOUD_INIT_QUERY_OUTPUT4 = """
(2024-11-19, test, test)
""".strip()


def test_cloud_init_query():
    ret = cloud_init.CloudInitQuery(context_wrap(CLOUD_INIT_QUERY_OUTPUT1))
    assert ret.cloud_name == 'azure'
    assert ret.platform == 'azure'

    ret = cloud_init.CloudInitQuery(context_wrap(CLOUD_INIT_QUERY_OUTPUT2))
    assert ret.cloud_name == 'aws'
    assert ret.platform == 'ec2'

    with pytest.raises(SkipComponent):
        cloud_init.CloudInitQuery(context_wrap(CLOUD_INIT_QUERY_OUTPUT3))

    with pytest.raises(SkipComponent):
        cloud_init.CloudInitQuery(context_wrap(CLOUD_INIT_QUERY_OUTPUT4))


def test_cloud_init_docs():
    env = {
        'cloud_query': cloud_init.CloudInitQuery(context_wrap(CLOUD_INIT_QUERY_OUTPUT1)),
    }
    failed, total = doctest.testmod(cloud_init, globs=env)
    assert failed == 0
