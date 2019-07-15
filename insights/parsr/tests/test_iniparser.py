from insights.parsr.iniparser import parse_doc


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
