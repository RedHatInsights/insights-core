import six
import sys
from insights import dr, rule


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

    def __init__(self, args=None):
        if args:
            hn = "insights.combiners.hostname"
            args.plugins = ",".join([args.plugins, hn]) if args.plugins else hn

    def preprocess(self, broker):
        self.formatter = self.Impl(broker)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()


RENDERERS = {}

try:
    from jinja2 import Template

    def get_content(obj, key):
        mod = sys.modules[obj.__module__]
        c = getattr(mod, "CONTENT", None)
        if c:
            if isinstance(c, dict):
                if key:
                    return c.get(key)
            else:
                return c

    def format_rule(comp, val):
        content = get_content(comp, val.get_key())
        if content:
            return Template(content).render(val)
        return str(val)

    RENDERERS[rule] = format_rule
except:
    pass


def render(comp, val):
    _type = dr.get_component_type(comp)
    func = RENDERERS.get(_type)
    return func(comp, val) if func else str(val)
