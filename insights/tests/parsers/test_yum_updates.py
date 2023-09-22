from insights.parsers import yum_updates
from insights.tests import context_wrap
import doctest

YUM_UPDATES_INPUT = """{
      "releasever": "8",
      "basearch": "x86_64",
      "update_list": {
        "NetworkManager-1:1.22.8-4.el8.x86_64": {
          "available_updates": [
            {
              "package": "NetworkManager-1:1.22.8-5.el8_2.x86_64",
              "repository": "rhel-8-for-x86_64-baseos-rpms",
              "basearch": "x86_64",
              "releasever": "8",
              "erratum": "RHSA-2020:3011"
            }
          ]
        }
      },
      "metadata_time": "2021-01-01T09:39:45Z"
    }
"""


def test_yum_updates():
    info = yum_updates.YumUpdates(context_wrap(YUM_UPDATES_INPUT))
    assert info is not None
    assert len(info.updates) == 1
    assert len(info.updates["NetworkManager-1:1.22.8-4.el8.x86_64"]["available_updates"]) == 1


def test_yum_updates_docs():
    env = {
        'updates': yum_updates.YumUpdates(context_wrap(YUM_UPDATES_INPUT)),
    }
    failed, total = doctest.testmod(yum_updates, globs=env)
    assert failed == 0
