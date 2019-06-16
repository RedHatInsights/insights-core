#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
