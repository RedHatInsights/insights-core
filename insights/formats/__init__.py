import six
from insights import dr
from insights.core.evaluators import SingleEvaluator


_FORMATTERS = {}


def get_formatter(name):
    """
    Looks up a formatter class given a prefix to it.
    The names are sorted, and the first matching class is returned.
    """
    for k in sorted(_FORMATTERS):
        if k.startswith(name):
            return _FORMATTERS[k]


class FormatterMeta(type):
    """ Automatically registers subclasses for later lookup. """

    def __init__(cls, name, bases, dct):
        if name not in ("Formatter", "EvaluatorFormatter"):
            _FORMATTERS[dr.get_name(cls)] = cls
        super(FormatterMeta, cls).__init__(name, bases, dct)


class Formatter(six.with_metaclass(FormatterMeta)):

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


class EvaluatorFormatter(Formatter):
    """
    Base class for formatters that want to serialize a SingleEvaluator after
    execution.
    """
    def __init__(self, args=None):
        if args:
            hn = "insights.combiners.hostname"
            args.plugins = ",".join([args.plugins, hn]) if args.plugins else hn

    def preprocess(self, broker):
        self.evaluator = SingleEvaluator(broker=broker)

    def postprocess(self, broker):
        self.evaluator.post_process()
        print(self.dump(self.evaluator.get_response()))

    def dump(self, data):
        raise NotImplemented("Subclasses must implement the dump method.")
