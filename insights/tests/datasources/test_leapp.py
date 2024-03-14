import json
import pytest

try:
    from unittest.mock import patch
    builtin_open = "builtins.open"
except Exception:
    from mock import patch
    builtin_open = "__builtin__.open"

from os import path

from insights.core.exceptions import SkipComponent, ContentException
from insights.specs.datasources.leapp import leapp_report, migration_results


with open(path.join(path.dirname(__file__), 'leapp-report.json'), 'r') as fp:
    LEAPP_REPORT_OK = json.load(fp)

with open(path.join(path.dirname(__file__), 'leapp-report.ret'), 'r') as fp:
    LEAPP_REPORT_RESULT = fp.readlines()

LEAPP_REPORT_NG_1 = json.loads("""
{ "entries":[
  {
    "a": "B"
  }
 ]
}
""".strip())

LEAPP_REPORT_NG_2 = MIGRATION_RESULTS_NG_2 = json.loads("{}")

MIGRATION_RESULTS_OK_1 = json.loads("""
{
   "activities": [
     {
       "activity": "preupgrade",
       "activity_ended": "2023-08-22T08:56:26.971009Z",
       "activity_started": "2023-08-22T08:55:47.798008Z",
       "env": {
         "LEAPP_COMMON_FILES": ":/etc/leapp/repos.d/system_upgrade/common/files:/etc/leapp/repos.d/system_upgrade/el8toel9/files",
         "LEAPP_COMMON_TOOLS": ":/etc/leapp/repos.d/system_upgrade/common/tools:/etc/leapp/repos.d/system_upgrade/el8toel9/tools",
         "LEAPP_CURRENT_PHASE": "FactsCollection",
         "LEAPP_DEBUG": "0",
         "LEAPP_EXECUTION_ID": "1edff870-626d-41ba-854c-8f9dc8f20dc3",
         "LEAPP_EXPERIMENTAL": "0",
         "LEAPP_HOSTNAME": "kvm-04-guest17.lab.eng.rdu2.redhat.com",
         "LEAPP_IPU_IN_PROGRESS": "8to9",
         "LEAPP_NO_RHSM": "0",
         "LEAPP_UNSUPPORTED": "0",
         "LEAPP_UPGRADE_PATH_FLAVOUR": "default",
         "LEAPP_UPGRADE_PATH_TARGET_RELEASE": "9.0",
         "LEAPP_VERBOSE": "0"
       },
       "executed": "/usr/bin/leapp preupgrade",
       "packages": [
         {
           "nevra": "leapp-0.15.1-1.el8_6.2.noarch",
           "signature": "RSA/SHA256, Mon 13 Mar 2023 12:08:57 PM EDT, Key ID 199e2f91fd431d51"
         },
         {
           "nevra": "python3-leapp-0.15.1-1.el8_6.2.noarch",
           "signature": "RSA/SHA256, Mon 13 Mar 2023 12:08:58 PM EDT, Key ID 199e2f91fd431d51"
         },
         {
           "nevra": "leapp-upgrade-el8toel9-0.18.0-1.el8_6.3.noarch",
           "signature": "RSA/SHA256, Mon 05 Jun 2023 12:54:10 PM EDT, Key ID 199e2f91fd431d51"
         },
         {
           "nevra": "leapp-deps-0.15.1-1.el8_6.2.noarch",
           "signature": "RSA/SHA256, Mon 13 Mar 2023 12:08:58 PM EDT, Key ID 199e2f91fd431d51"
         },
         {
           "nevra": "leapp-upgrade-el8toel9-deps-0.18.0-1.el8_6.3.noarch",
           "signature": "RSA/SHA256, Mon 05 Jun 2023 12:54:11 PM EDT, Key ID 199e2f91fd431d51"
         }
       ],
       "run_id": "1edff870-626d-41ba-854c-8f9dc8f20dc3",
       "source_os": "Red Hat Enterprise Linux 8.6",
       "success": false,
       "target_os": "Red Hat Enterprise Linux 9.0",
       "version": "0.15.1"
     },
     {
       "activity": "upgrade",
       "activity_ended": "2023-08-22T09:21:40.483395Z",
       "activity_started": "2023-08-22T09:13:50.876865Z",
       "env": {
         "LEAPP_COMMON_FILES": ":/etc/leapp/repos.d/system_upgrade/common/files:/etc/leapp/repos.d/system_upgrade/el8toel9/files",
         "LEAPP_COMMON_TOOLS": ":/etc/leapp/repos.d/system_upgrade/common/tools:/etc/leapp/repos.d/system_upgrade/el8toel9/tools",
         "LEAPP_CURRENT_PHASE": "InterimPreparation",
         "LEAPP_DEBUG": "0",
         "LEAPP_EXECUTION_ID": "b3baa3f4-de86-4c4b-a7f3-bbe271207efd",
         "LEAPP_EXPERIMENTAL": "0",
         "LEAPP_HOSTNAME": "kvm-04-guest17.lab.eng.rdu2.redhat.com",
         "LEAPP_IPU_IN_PROGRESS": "8to9",
         "LEAPP_NO_RHSM": "0",
         "LEAPP_UNSUPPORTED": "0",
         "LEAPP_UPGRADE_PATH_FLAVOUR": "default",
         "LEAPP_UPGRADE_PATH_TARGET_RELEASE": "9.0",
         "LEAPP_VERBOSE": "0"
       },
       "executed": "/usr/bin/leapp upgrade",
       "packages": [
         {
           "nevra": "leapp-0.15.1-1.el8_6.2.noarch",
           "signature": "RSA/SHA256, Mon 13 Mar 2023 12:08:57 PM EDT, Key ID 199e2f91fd431d51"
         },
         {
           "nevra": "python3-leapp-0.15.1-1.el8_6.2.noarch",
           "signature": "RSA/SHA256, Mon 13 Mar 2023 12:08:58 PM EDT, Key ID 199e2f91fd431d51"
         },
         {
           "nevra": "leapp-upgrade-el8toel9-0.18.0-1.el8_6.3.noarch",
           "signature": "RSA/SHA256, Mon 05 Jun 2023 12:54:10 PM EDT, Key ID 199e2f91fd431d51"
         },
         {
           "nevra": "leapp-deps-0.15.1-1.el8_6.2.noarch",
           "signature": "RSA/SHA256, Mon 13 Mar 2023 12:08:58 PM EDT, Key ID 199e2f91fd431d51"
         },
         {
           "nevra": "leapp-upgrade-el8toel9-deps-0.18.0-1.el8_6.3.noarch",
           "signature": "RSA/SHA256, Mon 05 Jun 2023 12:54:11 PM EDT, Key ID 199e2f91fd431d51"
         }
       ],
       "run_id": "b3baa3f4-de86-4c4b-a7f3-bbe271207efd",
       "source_os": "Red Hat Enterprise Linux 8.6",
       "success": true,
       "target_os": "Red Hat Enterprise Linux 9.0",
       "version": "0.15.1"
     }
  ]
}""".strip())

