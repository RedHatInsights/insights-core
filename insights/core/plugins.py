"""
The plugins module defines the components used by the rest of Insights and
specializes their interfaces and execution model where required.
"""

import logging
import traceback

from insights.core import dr
from insights.util.subproc import CalledProcessError
from insights import settings

log = logging.getLogger(__name__)


class ContentException(dr.SkipComponent):
    """ Raised whenever a datasource fails to get data. """
    pass


component = dr.ComponentType


class datasource(dr.ComponentType):
    """ Decorates a component that one or more Parsers will consume. """
    multi_output = False
    raw = False
    filterable = False

    def invoke(self, broker):
        try:
            return self.component(broker)
        except ContentException as ce:
            log.debug(ce)
            broker.add_exception(self.component, ce, traceback.format_exc())
            raise dr.SkipComponent()
        except CalledProcessError as cpe:
            log.debug(cpe)
            broker.add_exception(self.component, cpe, traceback.format_exc())
            raise dr.SkipComponent()


class parser(dr.ComponentType):
    """
    Decorates a component responsible for parsing the output of a
    datasource.
    """
    def __init__(self, dep, group=dr.GROUPS.single):
        super(parser, self).__init__(dep, group=group)

    def invoke(self, broker):
        dep_value = broker[self.requires[0]]
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
    def process(self, broker):
        """
        Ensures dependencies have been met before delegating to `self.invoke`.
        """
        if any(i in broker for i in dr.IGNORE.get(self.component, [])):
            raise dr.SkipComponent()
        missing = self.get_missing_dependencies(broker)
        if missing:
            details = dr.stringify_requirements(missing)
            return _make_skip(dr.get_name(self.component),
                    reason="MISSING_REQUIREMENTS", details=details)
        r = self.invoke(broker)
        if r is None:
            raise dr.SkipComponent()
        if not isinstance(r, Response):
            raise Exception("rules must return Response objects.")
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


class ValidationException(Exception):
    def __init__(self, msg, r=None):
        if r:
            msg = "%s: %s" % (msg, r)
        super(ValidationException, self).__init__(msg)


class Response(dict):
    """
    Response is the base class of response types that can be returned from
    rules.

    Subclasses must call __init__ of this class via super() and must provide
    the response_type class attribute.

    The key_name class attribute is optional, but if one is specified, the
    first argument to __init__ must not be None. If key_name is None, then
    the first argument to __init__ should be None. It's best to override
    __init__ in subclasses so users aren't required to pass None explicitly.
    """

    response_type = None
    """
    response_type is something like 'rule', 'metadata', 'fingerprint', etc. It
    is how downstream systems identify the type of information returned by a
    rule.
    """

    key_name = None
    """
    key_name is something like 'error_key', 'fingerprint_key', etc.  It is the
    key downstream systems use to look up the exact response returned by a
    rule.
    """

    def __init__(self, key, **kwargs):
        self.validate_kwargs(kwargs)

        r = {"type": self.response_type}
        if self.key_name:
            self.validate_key(key)
            r[self.key_name] = key

        kwargs.update(r)
        kwargs = self.adjust_for_length(key, r, kwargs)
        super(Response, self).__init__(kwargs)

    def get_key(self):
        """
        Helper function that uses the response's key_name to look up the
        response identifier. For a rule, this is like
        response.get("error_key").
        """
        if self.key_name:
            return self.get(self.key_name)

    def validate_kwargs(self, kwargs):
        """
        Validates expected subclass attributes and constructor keyword
        arguments.
        """
        if not self.response_type:
            msg = "response_type must be set on the Response subclass."
            raise ValidationException(msg)

        if (self.key_name and self.key_name in kwargs) or "type" in kwargs:
            name = self.__class__.__name__
            msg = "%s is an invalid argument for %s" % (self.key_name, name)
            raise ValidationException(msg)

    def validate_key(self, key):
        """ Called if the key_name class attribute is not None. """
        if not key:
            name = self.__class__.__name__
            msg = "%s response missing %s" % (name, self.key_name)
            raise ValidationException(msg, self)
        elif not isinstance(key, str):
            msg = "Response contains invalid %s type" % self.key_name
            raise ValidationException(msg, type(key))

    def adjust_for_length(self, key, r, kwargs):
        """
        Converts the response to a string and compares its length to a max
        length specified in settings. If the response is too long, an error is
        logged, and an abbreviated response is returned instead.
        """
        length = len(str(kwargs))
        if length > settings.defaults["max_detail_length"]:
            self._log_length_error(key, length)
            r["max_detail_length_error"] = length
            return r
        return kwargs

    def _log_length_error(self, key, length):
        """ Helper function for logging a response length error. """
        extra = {
            "max_detail_length": settings.defaults["max_detail_length"],
            "len": length
        }
        if self.key_name:
            extra[self.key_name] = key
        msg = "Length of data in %s is too long." % self.__class__.__name__
        log.error(msg, extra=extra)


class make_response(Response):
    """
    Traditionally used by a rule to signal that its conditions have been met.
    """
    response_type = "rule"
    key_name = "error_key"


class make_fail(make_response):
    """ An alias for make_response. """
    pass


class make_pass(Response):
    """
    Can be used by a rule to explicitly indicate that a system "passed" its
    checks.
    """
    response_type = "pass"
    key_name = "pass_key"


class make_fingerprint(Response):
    response_type = "fingerprint"
    key_name = "fingerprint_key"


class make_metadata_key(Response):
    response_type = "metadata_key"
    key_name = "key"

    def __init__(self, key, value):
        super(make_metadata_key, self).__init__(key, value=value)

    def adjust_for_length(self, key, r, kwargs):
        return kwargs


class make_metadata(Response):
    """
    Allows a rule to convey addtional metadata about a system to downstream
    systems. It doesn't convey success or failure but purely information that
    may be aggregated with other make_metadata responses. As such, it has no
    response key.
    """
    response_type = "metadata"

    def __init__(self, **kwargs):
        super(make_metadata, self).__init__(None, **kwargs)


class _make_skip(Response):
    """
    Called automatically whenever a rule's dependencies aren't met. Likely to
    be deprecated or have its semantics changed. Do not call explicitly from
    rules.
    """
    response_type = "skip"

    def __init__(self, rule_fqdn, reason, details=None):
        super(_make_skip, self).__init__(None,
                                        rule_fqdn=rule_fqdn,
                                        reason=reason,
                                        details=details)
