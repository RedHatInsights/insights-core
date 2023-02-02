import doctest

from insights.parsers import containers_policy
from insights.parsers.containers_policy import ContainersPolicy
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check

CONTAINERS_POLICY_FILE = '''
{
  "default": [
    {
      "type": "insecureAcceptAnything"
    }
  ],
  "transports": {
    "docker": {
      "registry.access.redhat.com": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
        }
      ],
      "registry.redhat.io/redhat/redhat-operator-index": [
        {
          "type": "insecureAcceptAnything"
        }
      ],
      "registry.redhat.io": [
        {
          "type": "signedBy",
          "keyType": "GPGKeys",
          "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
        }
      ]
    },
    "docker-daemon": {
      "": [
        {
          "type": "insecureAcceptAnything"
        }
      ]
    }
  }
}
'''.strip()


def test_doc_examples():
    env = {
        'containers_policy': ContainersPolicy(context_wrap(CONTAINERS_POLICY_FILE)),
    }
    failed, total = doctest.testmod(containers_policy, globs=env)
    assert failed == 0


def test_containers_policy():
    conf = ContainersPolicy(context_wrap(CONTAINERS_POLICY_FILE))
    assert len(conf["default"]) == 1
    assert conf["default"][0]["type"] == "insecureAcceptAnything"


def test_containers_policy_empty():
    assert 'Empty output.' in skip_component_check(ContainersPolicy)
