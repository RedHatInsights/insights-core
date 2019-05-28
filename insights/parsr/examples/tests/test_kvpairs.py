from insights.parsr.examples.kvpairs import loads

DATA = """
# this is a config file
a = 15
b = a string
valueless
d = 1.14

# another section
+valueless  # no value
e = hello   # a value
#
"""


def test_kvpairs():
    d = loads(DATA)
    assert d
    assert d["a"].value == 15
    assert d["b"].value == "a string"
    assert d["valueless"].value is None
    assert d["d"].value == 1.14
    assert d["+valueless"].value is None
    assert d["e"].value == "hello"
