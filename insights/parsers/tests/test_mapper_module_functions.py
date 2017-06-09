from insights.parsers import optlist_to_dict, unsplit_lines


def test_optlist_standard():
    d = optlist_to_dict('key1,key2=val2,key1=val1,key3')
    assert sorted(d.keys()) == sorted(['key1', 'key2', 'key3'])
    assert d['key1'] == 'val1'
    assert d['key2'] == 'val2'
    assert d['key3'] is True


def test_optlist_no_vals():
    d = optlist_to_dict('key1,key2=val2,key1=val1,key3', kv_sep=None)
    assert sorted(d.keys()) == sorted(['key1', 'key1=val1', 'key2=val2', 'key3'])
    assert d['key1'] is True
    assert d['key1=val1'] is True
    assert d['key2=val2'] is True
    assert d['key3'] is True


def test_unsplit_lines():
    lines = """
Not continued
Continued on \
next line
Continued on \
last line\\"""

    l = list(unsplit_lines(lines.splitlines()))
    assert l == ["", "Not continued", "Continued on next line", "Continued on last line"]
