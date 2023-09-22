from insights.parsers import checkin_conf
from insights.parsers.checkin_conf import CheckinConf
from insights.tests import context_wrap
from insights.tests.parsers import ic_testmod


CONFIG = """
[logging]
config = /etc/splice/logging/basic.cfg

# this is used only for single-spacewalk deployments
[spacewalk]
# Spacewalk/Satellite server to use for syncing data.
host=
# Path to SSH private key used to connect to spacewalk host.
ssh_key_path=
login=swreport

# these are used for multi-spacewalk deployments
# [spacewalk_one]
# type = ssh
# # Spacewalk/Satellite server to use for syncing data.
# host=
# # Path to SSH private key used to connect to spacewalk host.
# ssh_key_path=
# login=swreport
#
# [spacewalk_two]
# type = file
# # Path to directory containing report output
# path = /path/to/output

[katello]
hostname=localhost
port=443
proto=https
api_url=/sam
admin_user=admin
admin_pass=admin
#autoentitle_systems = False
#flatten_orgs = False
""".strip()


def test_checkin_conf():
    result = CheckinConf(context_wrap(CONFIG))

    assert list(result.sections()) == ['logging', 'spacewalk', 'katello']
    assert result.get('spacewalk', 'host') == ''


def test_checkin_conf_doc_examples():
    env = {
        'CheckinConf': CheckinConf,
        'checkin_conf': CheckinConf(context_wrap(CONFIG))
    }
    failed, total = ic_testmod(checkin_conf, globs=env)
    assert failed == 0
