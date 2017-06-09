import pytest
from collections import OrderedDict
from insights.parsers import split_kv_pairs, unsplit_lines, parse_fixed_table, calc_offset, optlist_to_dict


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


SPLIT_TEST_1 = """
# Comment line

  keyword1 = value1   # Inline comments

  # Comment indented
  keyword3     # Key with no separator
  keyword2 = value2a=True, value2b=100M

""".strip()

SPLIT_TEST_1_OD = OrderedDict([
    ('keyword1', 'value1'),
    ('keyword3', ''),
    ('keyword2', 'value2a=True, value2b=100M')
])

SPLIT_TEST_2 = """
@ Comment line

  keyword1: value1   @ Inline comments
  keyword2 : value2a=True, value2b=100M

  @ Comment indented
  keyword3     @ Key with no separator
""".strip()


def test_split_kv_pairs():
    kv_pairs = split_kv_pairs(SPLIT_TEST_1.splitlines())
    assert len(kv_pairs) == 2
    assert kv_pairs == {
        'keyword1': 'value1',
        'keyword2': 'value2a=True, value2b=100M'
    }

    kv_pairs = split_kv_pairs(SPLIT_TEST_1.splitlines(), filter_string='value2')
    assert len(kv_pairs) == 1
    assert kv_pairs == {
        'keyword2': 'value2a=True, value2b=100M'
    }

    kv_pairs = split_kv_pairs(SPLIT_TEST_1.splitlines(), use_partition=True)
    assert len(kv_pairs) == 3
    assert kv_pairs == {
        'keyword1': 'value1',
        'keyword2': 'value2a=True, value2b=100M',
        'keyword3': ''
    }

    kv_pairs = split_kv_pairs(SPLIT_TEST_1.splitlines(), use_partition=True, ordered=True)
    assert len(kv_pairs) == 3
    assert kv_pairs == SPLIT_TEST_1_OD

    kv_pairs = split_kv_pairs(SPLIT_TEST_2.splitlines(), comment_char='@', split_on=':')
    assert len(kv_pairs) == 2
    assert kv_pairs == {
        'keyword1': 'value1',
        'keyword2': 'value2a=True, value2b=100M'
    }

    kv_pairs = split_kv_pairs(SPLIT_TEST_2.splitlines(), comment_char='@', split_on=':', filter_string='value2')
    assert len(kv_pairs) == 1
    assert kv_pairs == {
        'keyword2': 'value2a=True, value2b=100M'
    }

    kv_pairs = split_kv_pairs(SPLIT_TEST_2.splitlines(), comment_char='@', split_on=':', use_partition=True)
    assert len(kv_pairs) == 3
    assert kv_pairs == {
        'keyword1': 'value1',
        'keyword2': 'value2a=True, value2b=100M',
        'keyword3': ''
    }


SPLIT_LINES = """
Line one
Line two part 1 \\
         line two part 2\\
         line two part 3
Line three
Continued on \
last line\\""".strip()
SPLIT_LINES_2 = """
Line one
Line two part 1 ^
         line two part 2^
         line two part 3
Line three
""".strip()


def test_unsplit_lines():
    lines = list(unsplit_lines(SPLIT_LINES.splitlines()))
    assert len(lines) == 4
    assert lines[0] == 'Line one'
    assert lines[1] == 'Line two part 1          line two part 2         line two part 3'
    assert lines[2] == 'Line three'
    assert lines[3] == 'Continued on last line'

    lines = list(unsplit_lines(SPLIT_LINES_2.splitlines(), cont_char='^'))
    assert len(lines) == 3
    assert lines[0] == 'Line one'
    assert lines[1] == 'Line two part 1          line two part 2         line two part 3'
    assert lines[2] == 'Line three'


OFFSET_CONTENT_1 = """
  data 1 line
data 2 line
""".strip()

OFFSET_CONTENT_2 = """
#
Warning line
Error line
    data 1 line
    data 2 line
Trailing line

Blank line above
Another trailing line
    Yet another trailing line
    Yet yet another trailing line
""".strip()


def test_calc_offset():
    assert calc_offset(OFFSET_CONTENT_1.splitlines(), target=[]) == 0
    assert calc_offset(OFFSET_CONTENT_1.splitlines(), target=[None]) == 0
    assert calc_offset(OFFSET_CONTENT_1.splitlines(), target=['data ']) == 0
    with pytest.raises(ValueError):
        calc_offset(OFFSET_CONTENT_1.splitlines(), target=['xdata '])
    with pytest.raises(ValueError):
        calc_offset(OFFSET_CONTENT_1.splitlines(),
                    target=['data '],
                    invert_search=True)
    assert calc_offset(OFFSET_CONTENT_1.splitlines(),
                       target=['Trailing', 'Blank', 'Another '],
                       invert_search=True) == 0
    assert calc_offset(OFFSET_CONTENT_2.splitlines(), target=[]) == 0
    assert calc_offset(OFFSET_CONTENT_2.splitlines(), target=['data ']) == 3
    assert calc_offset(reversed(OFFSET_CONTENT_2.splitlines()),
                       target=['Trailing', 'Blank', 'Another ', 'Yet'],
                       invert_search=True) == 6


