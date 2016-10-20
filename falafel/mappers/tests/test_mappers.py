from collections import OrderedDict
from falafel.mappers import split_kv_pairs

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
