import types

try:
    import cjson
    json_encode = cjson.encode
    json_decode = cjson.decode
except ImportError:
    import json
    json_encode = json.dumps
    json_decode = json.loads


class Marshaller(object):
    """
    Marshalling class that restructures mapper output
    for use in the reduce phase.
    """

    def marshal(self, o, use_value_list=False, shared=False):
        """
        Packages the return from a mapper for easy use in the reducer.
        """

        type_ = type(o)

        if o is None:
            return
        elif type_ == types.DictType:
            if use_value_list:
                for k, v in o.items():
                    o[k] = [v]
            return o
        elif type_ in types.StringTypes:
            if use_value_list:
                return {o: [True]}
            else:
                return {o: True}
        else:
            if shared:
                return [o] if use_value_list else o
            else:
                raise TypeError("Marshaller doesn't support given type %s" % type_)

    def unmarshal(self, doc):
        return doc

    def unmarshal_to_context(self, data, func_keys=False):
        """
        Given a list of marshalled mapper output, returns a single dictionary
        for use with a reducer
        """
        if func_keys:
            from falafel.core import plugins
        context = {}
        for t in data:
            for k, v in self.unmarshal(t).items():
                if func_keys:
                    k = plugins.MAPPER_FUNCS[k]
                if k not in context:
                    context[k] = v
                else:
                    cur = context[k]
                    if type(cur) != types.ListType:
                        context[k] = [cur]
                    if type(v) != types.ListType:
                        context[k].append(v)
                    else:
                        context[k].extend(v)

        return context


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
unmarshal_to_context = INSTANCE.unmarshal_to_context
