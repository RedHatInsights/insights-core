import unittest

from falafel.console.package import MetaPattern

METADATA = '''
It's a starting of the string
dummy: value
{key}: random text
pretext {key}: {value}
{key}: {value}
humpty: dumpty
It's a end of the string
'''.strip()


class TestMetaPattern(unittest.TestCase):

    def test___init__string(self):
        mp = MetaPattern('foo', 'bar')
        self.assertIsInstance(mp, MetaPattern)
        self.assertEqual(mp.key, 'foo')
        self.assertListEqual(mp.values, ['bar'])

    def test___init__array(self):
        mp = MetaPattern('foo', ['bar1', 'bar2'])
        self.assertIsInstance(mp, MetaPattern)
        self.assertEqual(mp.key, 'foo')
        self.assertListEqual(mp.values, ['bar1', 'bar2'])

    def test_set_pattern_string(self):
        mp = MetaPattern('foo', 'bar')
        mp.set_pattern()
        self.assertEqual(mp.pattern.pattern, r'^(foo): .*(bar).*')

    def test_set_pattern_array(self):
        mp = MetaPattern('foo', ['bar1', 'bar2'])
        mp.set_pattern()
        self.assertEqual(mp.pattern.pattern, r'^(foo): .*(bar1|bar2).*')

    def test_present_string(self):
        key = 'foo'
        value = 'bar'
        metadata = METADATA.format(key=key, value=value)
        mp = MetaPattern(key, value)
        is_present = mp.present(metadata)
        self.assertTrue(is_present)

    def test_present_string_neg(self):
        key = 'foo'
        value = 'bar'
        metadata = METADATA.format(key=key, value=value)
        mp = MetaPattern(key, 'var')
        is_present = mp.present(metadata)
        self.assertFalse(is_present)

    def test_present_array(self):
        key = 'foo'
        text = 'bar car dar ear'
        key_to_look = 'car'
        metadata = METADATA.format(key=key, value=text)
        mp = MetaPattern(key, key_to_look)
        is_present = mp.present(metadata)
        self.assertTrue(is_present)

    def test_present_array_neg(self):
        key = 'foo'
        text = 'bar car dar ear'
        key_to_look = 'far'
        metadata = METADATA.format(key=key, value=text)
        mp = MetaPattern(key, key_to_look)
        is_present = mp.present(metadata)
        self.assertFalse(is_present)
