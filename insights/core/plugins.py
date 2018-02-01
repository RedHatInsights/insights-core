"""
The plugins module defines the components used by the rest of Insights and
specializes their interfaces and execution model where required.
"""

import inspect
import logging
import sys
import traceback
import types

from functools import partial

from insights.core import dr
from insights import settings

log = logging.getLogger(__name__)

RULE_TYPES = set()


def parser_executor(component, broker, requires, optional):
    dependency = requires[0]
    if dependency not in broker:
        raise dr.MissingRequirements(([dependency], []))

    dep_value = broker[dependency]
    if not isinstance(dep_value, list):
        return component(dep_value)

    results = []
    for d in dep_value:
        try:
            r = component(d)
            if r is not None:
                results.append(r)
        except dr.SkipComponent:
            log.debug(traceback.format_exc())
        except Exception as ex:
            log.exception(ex)
            broker.add_exception(component, ex)

    if not results:
        raise dr.SkipComponent("All failed: %s" % dr.get_name(component))

    return results


def rule_executor(component, broker, requires, optional, executor=dr.default_executor):
    try:
        r = executor(component, broker, requires, optional)
        if r is None:
            raise dr.SkipComponent(dr.get_name(component))
    except dr.MissingRequirements as mr:
        details = dr.stringify_requirements(mr.requirements)
        r = make_skip(dr.get_name(component),
                reason="MISSING_REQUIREMENTS", details=details)
    validate_response(r)
    return r


broker_rule_executor = partial(rule_executor, executor=dr.broker_executor)


class ContentException(Exception):
    """
    Raised whenever a datasource fails to get data.
    """
    pass


class DatasourceDelegate(dr.Delegate):
    def __init__(self, component, requires, optional):
        super(DatasourceDelegate, self).__init__(component, requires, optional)
        self.multi_output = False
        self.raw = False


_datasource = dr.new_component_type("datasource", executor=dr.broker_executor, delegate_class=DatasourceDelegate)
""" Defines a component that one or more Parsers will consume."""


def datasource(*args, **kwargs):
    def _f(func):
        metadata = kwargs.get("metadata", {})
        c = _datasource(*args, metadata=metadata, component_type=datasource)(func)
        delegate = dr.get_delegate(c)
        delegate.multi_output = kwargs.get("multi_output", False)
        delegate.raw = kwargs.get("raw", False)
        return c
    return _f


_metadata = dr.new_component_type("_metadata",
        auto_requires=["metadata.json"], executor=parser_executor)


def metadata(group=dr.GROUPS.single):
    def _f(func):
        return _metadata(group=group, component_type=metadata)(func)
    return _f


_parser = dr.new_component_type("_parser", executor=parser_executor)


def parser(dependency, group=dr.GROUPS.single):
    """
    Parses the raw content of a datasource into a strongly-typed
    object usable by combiners and rules. `parser` is a specialization
    of the general component interface.
    """

    def _f(component):
        return _parser(dependency, group=group, component_type=parser)(component)
    return _f


def make_rule_type(name=None,
                   auto_requires=[],
                   auto_optional=[],
                   group=dr.GROUPS.single,
                   use_broker_executor=False,
                   type_metadata={}):

    executor = broker_rule_executor if use_broker_executor else rule_executor
    _type = dr.new_component_type(name=None,
                                  auto_requires=auto_requires,
                                  auto_optional=auto_optional,
                                  group=group,
                                  executor=executor,
                                  type_metadata=type_metadata)

    def decorator(*requires, **kwargs):
        if kwargs.get("cluster"):
            kwargs["group"] = dr.GROUPS.cluster

        kwargs["component_type"] = decorator

        return _type(*requires, **kwargs)

    if name:
        decorator.__name__ = name
        s = inspect.stack()
        frame = s[1][0]
        mod = inspect.getmodule(frame) or sys.modules.get("__main__")
        if mod:
            decorator.__module__ = mod.__name__
            setattr(mod, name, decorator)

    RULE_TYPES.add(decorator)
    return decorator


combiner = dr.new_component_type("combiner")
""" A component that connects other components. """

stage = combiner

rule = make_rule_type(name="rule")
""" A component that can see all parsers and combiners for a single host."""

cluster_rule = partial(rule, cluster=True)

condition = dr.new_component_type("condition")
""" A component used by rules that allows automated statistical analysis."""

incident = dr.new_component_type("incident")
""" A component used by rules that allows automated statistical analysis."""


def is_type(component, _type):
    return dr.get_component_type(component) is _type


def is_datasource(component):
    return is_type(component, datasource)


def is_parser(component):
    return is_type(component, parser)


def is_combiner(component):
    return is_type(component, combiner)


def is_rule(component):
    return dr.get_component_type(component) in RULE_TYPES


def is_component(obj):
    return bool(dr.get_component_type(obj))


def make_skip(rule_fqdn, reason, details=None):
    return {"rule_fqdn": rule_fqdn,
            "reason": reason,
            "details": details,
            "type": "skip"}


def make_response(error_key, **kwargs):
    """ Returns a JSON document approprate as a rule plugin final
    result.

    :param str error_key: The error name identified by the plugin
    :param \*\*kwargs: Strings to pass additional information to the frontend for
          rendering more complete messages in a customer system report.


    Given::

        make_response("CRITICAL_ERROR", cpu_number=2, cpu_type="intel")

    The response will be the JSON string ::

        {
            "type": "rule",
            "error_key": "CRITICAL_ERROR",
            "cpu_number": 2,
            "cpu_type": "intel"
        }
    """

    if "error_key" in kwargs or "type" in kwargs:
        raise Exception("Can't use an invalid argument for make_response")

    r = {
        "type": "rule",
        "error_key": error_key
    }
    kwargs.update(r)

    # using str() avoids many serialization issues and runs in about 75%
    # of the time as json.dumps
    detail_length = len(str(kwargs))

    if detail_length > settings.defaults["max_detail_length"]:
        log.error("Length of data in make_response is too long.", extra={
            "max_detail_length": settings.defaults["max_detail_length"],
            "error_key": error_key,
            "len": detail_length
        })
        r["max_detail_length_error"] = detail_length
        return r

    return kwargs


def make_metadata(**kwargs):
    if "type" in kwargs:
        raise ValueError("make_metadata kwargs contain 'type' key.")

    r = {"type": "metadata"}
    r.update(kwargs)
    return r


class ValidationException(Exception):
    def __init__(self, msg, r=None):
        if r:
            msg = "%s: %s" % (msg, r)
        super(ValidationException, self).__init__(msg)


def validate_response(r):
    RESPONSE_TYPES = set(["rule", "metadata", "skip"])
    if not isinstance(r, types.DictType):
        raise ValidationException("Response is not a dict", type(r))
    if "type" not in r:
        raise ValidationException("Response requires 'type' key", r)
    if r["type"] not in RESPONSE_TYPES:
        raise ValidationException("Invalid response type", r["type"])
    if r["type"] == "rule":
        error_key = r.get("error_key")
        if not error_key:
            raise ValidationException("Rule response missing error_key", r)
        elif not isinstance(error_key, types.StringTypes):
            raise ValidationException("Response contains invalid error_key type", type(error_key))
