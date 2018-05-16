import doctest

from insights.parsers import tuned_adm
from insights.parsers.tuned_adm import TunedAdmActive
from insights.tests import context_wrap

OUTPUT1 = """
-bash: tuned-adm: command not found
"""

OUTPUT2 = """
-bash: /usr/sbin/tuned-adm: No such file or directory
"""

OUTPUT3_RHEL6 = """
Current active profile: default
Service tuned: disabled, stopped
Service ktune: disabled, stopped
"""

OUTPUT4_RHEL7 = """
Current active profile: virtual-guest
"""

OUTPUT5_RHEL7 = """
Cannot talk to Tuned daemon via DBus. Is Tuned daemon running?
It seems that tuned daemon is not running, preset profile is not activated.
Preset profile: virtual-guest
"""


def test_tuned_adm_active():
    context = TunedAdmActive(context_wrap(OUTPUT1))
    assert context.data == {}

    context = TunedAdmActive(context_wrap(OUTPUT2))
    assert context.data == {}

    context = TunedAdmActive(context_wrap(OUTPUT3_RHEL6))
    assert context.data == {
                'Current active profile': 'default',
                'Service tuned': 'disabled, stopped',
                'Service ktune': 'disabled, stopped',
            }

    context = TunedAdmActive(context_wrap(OUTPUT4_RHEL7))
    assert context.data == {
                'Current active profile': 'virtual-guest'
            }

    context = TunedAdmActive(context_wrap(OUTPUT5_RHEL7))
    assert context.data == {
                'Preset profile': 'virtual-guest'
            }


def test_tuned_adm_active_doc_examples():
    env = {
        'TunedAdmActive': TunedAdmActive,
        'tuned_adm_active': TunedAdmActive(context_wrap(OUTPUT3_RHEL6)),
    }
    failed, total = doctest.testmod(tuned_adm, globs=env)
    assert failed == 0
