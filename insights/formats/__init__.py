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
        pass


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
        p.add_argument("-m", "--missing", help="Show missing requirements.", action="store_true")
        p.add_argument("-r", "--render-content", help="Render rule content in json output.", action="store_true")
        p.add_argument("-S", "--show-rules", nargs="+",
                       choices=["fail", "info", "pass", "none", "metadata", "fingerprint"],
                       metavar="TYPE",
                       help="Show results per rule's type: 'fail', 'info', 'pass', 'none', 'metadata', and 'fingerprint'")
        p.add_argument("-F", "--fail-only",
                       help="Show FAIL results only. Conflict with '-m', will be dropped when using them together. This option is deprecated by '-S fail'",
                       action="store_true")

    def __init__(self, args=None):
        if args:
            hn = "insights.combiners.hostname, insights.parsers.client_metadata"
            args.plugins = ",".join([args.plugins, hn]) if args.plugins else hn
            self.missing = args.missing
            self.render_content = args.render_content
            fail_only = args.fail_only
            if args.missing and fail_only:
                # Drops the '-F' silently when specifying '-m' and '-F' together
                # --> Do NOT break the Format of the output
                fail_only = None
            self.show_rules = []  # Empty by default, means show ALL types (exclude "none")
            if not args.show_rules and fail_only:
                self.show_rules = ['rule']
            elif args.show_rules:
                self.show_rules = [opt.replace('fail', 'rule') for opt in args.show_rules]

    def preprocess(self, broker):
        self.formatter = self.Impl(broker, self.missing, self.render_content, self.show_rules)
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
    from jinja2 import exceptions as jinja2Exceptions

    def format_rule(comp, val):
        content = get_content(comp, val)
        if content and val.get("type") != "skip":
            try:
                text = Template(content).render(val)
            except jinja2Exceptions.UndefinedError as err:
                text = '\n'.join([str(val),
                                "CONTENT:",
                                "--------",
                                content,
                                "Failed to render the Content above:",
                                "    " + str(err)])
            finally:
                return text
        return str(val)

    RENDERERS[rule] = format_rule
except:
    pass


def render(comp, val):
    _type = dr.get_component_type(comp)
    func = RENDERERS.get(_type)
    return func(comp, val) if func else str(val)


def get_response_of_types(response, missing=True, show_rules=None):
    # Check the "-m" option:
    #  - When "-m" is specified, show the "skips" rules
    #  - When "-m" is NOT specified, do not show the "skips" rules
    if not missing and 'skips' in response:
        response.pop('skips')
    # Check the "-S" option:
    #  - When "-m" is specified but "-S" is NOT specified, show all the loaded rules
    #  - When neither "-m" nor "-S" is specified, show all the HIT rules (exclude the "skips")
    if not show_rules:
        #  - Discard the "make_none" by default when no "-S"
        #  That means show "make_none" rules only when "none" is specified in "-S"
        response.pop('none') if 'none' in response else None
        return response
    #  - Discard the "medadata" rules when it's not specified in the "-S" option
    if 'metadata' not in show_rules and 'metadata' in response.get('system', {}):
        response['system'].pop('metadata')
    #  - Discard the "make_fail" rules when it's not specified in the "-S" option
    if 'rule' not in show_rules and 'reports' in response:
        response.pop('reports')
    #  - Discard the "make_info" rules when it's not specified in the "-S" option
    if 'info' not in show_rules and 'info' in response:
        response.pop('info')
    #  - Discard the "make_pass" rules when it's not specified in the "-S" option
    if 'pass' not in show_rules and 'pass' in response:
        response.pop('pass')
    #  - Discard the "make_none" rules when it's not specified in the "-S" option
    if 'none' not in show_rules and 'none' in response:
        response.pop('none')
    #  - Discard the "fingerprint" rules when it's not specified in the "-S" option
    if 'fingerprint' not in show_rules and 'fingerprints' in response:
        response.pop('fingerprints')
    return response
