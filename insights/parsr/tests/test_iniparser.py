# coding:UTF-8
from insights.parsr.iniparser import parse_doc
from insights.parsr.query import last
from six import PY2


DATA = """
[DEFAULT]
trooper_guns = miss

[global]
logging=debug
log=/var/logs/sample.log

# Keep this info secret
[secret_stuff]
username=dvader
password=luke_is_my_son

[facts]
major_vulnerability=ray-shielded particle exhaust vent
vader = definitely Luke's
    father

[settings]
music=The Imperial March
color=blue
#blah
color=black
accuracy=0
banks=0 1 2

[novalue]
the_force

""".strip()

DATA_UNICODE_TEST = """
[global]
secret-name = "vsphere-creds"
secret-namespace = kube-system
insecure-flag = 1

[workspace]
datacenter = 1-测试部
folder = "/1-测试部/xxxxxxxxx"
""".strip()


def test_iniparser():
    res = parse_doc(DATA, None)
    assert len(res) == 5


def test_hanging_indent():
    res = parse_doc(DATA, None)
    assert res["facts"]["vader"][0].value == "definitely Luke's father"


def test_defaults():
    res = parse_doc(DATA, None)
    assert res["facts"]["trooper_guns"][0].value == "miss"


def test_multiple_values():
    res = parse_doc(DATA, None)
    assert len(res["settings"]["color"]) == 2
    assert res["settings"]["accuracy"][0].value == "0"
    assert res["settings"]["banks"][0].value == "0 1 2"


def test_no_value():
    res = parse_doc(DATA, None)
    assert res["novalue"]["the_force"][0].value is None


def test_unicode():
    res = parse_doc(DATA_UNICODE_TEST, None)
    assert res["global"]["insecure-flag"][last].value == "1"
    assert res["global"]["secret-name"][last].value == '"vsphere-creds"'
    assert res["global"]["secret-namespace"][last].value == "kube-system"

    if PY2:
        assert res["workspace"]["datacenter"][last].value == "1-?????????"
        assert res["workspace"]["folder"][last].value == '"/1-?????????/xxxxxxxxx"'
    else:
        assert res["workspace"]["datacenter"][last].value == "1-???"
        assert res["workspace"]["folder"][last].value == '"/1-???/xxxxxxxxx"'
