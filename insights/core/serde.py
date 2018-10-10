import json as ser
import logging
import os
from glob import glob

from insights.core import dr, Parser
from insights.core.spec_factory import (CommandOutputProvider,
                                        ContentProvider,
                                        FileProvider)

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


def get_serializer_type(obj):
    _type = type(obj)
    for o in _type.mro():
        if o in SERIALIZERS:
            return o


def get_deserializer_type(obj):
    for o in obj.mro():
        if o in DESERIALIZERS:
            return o


def get_serializer(obj):
    """ Get a registered serializer for the given object.

        This function walks the mro of obj looking for serializers.
        Returns None if no valid serializer is found.
    """
    _type = get_serializer_type(obj)
    return SERIALIZERS.get(_type)


def get_deserializer(obj):
    """ Returns a deserializer based on the fully qualified name string."""
    _type = get_deserializer_type(obj)
    return DESERIALIZERS.get(_type)


def serialize(obj):
    the_ser = get_serializer(obj)

    if the_ser:
        def to_dict(x):
            return {"type": dr.get_name(type(obj)), "object": the_ser(x)}
    else:
        def to_dict(x):
            return {"type": None, "object": x}

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


def hydrate(root, broker=None):
    broker = broker or dr.Broker()
    raw_data = os.path.join(root, "raw_data")

    def localize(comp):
        def inner(thing):
            if isinstance(comp, FileProvider):
                comp.root = raw_data

        if isinstance(comp, list):
            for c in comp:
                inner(c)
        else:
            inner(comp)

    data = os.path.join(root, "data")
    for path in glob(os.path.join(data, "*")):
        with open(path) as f:
            doc = ser.load(f)
        name = doc["name"]
        key = dr.get_component(name)
        broker.exec_times[key] = doc["time"]

        results = unmarshal(doc["results"])
        if results:
            localize(results)
            broker[key] = results

        errors = unmarshal(doc["errors"])
        if errors:
            broker.exceptions[key] = errors
    return broker


@serializer(BaseException)
def serialize_exception(ex):
    return ex.args


@deserializer(BaseException)
def deserialize_exception(_type, data):
    obj = _type.__new__(_type)
    for k, v in data.items():
        setattr(obj, k, v)
    return obj


@serializer(FileProvider)
def serialize_provider(obj):
    return {
        "root": obj.root,
        "relative_path": obj.relative_path,
        "file_name": obj.file_name,
        "loaded": obj.loaded,
        "filter": False,
        "_content": obj._content,
        "_exception": None
    }


@serializer(CommandOutputProvider)
def serialize_command_provider(obj):
    return {
        "rc": obj.rc,
        "cmd": obj.cmd,
        "args": obj.args,
        "root": obj.root,
        "relative_path": obj.relative_path,
        "loaded": obj.loaded,
        "_content": obj.content,
        "_exception": None
    }


@deserializer(ContentProvider)
def deserialize_content(_type, data):
    obj = _type.__new__(_type)
    for k, v in data.items():
        setattr(obj, k, v)
    return obj


@serializer(Parser)
def default_parser_serializer(obj):
    return vars(obj)


@deserializer(Parser)
def default_parser_deserializer(_type, data):
    obj = _type.__new__(_type)
    obj.file_path = None
    obj.file_name = None
    obj.last_client_run = None
    obj.args = None
    for k, v in data.items():
        setattr(obj, k, v)
    return obj
