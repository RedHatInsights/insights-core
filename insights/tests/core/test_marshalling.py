import unittest
from insights.core import marshalling


def mar_unmar(o, use_value_list=False):
    marshalled = marshalling.marshal(o, use_value_list)
    unmarshalled = marshalling.unmarshal(marshalled)
    return marshalled, unmarshalled


class TestMarshalling(unittest.TestCase):

    def test_string_marshal(self):
        flag = "TEST_FLAG"
        _, unmarshalled = mar_unmar(flag)
        self.assertEquals({flag: True}, unmarshalled)

    def test_dict_marshal(self):
        doc = {"foo": "bar"}
        _, unmarshalled = mar_unmar(doc)
        self.assertEquals(doc, unmarshalled)

    def test_bad_returns(self):
        self.assertRaises(TypeError, marshalling.marshal, True)
        self.assertRaises(TypeError, marshalling.marshal, 1)
        self.assertRaises(TypeError, marshalling.marshal, 1.0)
        self.assertRaises(TypeError, marshalling.marshal, [])
        self.assertRaises(TypeError, marshalling.marshal, ())
        self.assertRaises(TypeError, marshalling.marshal, set())

    def test_none_marshal(self):
        ma, um = mar_unmar(None)
        self.assertIsNone(um)

    def test_value_list(self):
        ma, um = mar_unmar("test", use_value_list=True)
        self.assertEqual(um, {"test": [True]})
