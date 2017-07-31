import json as ser
import logging
import os

from insights.core import dr

log = logging.getLogger(__name__)

SERIALIZERS = {}
DESERIALIZERS = {}


def serializer(_type):
    """ Decorator for serializers."""

    def inner(func):
        if _type in SERIALIZERS:
            msg = "%s already has a serializer registered: %s"
            raise Exception(msg % (dr.get_name(_type), dr.get_name(SERIALIZERS[_type])))
        SERIALIZERS[_type] = func
        return func
    return inner


def deserializer(_type):
    """ Decorator for deserializers."""

    def inner(func):
        if _type in DESERIALIZERS:
            msg = "%s already has a deserializer registered: %s"
            raise Exception(msg % (dr.get_name(_type), dr.get_name(DESERIALIZERS[_type])))
        DESERIALIZERS[_type] = func
        return func
    return inner


def get_serializer(obj):
    """ Get a registered serializer for the given object.

        This function walks the mro of obj looking for serializers.
        Returns None if no valid serializer is found.
    """
    for o in type(obj).mro():
        if o not in SERIALIZERS:
            continue
        return lambda x: {"type": dr.get_name(o), "object": SERIALIZERS[o](x)}
    return lambda x: {"type": "Unknown", "object": x}


def get_deserializer(name):
    """ Returns a deserializer based on the fully qualified name string."""
    def ident(x):
        return x

    if name == "Unknown":
        return ident
    try:
        obj = dr.get_component(name)
        for o in obj.mro():
            if o in DESERIALIZERS:
                return DESERIALIZERS[o]
    except:
        pass
    return ident


def serialize(obj):
    to_dict = get_serializer(obj)
    return to_dict(obj)


def deserialize(data):
    if "type" not in data:
        return data

    to_obj = get_deserializer(data["type"])
    return to_obj(data["object"])


def persister(output_dir, ignore_hidden=True):
    def observer(c, broker):
        if c not in broker:
            return

        if ignore_hidden and dr.is_hidden(c):
            return

        value = broker[c]
        try:
            content = [serialize(t) for t in value]
        except:
            content = serialize(value)
        name = dr.get_name(c)
        doc = {}
        doc["name"] = name
        doc["time"] = broker.exec_times[c]
        doc["results"] = content
        path = os.path.join(output_dir, name + "." + ser.__name__)
        with open(path, "wb") as f:
            ser.dump(doc, f)

    return observer


def hydrate(payload):
    key = dr.get_component(payload["name"])
    data = payload["results"]
    try:
        value = [deserialize(d) for d in data]
    except:
        value = deserialize(data)

    return (key, value)
