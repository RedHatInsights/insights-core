import doctest
import pytest

from insights.core.exceptions import ContentException, SkipComponent, ParseException
from insights.parsers import ansible
from insights.tests import context_wrap

AT_INPUT_NG_CMD = """
no such file or directory: /usr/share/ansible/telemetry/telemetry.py
"""

AT_INPUT_NG_CNT = """
{"collections":{"ansible.builtin":{"resources":{"action":{"ansible.builtin.command":13}},"version":"*"}},"ansible_core":{"version":"2.18.9rc1"}}

{"collections":{"ansible.builtin":{"resources":{"action":{"ansible.builtin.command":14}},"version":"*"}},"ansible_core":{"version":"2.19.9"}}]
"""

AT_INPUT = """
{"collections":{"ansible.builtin":{"resources":{"action":{"ansible.builtin.command":13}},"version":"*"}},"ansible_core":{"version":"2.18.9rc1"}}
{"collections":{"ansible.builtin":{"resources":{"action":{"ansible.builtin.command":14}},"version":"*"}},"ansible_core":{"version":"2.19.9"}}
""".strip()


def test_ansible_telemetry():
    ret = ansible.AnsibleTelemetry(context_wrap(AT_INPUT))
    assert len(ret) == 2
    assert ret[0]['ansible_core']['version'] == '2.18.9rc1'
    assert ret[1]['collections']['ansible.builtin']['resources']['action'] == {
        'ansible.builtin.command': 14
    }

    with pytest.raises(SkipComponent):
        ansible.AnsibleTelemetry(context_wrap(""))

    with pytest.raises(ContentException):
        ansible.AnsibleTelemetry(context_wrap(AT_INPUT_NG_CMD))

    with pytest.raises(ParseException):
        ansible.AnsibleTelemetry(context_wrap(AT_INPUT_NG_CNT))


def test_doc_examples():
    env = {
        'ansible_telemetry': ansible.AnsibleTelemetry(context_wrap(AT_INPUT)),
    }
    failed, total = doctest.testmod(ansible, globs=env)
    assert failed == 0
