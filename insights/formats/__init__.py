from __future__ import print_function
import six
import sys

from datetime import datetime
from insights import dr, rule
from insights.util import utc


RENDERERS = {}
_FORMATTERS = {}


def get_formatter(name):
    """
    Looks up a formatter class given a prefix to it.
    The names are sorted, and the first matching class is returned.
    """
    for k in sorted(_FORMATTERS):
        if k.startswith(name):
            return _FORMATTERS[k]


class FormatterAdapterMeta(type):
    """ Automatically registers subclasses for later lookup. """

    def __init__(cls, name, bases, dct):
        if name not in ("FormatterAdapter", "EvaluatorFormatterAdapter"):
            _FORMATTERS[dr.get_name(cls)] = cls
        super(FormatterAdapterMeta, cls).__init__(name, bases, dct)


class FormatterAdapter(six.with_metaclass(FormatterAdapterMeta)):

    @staticmethod
    def configure(p):
        """ Override to add arguments to the ArgumentParser. """
        pass

    def __init__(self, args=None):
        """ Subclasses get passed the parsed args. """
        pass

    def preprocess(self, broker):
        """
        Called before any components have been run. Useful for registering
        observers.
        """
        pass

    def postprocess(self, broker):
        """
        Called after all components have been run. Useful for interrogating
        the broker for final state.
        """


class Formatter(object):
    def __init__(self, broker, stream=sys.stdout):
        self.broker = broker
        self.stream = stream
        self.start_time = datetime.now(utc)

    def __enter__(self):
        self.preprocess()
        return self

    def __exit__(self, _type, value, tb):
        self.postprocess()

    def preprocess(self):
        pass

    def postprocess(self):
        pass


class EvaluatorFormatterAdapter(FormatterAdapter):
    """
    Base class for formatters that want to serialize a SingleEvaluator after
    execution.
    """
    Impl = None

    @staticmethod
    def configure(p):
        """ Override to add arguments to the ArgumentParser. """
        p.add_argument("-F", "--fail-only", help="Show FAIL results only. Conflict with '-m' or '-f', will be dropped when using them together", action="store_true")

    def __init__(self, args=None):
        if args:
            hn = "insights.combiners.hostname, insights.parsers.branch_info"
            args.plugins = ",".join([args.plugins, hn]) if args.plugins else hn
            if args.fail_only:
                print('Options conflict: -f and -F, drops -F', file=sys.stderr)
                args.fail_only = False

    def preprocess(self, broker):
        self.formatter = self.Impl(broker)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()


def get_content(obj, val):
    """
    Attempts to determine a jinja2 content template for a rule's response.
    """
    # does the rule define a content= kwarg?
    c = dr.get_delegate(obj).content

    # otherwise, does the rule module have a CONTENT attribute?
    if c is None:
        mod = sys.modules[obj.__module__]
        c = getattr(mod, "CONTENT", None)

    if c:
        # is the content a dictionary?
        if isinstance(c, dict):

            # does it contain a make_* class as a key?
            v = c.get(val.__class__)
            if v is not None:
                return v

            # does it contain an error key?
            key = val.get_key()
            if key:
                v = c.get(key)

                # is the value a dict that contains make_* classes?
                if isinstance(v, dict):
                    return v.get(val.__class__)
                return v
        else:
            return c


try:
    from jinja2 import Template

    def format_rule(comp, val):
        content = get_content(comp, val)
        if content and val.get("type") != "skip":
            return Template(content).render(val)
        return str(val)

    RENDERERS[rule] = format_rule
except:
    pass


def render(comp, val):
    _type = dr.get_component_type(comp)
    func = RENDERERS.get(_type)
    return func(comp, val) if func else str(val)
