"""
The plugins module defines the components used by the rest of Insights and
specializes their interfaces and execution model where required.
"""

import logging
import sys
import traceback

from insights.core import dr
from insights import settings

log = logging.getLogger(__name__)


class ContentException(dr.SkipComponent):
    """ Raised whenever a datasource fails to get data. """
    pass


class datasource(dr.ComponentType):
    """ Decorates a component that one or more Parsers will consume. """
    multi_output = False
    raw = False

    def invoke(self, broker):
        try:
            return self.component(broker)
        except ContentException as ce:
            log.debug(ce)
            broker.add_exception(self.component, ce, traceback.format_exc())
            raise dr.SkipComponent()


class parser(dr.ComponentType):
    """
    Decorates a component responsible for parsing the output of a
    datasource.
    """
    def __init__(self, dep, group=dr.GROUPS.single):
        super(parser, self).__init__(dep, group=group)

    def invoke(self, broker):
        dependency = self.requires[0]
        if dependency not in broker:
            raise dr.MissingRequirements(([dependency], []))

        dep_value = broker[dependency]
        if not isinstance(dep_value, list):
            return self.component(dep_value)

        results = []
        for d in dep_value:
            try:
                r = self.component(d)
                if r is not None:
                    results.append(r)
            except dr.SkipComponent:
                pass
            except Exception as ex:
                tb = traceback.format_exc()
                log.warn(tb)
                broker.add_exception(self.component, ex, tb)

        if not results:
            log.debug("All failed: %s" % dr.get_name(self.component))
            raise dr.SkipComponent()
        return results


class metadata(parser):
    """ Used for old cluster uber-archives. """
    # TODO: Mark deprecated
    requires = ["metadata.json"]


class combiner(dr.ComponentType):
    """ ComponentType for a component that composes other components. """
    pass


class rule(dr.ComponentType):
    """
    ComponentType for a component that can see all parsers and combiners for a
    single host.
    """
    def invoke(self, broker):
        try:
            r = super(rule, self).invoke(broker)
            if r is None:
                raise dr.SkipComponent()
        except dr.MissingRequirements as mr:
            details = dr.stringify_requirements(mr.requirements)
            r = make_skip(dr.get_name(self.component),
                    reason="MISSING_REQUIREMENTS", details=details)
        validate_response(r)
        return r


class condition(dr.ComponentType):
    """
    ComponentType for a component used by rules that allows automated
    statistical analysis.
    """
    pass


class incident(dr.ComponentType):
    """
    ComponentType for a component used by rules that allows automated
    statistical analysis.
    """
    pass


class fact(dr.ComponentType):
    """
    ComponentType for a component that surfaces a dictionary or list of
    dictionaries that will be used later by cluster rules.
    """
    pass


def is_type(component, _type):
    try:
        return issubclass(dr.get_component_type(component), _type)
    except:
        return False


def is_datasource(component):
    return is_type(component, datasource)


def is_parser(component):
    return is_type(component, parser)


def is_combiner(component):
    return is_type(component, combiner)


def is_rule(component):
    return is_type(component, rule)


def is_component(obj):
    return bool(dr.get_component_type(obj))


def make_skip(rule_fqdn, reason, details=None):
    return {"rule_fqdn": rule_fqdn,
            "reason": reason,
            "details": details,
            "type": "skip"}


def _is_make_reponse_too_long(key, kwargs):
    response_type = {"rule": "make_response", "fingerprint": "make_fingerprint"}

    # using str() avoids many serialization issues and runs in about 75%
    # of the time as json.dumps
    detail_length = len(str(kwargs))

    if detail_length > settings.defaults["max_detail_length"]:
        log.error("Length of data in %s is too long." % response_type[kwargs['type']], extra={
            "max_detail_length": settings.defaults["max_detail_length"],
            "error_key": key,
            "len": detail_length
        })
        return True
    return False


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

    detail_length = len(str(kwargs))

    if _is_make_reponse_too_long(error_key, kwargs):
        r["max_detail_length_error"] = detail_length
        return r

    return kwargs


def make_fingerprint(fingerprint_key, **kwargs):
    """ Returns a JSON document appropriate as a fingerprint rule plugin final
    result.

    :param str fingerprint_key: The fingerprint key name is used for
          identification of the plugin.
    :param \*\*kwargs: Strings to pass additional information to the frontend for
          rendering more complete messages in a customer system report.


    Given::

        make_fingerprint("FINGERPRINT", manufacturer="Red Hat", product="Insights")

    The response will be the JSON string ::

        {
            "type": "fingerprint",
            "fingerprint_key": "FINGERPRINT",
            "manufacturer": "Red Hat",
            "product": "Insights"
        }
    """

    if "fingerprint_key" in kwargs or "type" in kwargs:
        raise Exception("Can't use an invalid argument for make_fingerprint")

    r = {
        "type": "fingerprint",
        "fingerprint_key": fingerprint_key
    }
    kwargs.update(r)

    detail_length = len(str(kwargs))

    if _is_make_reponse_too_long(fingerprint_key, kwargs):
        r["max_detail_length_error"] = detail_length
        return r

    return kwargs


def make_metadata_key(key, value):
    if key == "type":
        raise ValueError("metadata key cannot be 'type'")

    return {"type": "metadata_key", "key": key, "value": value}


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
    RESPONSE_TYPES = set(["rule", "metadata", "skip", "metadata_key", "fingerprint"])
    if not isinstance(r, dict):
        raise ValidationException("Response is not a dict", type(r))
    if "type" not in r:
        raise ValidationException("Response requires 'type' key", r)
    if r["type"] not in RESPONSE_TYPES:
        raise ValidationException("Invalid response type", r["type"])
    if r["type"] == "rule":
        error_key = r.get("error_key")
        if not error_key:
            raise ValidationException("Rule response missing error_key", r)
        elif not isinstance(error_key, str):
            raise ValidationException("Response contains invalid error_key type", type(error_key))
    if r["type"] == "fingerprint":
        fingerprint_key = r.get("fingerprint_key")
        if not fingerprint_key:
            raise ValidationException("Rule response missing fingerprint_key", r)
        elif not isinstance(fingerprint_key, str):
            raise ValidationException("Response contains invalid fingerprint_key type", type(fingerprint_key))


try:
    from jinja2 import Template

    def get_content(obj, key):
        mod = sys.modules[obj.__module__]
        c = getattr(mod, "CONTENT", None)
        if c:
            if isinstance(c, dict) and key:
                return c.get(key)
            return c

    def format_rule(comp, val):
        content = get_content(comp, val.get("error_key"))
        if content:
            return Template(content).render(val)
        return str(val)

    dr.set_formatter(format_rule, rule)
except:
    pass