FIXED_CONTENT_1 = """
Column1    Column2    Column3
data1      data 2     data   3
     data4 data5      data6
data     7            data   9
""".strip()

FIXED_CONTENT_1A = """
    WARNING
    Column1    Column2    Column3
    data1      data 2     data   3
         data4 data5      data6
    data     7            data   9
""".strip()

FIXED_CONTENT_1B = """
Column1    Column2    Column3
data1      data 2
data4      data5      data6
  data   7            data   9
""".strip()

FIXED_CONTENT_2 = """
WARNING WARNING WARNING
 Some message
Another message
Column1    Column2    Column3
data1      data 2     data   3
     data4 data5      data6
data     7            data   9
""".strip()

FIXED_CONTENT_3 = """
WARNING WARNING WARNING
 Some message
Another message
Column1    Column2    Column3
data1      data 2     data   3
     data4 data5      data6
data     7            data   9
Trailing non-data line
 Another trailing non-data line
""".strip()

FIXED_CONTENT_4 = """
WARNING WARNING WARNING
 Some message
Another message
Column1    Column 2    Column 3
data1      data 2      data   3
     data4 data5       data6
data     7             data   9
data10
Trailing non-data line
 Another trailing non-data line
""".strip()


def test_parse_fixed_table():
    data = parse_fixed_table(FIXED_CONTENT_1.splitlines())
    assert len(data) == 3
    assert data[0] == {'Column1': 'data1', 'Column2': 'data 2', 'Column3': 'data   3'}
    assert data[1] == {'Column1': 'data4', 'Column2': 'data5', 'Column3': 'data6'}
    assert data[2] == {'Column1': 'data     7', 'Column2': '', 'Column3': 'data   9'}

    data = parse_fixed_table(FIXED_CONTENT_1A.splitlines(), heading_ignore=['Column1 '])
    assert len(data) == 3
    assert data[0] == {'Column1': 'data1', 'Column2': 'data 2', 'Column3': 'data   3'}
    assert data[1] == {'Column1': 'data4', 'Column2': 'data5', 'Column3': 'data6'}
    assert data[2] == {'Column1': 'data     7', 'Column2': '', 'Column3': 'data   9'}

    data = parse_fixed_table(FIXED_CONTENT_1B.splitlines())
    assert len(data) == 3
    assert data[0] == {'Column1': 'data1', 'Column2': 'data 2', 'Column3': ''}
    assert data[1] == {'Column1': 'data4', 'Column2': 'data5', 'Column3': 'data6'}
    assert data[2] == {'Column1': 'data   7', 'Column2': '', 'Column3': 'data   9'}

    data = parse_fixed_table(FIXED_CONTENT_2.splitlines(), heading_ignore=['Column1 '])
    assert len(data) == 3
    assert data[0] == {'Column1': 'data1', 'Column2': 'data 2', 'Column3': 'data   3'}
    assert data[1] == {'Column1': 'data4', 'Column2': 'data5', 'Column3': 'data6'}
    assert data[2] == {'Column1': 'data     7', 'Column2': '', 'Column3': 'data   9'}

    data = parse_fixed_table(FIXED_CONTENT_3.splitlines(),
                             heading_ignore=['Column1 '],
                             trailing_ignore=['Trailing', 'Another'])
    assert len(data) == 3
    assert data[0] == {'Column1': 'data1', 'Column2': 'data 2', 'Column3': 'data   3'}
    assert data[1] == {'Column1': 'data4', 'Column2': 'data5', 'Column3': 'data6'}
    assert data[2] == {'Column1': 'data     7', 'Column2': '', 'Column3': 'data   9'}

    data = parse_fixed_table(FIXED_CONTENT_4.splitlines(),
                             heading_ignore=['Column1 '],
                             header_substitute=[('Column 2', 'Column_2'), ('Column 3', 'Column_3')],
                             trailing_ignore=['Trailing', 'Another'])
    assert len(data) == 4
    assert data[0] == {'Column1': 'data1', 'Column_2': 'data 2', 'Column_3': 'data   3'}
    assert data[1] == {'Column1': 'data4', 'Column_2': 'data5', 'Column_3': 'data6'}
    assert data[2] == {'Column1': 'data     7', 'Column_2': '', 'Column_3': 'data   9'}
    assert data[3] == {'Column1': 'data10', 'Column_2': '', 'Column_3': ''}

    # Test that if we search for trailing data that is always found, then we
    # should get the whole thing parsed as a table from the header line
    data = parse_fixed_table(
        ['foo' + line for line in FIXED_CONTENT_4.splitlines()],
        heading_ignore=['fooColumn1 '],
        header_substitute=[('fooColumn1', 'Column1'), ('Column 2', 'Column_2'), ('Column 3', 'Column_3')],
        trailing_ignore=['foo']
    )
    assert len(data) == 6
    assert data[4] == {'Column1': 'fooTrailing', 'Column_2': 'non-data li', 'Column_3': 'ne'}
    assert data[5] == {'Column1': 'foo Another', 'Column_2': 'trailing no', 'Column_3': 'n-data line'}
