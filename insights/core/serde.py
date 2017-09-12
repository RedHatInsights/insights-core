import json as ser
import logging
import os

from insights.core import dr, plugins
from insights.util import fs

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
    _type = type(obj)
    for o in _type.mro():
        if o not in SERIALIZERS:
            continue
        return lambda x: {"type": dr.get_name(_type), "object": SERIALIZERS[o](x)}
    return lambda x: {"type": None, "object": x}


def get_deserializer(obj):
    """ Returns a deserializer based on the fully qualified name string."""
    for o in obj.mro():
        if o in DESERIALIZERS:
            return DESERIALIZERS[o]


def serialize(obj):
    to_dict = get_serializer(obj)
    return to_dict(obj)


def deserialize(data):
    if not data.get("type"):
        return data["object"]

    _type = dr.get_component(data["type"])
    if not _type:
        raise Exception("Unrecognized type: %s" % data["type"])

    to_obj = get_deserializer(_type)
    if not to_obj:
        raise Exception("No deserializer for type: %s" % data["type"])

    return to_obj(_type, data["object"])


def marshal(v):
    if v is None:
        return None
    if isinstance(v, list):
        return [serialize(t) for t in v]
    return serialize(v)


def unmarshal(data):
    if data is None:
        return None
    if isinstance(data, list):
        return [deserialize(d) for d in data]
    return deserialize(data)


def persister(output_dir, ignore_hidden=True):
    def observer(c, broker):
        if ignore_hidden and dr.is_hidden(c):
            return

        if c not in broker and c not in broker.exceptions:
            return

        name = dr.get_name(c)
        c_type = dr.get_component_type(c)
        doc = {}
        doc["name"] = name
        doc["dr_type"] = dr.get_name(c_type) if c_type else None
        doc["is_rule"] = plugins.is_rule(c)
        doc["time"] = broker.exec_times.get(c)
        doc["results"] = marshal(broker.get(c))
        doc["errors"] = marshal(broker.exceptions.get(c))
        path = os.path.join(output_dir, name + "." + dr.get_base_module_name(ser))
        try:
            with open(path, "wb") as f:
                ser.dump(doc, f)
        except Exception as boom:
            log.exception(boom)
            fs.remove(path)

    return observer


def hydrate(payload, broker=None):
    broker = broker or dr.Broker()
    name = payload["name"]
    key = dr.get_component(name) or name

    results = unmarshal(payload["results"])
    if results:
        broker[key] = results

    errors = unmarshal(payload["errors"])
    if errors:
        broker.exceptions[key] = errors

    return broker


@serializer(BaseException)
def serialize_exception(ex):
    return ex.args


@deserializer(BaseException)
def deserialize_exception(_type, data):
    return _type(*data)
