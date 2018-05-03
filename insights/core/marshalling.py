try:
    import cjson
    json_encode = cjson.encode
    json_decode = cjson.decode
except ImportError:
    import json
    json_encode = json.dumps
    json_decode = json.loads

import six


class Marshaller(object):
    """
    Marshalling class that restructures parser output
    for use in the reduce phase.
    """

    def marshal(self, o, use_value_list=False):
        """
        Packages the return from a parser for easy use in a rule.
        """

        if o is None:
            return
        elif isinstance(o, dict):
            if use_value_list:
                for k, v in o.items():
                    o[k] = [v]
            return o
        elif isinstance(o, six.string_types):
            if use_value_list:
                return {o: [True]}
            else:
                return {o: True}
        else:
            raise TypeError("Marshaller doesn't support given type %s" % type(o))

    def unmarshal(self, doc):
        return doc


class JsonMarshaller(Marshaller):
    """
    Marshalling class that json encodes/decodes
    """

    def marshal(self, o, use_value_list=False):
        return json_encode(super(JsonMarshaller, self).marshal(o, use_value_list))

    def unmarshal(self, doc):
        return json_decode(doc)


INSTANCE = JsonMarshaller()
marshal = INSTANCE.marshal
unmarshal = INSTANCE.unmarshal
