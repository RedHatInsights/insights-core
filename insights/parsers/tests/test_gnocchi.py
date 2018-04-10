import doctest
from insights.parsers import gnocchi
from insights.parsers.gnocchi import GnocchiConf, GnocchiMetricdLog
from insights.tests import context_wrap

from datetime import datetime

GNOCCHI_CONF = """
[DEFAULT]
log_dir = /var/log/gnocchi
[api]
auth_mode = keystone
max_limit = 1000
[archive_policy]
[indexer]
url = mysql+pymysql://gnocchi:exampleabckeystring@192.168.0.1/gnocchi?charset=utf8
[metricd]
workers = 2
[oslo_middleware]
[oslo_policy]
policy_file = /etc/gnocchi/policy.json
[statsd]
resource_id = 5e3fcbe2-7aab-475d-b42c-abcdefgh
user_id = e0ca4711-1128-422c-abd6-abcdefgh
project_id = af0c88e8-90d8-4795-9efe-abcdefgh
archive_policy_name = high
flush_delay = 10
[storage]
driver = file
#this one comment
file_basepath = /var/lib/gnocchi
[keystone_authtoken]
auth_uri=http://192.168.0.1:5000/v3
auth_type=password
auth_version=v3
auth_url=http://192.168.0.1:35357
username=gnocchi
password=yourpassword23432
user_domain_name=Default
project_name=services
project_domain_name=Default
""".strip()

METRICD_LOG = """
2017-04-12 03:10:53.076 14550 INFO gnocchi.cli [-] 0 measurements bundles across 0 metrics wait to be processed.
2017-04-12 03:12:53.078 14550 INFO gnocchi.cli [-] 0 measurements bundles across 0 metrics wait to be processed.
2017-04-12 03:14:53.080 14550 INFO gnocchi.cli [-] 0 measurements bundles across 0 metrics wait to be processed.
2017-04-13 21:06:11.676 114807 ERROR tooz.drivers.redis ToozError: Cannot extend an unlocked lock
"""


def test_gnocchi_conf():
    gnocchi_conf = GnocchiConf(context_wrap(GNOCCHI_CONF))
    assert sorted(gnocchi_conf.sections()) == sorted(['api', 'archive_policy', 'indexer', 'metricd', 'oslo_middleware', 'oslo_policy', 'statsd', 'storage', 'keystone_authtoken'])
    assert "storage" in gnocchi_conf.sections()
    assert gnocchi_conf.has_option('indexer', 'url')
    assert gnocchi_conf.get("indexer", "url") == "mysql+pymysql://gnocchi:exampleabckeystring@192.168.0.1/gnocchi?charset=utf8"
    assert gnocchi_conf.getint("statsd", "flush_delay") == 10


def test_metrics_log():
    log = GnocchiMetricdLog(context_wrap(METRICD_LOG))
    assert len(log.get('INFO')) == 3
    assert 'measurements bundles across 0 metrics wait to be processed' in log
    assert log.get('ERROR') == [{'raw_message': '2017-04-13 21:06:11.676 114807 ERROR tooz.drivers.redis ToozError: Cannot extend an unlocked lock'}]
    assert len(list(log.get_after(datetime(2017, 4, 12, 19, 36, 38)))) == 1
    assert list(log.get_after(datetime(2017, 4, 12, 19, 36, 38))) == [{'raw_message': '2017-04-13 21:06:11.676 114807 ERROR tooz.drivers.redis ToozError: Cannot extend an unlocked lock'}]


def test_doc():
    env = {
            'GnocchiConf': GnocchiConf,
            'conf': GnocchiConf(context_wrap(GNOCCHI_CONF, path='/etc/gnocchi/gnocchi.conf')),
            'GnocchiMetricdLog': GnocchiMetricdLog,
            'log': GnocchiMetricdLog(context_wrap(METRICD_LOG, path='/etc/gnocchi/metricd.log')),
          }
    failed, total = doctest.testmod(gnocchi, globs=env)
    assert failed == 0