MIGRATION_RESULTS_OK_2 = json.loads("""
{
  "activities": [
    {
      "executed": "/usr/bin/convert2rhel analyze -y",
      "run_id": "null",
      "packages": [
        {
          "nevra": "0:convert2rhel-1.6.1-1.el7.noarch",
          "signature": "RSA/SHA256, Wed Dec 13 19:27:28 2023, Key ID 199e2f91fd431d51"
        }
      ],
      "target_os": "null",
      "success": true,
      "activity_ended": "2024-03-01T07:44:15.814899Z",
      "version": "1",
      "env": {},
      "activity": "analysis",
      "source_os": {
        "version": "7.9",
        "id": "Core",
        "name": "CentOS Linux"
      },
      "activity_started": "2024-03-01T07:37:39.278478Z"
    }
  ]
}""".strip())

MIGRATION_RESULTS_RET_1 = """
[
  {
    "activity": "preupgrade",
    "activity_ended": "2023-08-22T08:56:26.971009Z",
    "activity_started": "2023-08-22T08:55:47.798008Z",
    "env": {
         "LEAPP_COMMON_FILES": ":/etc/leapp/repos.d/system_upgrade/common/files:/etc/leapp/repos.d/system_upgrade/el8toel9/files",
         "LEAPP_COMMON_TOOLS": ":/etc/leapp/repos.d/system_upgrade/common/tools:/etc/leapp/repos.d/system_upgrade/el8toel9/tools",
         "LEAPP_CURRENT_PHASE": "FactsCollection",
         "LEAPP_DEBUG": "0",
         "LEAPP_EXECUTION_ID": "1edff870-626d-41ba-854c-8f9dc8f20dc3",
         "LEAPP_EXPERIMENTAL": "0",
         "LEAPP_HOSTNAME": "kvm-04-guest17.lab.eng.rdu2.redhat.com",
         "LEAPP_IPU_IN_PROGRESS": "8to9",
         "LEAPP_NO_RHSM": "0",
         "LEAPP_UNSUPPORTED": "0",
         "LEAPP_UPGRADE_PATH_FLAVOUR": "default",
         "LEAPP_UPGRADE_PATH_TARGET_RELEASE": "9.0",
         "LEAPP_VERBOSE": "0"
    },
    "run_id": "1edff870-626d-41ba-854c-8f9dc8f20dc3",
    "source_os": "Red Hat Enterprise Linux 8.6",
    "success": false,
    "target_os": "Red Hat Enterprise Linux 9.0",
    "version": "0.15.1"
  },
  {
    "activity": "upgrade",
    "activity_ended": "2023-08-22T09:21:40.483395Z",
    "activity_started": "2023-08-22T09:13:50.876865Z",
    "env": {
         "LEAPP_COMMON_FILES": ":/etc/leapp/repos.d/system_upgrade/common/files:/etc/leapp/repos.d/system_upgrade/el8toel9/files",
         "LEAPP_COMMON_TOOLS": ":/etc/leapp/repos.d/system_upgrade/common/tools:/etc/leapp/repos.d/system_upgrade/el8toel9/tools",
         "LEAPP_CURRENT_PHASE": "InterimPreparation",
         "LEAPP_DEBUG": "0",
         "LEAPP_EXECUTION_ID": "b3baa3f4-de86-4c4b-a7f3-bbe271207efd",
         "LEAPP_EXPERIMENTAL": "0",
         "LEAPP_HOSTNAME": "kvm-04-guest17.lab.eng.rdu2.redhat.com",
         "LEAPP_IPU_IN_PROGRESS": "8to9",
         "LEAPP_NO_RHSM": "0",
         "LEAPP_UNSUPPORTED": "0",
         "LEAPP_UPGRADE_PATH_FLAVOUR": "default",
         "LEAPP_UPGRADE_PATH_TARGET_RELEASE": "9.0",
         "LEAPP_VERBOSE": "0"
    },
    "run_id": "b3baa3f4-de86-4c4b-a7f3-bbe271207efd",
    "source_os": "Red Hat Enterprise Linux 8.6",
    "success": true,
    "target_os": "Red Hat Enterprise Linux 9.0",
    "version": "0.15.1"
  }
]
""".strip()

