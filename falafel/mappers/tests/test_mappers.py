from collections import OrderedDict
from falafel.mappers import split_kv_pairs, unsplit_lines

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
""".strip()
SPLIT_LINES_2 = """
Line one
Line two part 1 ^
         line two part 2^
         line two part 3
Line three
""".strip()


def test_unsplit_lines():
    lines = list(unsplit_lines(SPLIT_LINES.splitlines()))
    assert len(lines) == 3
    assert lines[0] == 'Line one'
    assert lines[1] == 'Line two part 1          line two part 2         line two part 3'
    assert lines[2] == 'Line three'

    lines = list(unsplit_lines(SPLIT_LINES_2.splitlines(), cont_char='^'))
    assert len(lines) == 3
    assert lines[0] == 'Line one'
    assert lines[1] == 'Line two part 1          line two part 2         line two part 3'
    assert lines[2] == 'Line three'
