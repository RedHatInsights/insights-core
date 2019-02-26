from parsr.examples.iniparser import loads


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
color=black
"""


def test_iniparser():
    res = loads(DATA)
    assert len(res) == 5


def test_hanging_indent():
    res = loads(DATA)
    assert res["facts"]["vader"] == "definitely Luke's father"


def test_defaults():
    res = loads(DATA)
    assert res["facts"]["trooper_guns"] == "miss"


def test_multiple_values():
    res = loads(DATA)
    assert len(res["settings"]["color"]) == 2
