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

    def test_context_building(self):

        marshalled = [marshalling.marshal(o) for o in ("TEST_FLAG", {"foo": "bar"})]
        context = marshalling.unmarshal_to_context(marshalled)
        self.assertEquals({
            "TEST_FLAG": True,
            "foo": "bar"
        }, context)

    def test_key_merge(self):

        marshalled = [marshalling.marshal(o) for o in ("TEST_FLAG", "TEST_FLAG")]
        context = marshalling.unmarshal_to_context(marshalled)
        self.assertEquals({
            "TEST_FLAG": [True, True]
        }, context)

    def test_complex_value(self):

        marshalled = [marshalling.marshal(o) for o in (
            {"foo": {"a": 1, "b": 2}},
            {"foo": {"c": 3, "d": 4}}
        )]
        context = marshalling.unmarshal_to_context(marshalled)
        self.assertEquals({
            "foo": [{"a": 1, "b": 2}, {"c": 3, "d": 4}]
        }, context)

    def test_always_a_list(self):
        marshalled = [marshalling.marshal(o, use_value_list=True) for o in (
            {"iface": "foo"},)]
        context = marshalling.unmarshal_to_context(marshalled)
        self.assertEquals({
            "iface": ["foo"]
        }, context)

    def test_bad_returns(self):

        self.assertRaises(TypeError, marshalling.marshal, True)
        self.assertRaises(TypeError, marshalling.marshal, 1)
        self.assertRaises(TypeError, marshalling.marshal, 1.0)
        self.assertRaises(TypeError, marshalling.marshal, [])
        self.assertRaises(TypeError, marshalling.marshal, ())
        self.assertRaises(TypeError, marshalling.marshal, set())

    def test_list_of_lists(self):
        marshalled = [marshalling.marshal(o, use_value_list=True) for o in [
            {"AFFECTED_BE2NET_NIC": ("eth0", "3.704.281.0")},
            {"AFFECTED_BE2NET_NIC": ("eth1", "2.102.517.7")}
        ]]
        marshalled.append(marshalling.marshal({"AFFECTED_KERNEL": "2.6.32-431.11.2.el6.x86_64"}))
        expected = {
            "AFFECTED_KERNEL": "2.6.32-431.11.2.el6.x86_64",
            "AFFECTED_BE2NET_NIC": [["eth0", "3.704.281.0"], ["eth1", "2.102.517.7"]]
        }
        actual = marshalling.unmarshal_to_context(marshalled)
        self.assertEqual(actual, expected)

    def test_none_marshal(self):
        ma, um = mar_unmar(None)
        self.assertIsNone(um)

    def test_value_list(self):
        ma, um = mar_unmar("test", use_value_list=True)
        self.assertEqual(um, {"test": [True]})