MIGRATION_RESULTS_RET_2 = """
[
  {
      "activity": "analysis",
      "activity_ended": "2024-03-01T07:44:15.814899Z",
      "activity_started": "2024-03-01T07:37:39.278478Z",
      "env": {},
      "run_id": "null",
      "source_os": {
          "version": "7.9",
          "id": "Core",
          "name": "CentOS Linux"
      },
      "success": true,
      "target_os": "null",
      "version": "1"
  }
]
""".strip()


MIGRATION_RESULTS_NG_1 = json.loads("""
{ "activities":[
  {
    "a": "B"
  }
 ]
}
""".strip())


@patch("json.load", return_value=LEAPP_REPORT_OK)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_leapp_report_ok(m_open, m_isfile, m_load):
    result = leapp_report({})
    result_json = json.loads(''.join(result.content).strip())
    expected_json = json.loads(''.join(LEAPP_REPORT_RESULT).strip())
    for ret in result_json:
        assert ret in expected_json


@patch("json.load", return_value=LEAPP_REPORT_NG_1)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_leapp_report_nothing(m_open, m_isfile, m_load):
    with pytest.raises(SkipComponent) as ce:
        leapp_report({})
    assert "Nothing" in str(ce)


@patch("json.load", return_value=LEAPP_REPORT_NG_2)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_leapp_report_ng_2(m_open, m_isfile, m_load):
    with pytest.raises(ContentException) as ce:
        leapp_report({})
    assert "Nothing" in str(ce)


@patch("os.path.isfile", return_value=False)
def test_leapp_report_no_file(isfile):
    with pytest.raises(SkipComponent):
        leapp_report({})


@patch("json.load", return_value=MIGRATION_RESULTS_OK_1)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_leapp_migration_results_ok(m_open, m_isfile, m_load):
    result = migration_results({})
    result_json = json.loads(''.join(result.content).strip())
    expected_json = json.loads(''.join(MIGRATION_RESULTS_RET_1).strip())
    for ret in result_json:
        assert ret in expected_json


@patch("json.load", return_value=MIGRATION_RESULTS_OK_2)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_c2r_migration_results_ok(m_open, m_isfile, m_load):
    result = migration_results({})
    result_json = json.loads(''.join(result.content).strip())
    expected_json = json.loads(''.join(MIGRATION_RESULTS_RET_2).strip())
    for ret in result_json:
        assert ret in expected_json


@patch("json.load", return_value=MIGRATION_RESULTS_NG_1)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_leapp_migration_results_nothing(m_open, m_isfile, m_load):
    with pytest.raises(SkipComponent) as ce:
        migration_results({})
    assert "Nothing" in str(ce)


@patch("json.load", return_value=MIGRATION_RESULTS_NG_2)
@patch("os.path.isfile", return_value=True)
@patch(builtin_open)
def test_leapp_migration_results_ng_2(m_open, m_isfile, m_load):
    with pytest.raises(ContentException) as ce:
        migration_results({})
    assert "Nothing" in str(ce)


@patch("os.path.isfile", return_value=False)
def test_leapp_migration_results_no_file(isfile):
    with pytest.raises(SkipComponent):
        migration_results({})
