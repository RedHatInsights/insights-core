from insights.parsers.rc_local import RcLocal
from insights.tests import context_wrap

RC_LOCAL_DATA = """
#!/bin/sh
#
# This script will be executed *after* all the other init scripts.
# You can put your own initialization stuff in here if you don't
# want to do the full Sys V style init stuff.

touch /var/lock/subsys/local
echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled
""".strip()


def test_rc_local():
    rc_local = RcLocal(context_wrap(RC_LOCAL_DATA))
    assert len(rc_local.data) == 2
    assert rc_local.data[0] == 'touch /var/lock/subsys/local'
    assert rc_local.get('kernel') == ['echo never > /sys/kernel/mm/redhat_transparent_hugepage/enabled']
