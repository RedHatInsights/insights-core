import doctest
import pytest

from insights.core.exceptions import ContentException
from insights.parsers import ansible
from insights.tests import context_wrap

AT_INPUT_NG = """
no such file or directory: /usr/share/ansible/telemetry/telemetry.py
"""

AT_INPUT = """
{
  "collections":{
    "ansible.builtin":{
      "resources":{
        "action":{
          "ansible.builtin.add_host":78,
          "ansible.builtin.uri":147,
          "ansible.builtin.set_fact":96,
          "ansible.builtin.debug":30,
          "ansible.builtin.find":2,
          "ansible.builtin.file":6,
          "ansible.builtin.template":2,
          "ansible.builtin.command":13
        },
        "connection":{
          "ansible.builtin.local":113,
          "ansible.builtin.ssh":290
        }
      },
      "version":"*"
    }
  },
  "ansible_core":{
    "version":"2.18.9rc1"
  },
  "hosts":{
    "count":44
  }
}
""".strip()


def test_ansible_telemetry():
    ret = ansible.AnsibleTelemetry(context_wrap(AT_INPUT))
    assert ret['hosts']['count'] == 44

    with pytest.raises(ContentException):
        ansible.AnsibleTelemetry(context_wrap(AT_INPUT_NG))


def test_doc_examples():
    env = {
        'ansible_telemetry': ansible.AnsibleTelemetry(context_wrap(AT_INPUT)),
    }
    failed, total = doctest.testmod(ansible, globs=env)
    assert failed == 0
