from __future__ import print_function
import inspect
import six
import sys
from datetime import datetime

from jinja2 import Template

from insights import dr, rule
from insights.core.context import ExecutionContext
from insights.core.spec_factory import ContentProvider
from insights.core.plugins import is_datasource


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
            hn = "insights.combiners.hostname"
            args.plugins = ",".join([args.plugins, hn]) if args.plugins else hn
            if args.fail_only:
                print('Options conflict: -f and -F, drops -F', file=sys.stderr)
                args.fail_only = False

    def preprocess(self, broker):
        self.formatter = self.Impl(broker)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()


class TemplateFormat(Formatter):
    """
    Subclasses should implement create_template_context to return a dictionary
    to use when rendering the jinja2 template defined by the class level
    TEMPLATE attribute.
    """

    TEMPLATE = ""
    """ jinja2 template to use for rule result rendering. """

    def find_root(self):
        """
        Finds the root directory used during the evaluation. Note this could be
        a non-existent temporary directory if analyzing an archive.
        """
        for comp in self.broker:
            try:
                if issubclass(comp, ExecutionContext):
                    return self.broker[comp].root
            except:
                pass
        return "Unknown"

    def get_datasources(self, comp, broker):
        """
        Get the most relevant activated datasources for each rule.
        """
        graph = dr.get_dependency_graph(comp)
        ds = []
        for cand in graph:
            if cand in broker and is_datasource(cand):
                val = broker[cand]
                if not isinstance(val, list):
                    val = [val]

                results = []
                for v in val:
                    if isinstance(v, ContentProvider):
                        results.append(v.cmd or v.path or "python implementation")
                ds.extend(results)
        return ds

    def collect_rules(self, comp, broker):
        """
        Rule results are stored as dictionaries in the ``self.rules`` list.
        Each dictionary contains the folowing keys:
            name: fully qualified name of the rule
            id: fully qualified rule name with "." replaced with "_"
            response_type: the class name of the response object (make_info, etc.)
            body: rendered content for the rule as provided in the rule module.
            mod_doc: pydoc of the module containing the rule
            rule_doc: pydoc of the rule
            rule_path: absolute path to the source file of the rule
            datasources: sorted list of command or files contributing to the rule
        """
        if comp in broker:
            name = dr.get_name(comp)
            rule_id = name.replace(".", "_")
            val = broker[comp]
            self.rules.append({
                "name": name,
                "id": rule_id,
                "response_type": type(val).__name__,
                "body": render(comp, val),
                "mod_doc": sys.modules[comp.__module__].__doc__ or "",
                "rule_doc": comp.__doc__ or "",
                "source_path": inspect.getabsfile(comp),
                "datasources": sorted(set(self.get_datasources(comp, broker)))
            })

    def preprocess(self):
        """
        Watches rules go by as they evaluate and collects information about
        them for later display in postprocess.
        """
        self.start_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.rules = []
        self.broker.add_observer(self.collect_rules, rule)

    def create_template_context(self):
        raise NotImplementedError()

    def postprocess(self):
        """
        Builds a dictionary of rule data as context for a jinja2 template that
        renders the final output.
        """
        ctx = self.create_template_context()
        print(Template(self.TEMPLATE).render(ctx), file=self.stream)


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


def format_rule(comp, val):
    content = get_content(comp, val)
    if content and val.get("type") != "skip":
        return Template(content).render(val)
    return str(val)


RENDERERS[rule] = format_rule


def render(comp, val):
    _type = dr.get_component_type(comp)
    func = RENDERERS.get(_type)
    return func(comp, val) if func else str(val)
