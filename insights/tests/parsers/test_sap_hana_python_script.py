import pytest
import doctest

from insights.parsers import SkipException, sap_hana_python_script
from insights.parsers.sap_hana_python_script import HanaLandscape
from insights.tests import context_wrap

LANDSCAPE_SCALE_UP = """
| Host   | Host   | Host   | Failover | Remove | Storage   | Failover     | Failover     | NameServer  | NameServer  | IndexServer | IndexServer |
|        | Active | Status | Status   | Status | Partition | Config Group | Actual Group | Config Role | Actual Role | Config Role | Actual Role |
| ------ | ------ | ------ | -------- | ------ | --------- | ------------ | ------------ | ----------- | ----------- | ----------- | ----------- |
| node1  | yes    | ok     |          |        |         1 | default      | default      | master 1    | master      | worker      | master      |
overall host status: ok
""".strip()

LANDSCAPE_SCALE_OUT = """
| Host   | Host   | Host   | Failover | Remove | Storage   | Failover     | Failover     | NameServer  | NameServer  | IndexServer | IndexServer |
|        | Active | Status | Status   | Status | Partition | Config Group | Actual Group | Config Role | Actual Role | Config Role | Actual Role |
| ------ | ------ | ------ | -------- | ------ | --------- | ------------ | ------------ | ----------- | ----------- | ----------- | ----------- |
| node1  | yes    | info   |          |        | 0         | default      | default      | master 1    | slave       | worker      | standby     |
| node2  | yes    | ok     |          |        | 2         | default      | default      | master 2    | slave       | worker      | slave       |
| node3  | yes    | info   |          |        | 1         | default      | default      | master 3    | master      | standby     | master      |
overall host status: ok
""".strip()

LANDSCAPE_SCALE_UP_NG = """
nameserver vm37-39:30201 not responding.
nameserver vm37-39:30201 not responding.
| Host    | Host   | Host   | Failover | Remove | Storage   | Storage   | Failover | Failover | NameServer | NameServer | IndexServer | IndexServer | Host             | Host   | Worker  | Worker |
|         | Active | Status | Status   | Status | Config    | Actual    | Config   | Actual   | Config     | Actual     | Config      | Actual      | Config           | Actual | Config  | Actual |
|         |        |        |          |        | Partition | Partition | Group    | Group    | Role       | Role       | Role        | Role        | Roles            | Roles  | Groups  | Groups |
| ------- | ------ | ------ | -------- | ------ | --------- | --------- | -------- | -------- | ---------- | ---------- | ----------- | ----------- | ---------------- | ------ | ------- | ------ |
| vm37-39 | no     | error  | ?        | ?      | ?         | ?         | ?        | ?        | master 1   | ?          | worker      | ?           | worker xs_worker | ?      | default | ?      |

overall host status: error
""".strip()

LANDSCAPE_SCALE_UP_AB_1 = """
| Host   | Host   | Host   | Failover | Remove | Storage   | Failover     | Failover     | NameServer  | NameServer  | IndexServer | IndexServer |
|        | Active | Status | Status   | Status | Partition | Config Group | Actual Group | Config Role | Actual Role | Config Role | Actual Role |
| ------ | ------ | ------ | -------- | ------ | --------- | ------------ | ------------ | ----------- | ----------- | ----------- | ----------- |
""".strip()


def test_doc_examples():
    env = {'hana_sta': HanaLandscape(context_wrap(LANDSCAPE_SCALE_UP))}
    failed, total = doctest.testmod(sap_hana_python_script, globs=env)
    assert failed == 0


def test_HanaLandscape_ab():
    with pytest.raises(SkipException):
        HanaLandscape(context_wrap(LANDSCAPE_SCALE_UP_AB_1))


def test_HanaLandscape():
    d = HanaLandscape(context_wrap(LANDSCAPE_SCALE_UP))
    assert len(d) == 1
    assert d[0]['Host'] == 'node1'
    assert d[0]['Failover Config Group'] == 'default'
    assert d[0]['Failover Status'] == ''
    assert d.overall_status == 'ok'
    assert d.scale_up is True
    assert d.scale_out is False

    d = HanaLandscape(context_wrap(LANDSCAPE_SCALE_UP_NG))
    assert len(d) == 1
    assert d[0]['Host'] == 'vm37-39'
    assert d[0]['Failover Config Group'] == '?'
    assert d[0]['Failover Status'] == '?'
    assert d[0]['Host Status'] == 'error'
    assert d.overall_status == 'error'
    assert d.scale_up is True
    assert d.scale_out is False

    d = HanaLandscape(context_wrap(LANDSCAPE_SCALE_OUT))
    assert len(d) == 3
    assert d.overall_status == 'ok'
    assert d[0]['Host'] == 'node1'
    assert d[0]['Failover Config Group'] == 'default'
    assert d[0]['Failover Status'] == ''
    assert d[0]['Host Status'] == 'info'
    assert d[1]['Host'] == 'node2'
    assert d[1]['Failover Config Group'] == 'default'
    assert d[1]['Failover Status'] == ''
    assert d[1]['Host Status'] == 'ok'
    assert d[2]['Host'] == 'node3'
    assert d[2]['Failover Config Group'] == 'default'
    assert d[2]['Failover Status'] == ''
    assert d[2]['Host Status'] == 'info'
    assert d.scale_up is False
    assert d.scale_out is True
