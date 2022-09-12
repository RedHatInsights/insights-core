"""
The serde module provides decorators that allow developers to register
serializer and deserializer functions for types. It also provides a
:py:class`Hydration` class that uses registered serde functions to save and
load objects from the file system. The Hydration class includes a
:py:func`Hydration.make_persister` method that returns a function appropriate
to register as an observer on a :py:class:`Broker`.
"""
import json as ser
import logging
import os
import time
import traceback
from glob import glob
from functools import partial

from insights.core import dr
from insights.util import fs

log = logging.getLogger(__name__)

SERIALIZERS = {}
DESERIALIZERS = {}


def serializer(_type):
    """
    Decorator for serializers.

    A serializer should accept two parameters: An object and a path which is
    a directory on the filesystem where supplementary data can be stored. This
    is most often useful for datasources. It should return a dictionary version
    of the original object that contains only elements that can be serialized
    to json.
    """

    def inner(func):
        name = dr.get_name(_type)
        if name in SERIALIZERS:
            msg = "%s already has a serializer registered: %s"
            raise Exception(msg % (name, dr.get_name(SERIALIZERS[name])))
        SERIALIZERS[name] = func
        return func
    return inner


def deserializer(_type):
    """
    Decorator for deserializers.

    A deserializer should accept three parameters: A type, a dictionary, and a
    path that may contain supplementary data stored by its paired serializer.
    If the serializer stores supplementary data, the relative path to it should
    be somewhere in the dict of the second parameter.
    """

    def inner(func):
        name = dr.get_name(_type)
        if name in DESERIALIZERS:
            msg = "%s already has a deserializer registered: %s"
            raise Exception(msg % (dr.get_name(name), dr.get_name(DESERIALIZERS[name])))
        DESERIALIZERS[name] = (_type, func)
        return func
    return inner


def get_serializer(obj):
    """ Get a registered serializer for the given object.

        This function walks the mro of obj looking for serializers.
        Returns None if no valid serializer is found.
    """
    return SERIALIZERS.get(dr.get_name(type(obj)))


def get_deserializer(obj):
    """ Returns a deserializer based on the fully qualified name string."""
    return DESERIALIZERS.get(dr.get_name(type(obj)))


def serialize(obj, root=None):
    to_dict = get_serializer(obj)
    return {
        "type": dr.get_name(type(obj)),
        "object": to_dict(obj, root=root),
    }


def deserialize(data, root=None):
    type_data = DESERIALIZERS.get(data["type"])
    if type_data is None:
        raise Exception("Unrecognized type: %s" % data["type"])
    (_type, from_dict) = type_data
    return from_dict(_type, data["object"], root=root)


def marshal(v, root=None, pool=None):
    def call_serializer(func, value):
        try:
            return func(value), None
        except Exception:
            return None, traceback.format_exc()

    if v is None:
        return None, None
    f = partial(serialize, root=root)
    if isinstance(v, list):
        if pool:
            data = list(pool.map(call_serializer, [f] * len(v), v))
        else:
            data = list(map(call_serializer, [f] * len(v), v))
        results = [i[0] for i in data if i[0]]
        errors = [i[1] for i in data if i[1]]
        return results, errors
    return call_serializer(f, v)


def unmarshal(data, root=None):
    if data is None:
        return
    if isinstance(data, list):
        return [deserialize(d, root=root) for d in data]
    return deserialize(data, root=root)


class Hydration(object):
    """
    The Hydration class is responsible for saving and loading insights
    components. It puts metadata about a component's evaluation in a metadata
    file for the component and allows the serializer for a component to put raw
    data beneath a working directory.
    """
    def __init__(self, root=None, meta_data="meta_data", data="data", pool=None):
        self.root = root
        self.meta_data = os.path.join(root, meta_data) if root else None
        self.data = os.path.join(root, data) if root else None
        self.ser_name = dr.get_base_module_name(ser)
        self.created = False
        self.pool = pool

    def _hydrate_one(self, doc):
        """ Returns (component, results, errors, duration) """
        name = doc["name"]

        key = dr.get_component_by_name(name)
        if key is None:
            raise ValueError("{} is not a loaded component.".format(name))
        exec_time = doc["exec_time"]
        ser_time = doc["ser_time"]
        results = unmarshal(doc["results"], root=self.data)
        return (key, results, exec_time, ser_time)

    def hydrate(self, broker=None):
        """
        Loads a Broker from a previously saved one. A Broker is created if one
        isn't provided.
        """
        from insights.core.spec_factory import ContentException

        broker = broker or dr.Broker()
        for path in glob(os.path.join(self.meta_data, "*")):
            try:
                with open(path) as f:
                    doc = ser.load(f)
                    res = self._hydrate_one(doc)
                    comp, results, exec_time, ser_time = res
                    if results:
                        broker[comp] = results
                        broker.exec_times[comp] = exec_time + ser_time
            except ContentException as ex:
                log.debug(ex)
            except Exception as ex:
                log.warning(ex)
        return broker

    def dehydrate(self, comp, broker):
        """
        Saves a component in the given broker to the file system.
        """
        if not self.meta_data:
            raise Exception("Hydration meta_path not set. Can't dehydrate.")

        if not self.created:
            fs.ensure_path(self.meta_data, mode=0o770)
            if self.data:
                fs.ensure_path(self.data, mode=0o770)
            self.created = True

        c = comp
        doc = None
        try:
            name = dr.get_name(c)
            value = broker.get(c)
            errors = [t for e in broker.exceptions.get(c, [])
                        for t in broker.tracebacks[e]]
            doc = {
                "name": name,
                "exec_time": broker.exec_times.get(c),
                "errors": errors
            }
            start = time.time()
            results, ms_errors = marshal(value, root=self.data, pool=self.pool)
            doc["results"] = results if results else None
            errors.extend(ms_errors if isinstance(ms_errors, list) else [ms_errors]) if ms_errors else None
            doc["ser_time"] = time.time() - start
        except Exception as ex:
            log.exception(ex)
        else:
            if doc is not None and (doc["results"] or doc["errors"]):
                try:
                    path = os.path.join(self.meta_data, name + "." + self.ser_name)
                    with open(path, "w") as f:
                        ser.dump(doc, f)
                except Exception as boom:
                    log.error("Could not serialize %s to %s: %r" % (name, self.ser_name, boom))
                    if path:
                        fs.remove(path)

    def make_persister(self, to_persist):
        """
        Returns a function that hydrates components as they are evaluated. The
        function should be registered as an observer on a Broker just before
        execution.

        Args:
            to_persist (set): Set of components to persist. Skip everything
                else.
        """

        if not self.meta_data:
            raise Exception("Root not set. Can't create persister.")

        def persister(c, broker):
            if c in to_persist:
                self.dehydrate(c, broker)
        return persister
