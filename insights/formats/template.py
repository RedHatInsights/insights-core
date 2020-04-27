from __future__ import print_function
import inspect
import sys

from jinja2 import Template

from insights import dr, rule
from insights.core.context import ExecutionContext
from insights.core.spec_factory import ContentProvider
from insights.core.plugins import is_datasource
from insights.formats import render, Formatter


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
            source_path: absolute path to the source file of the rule
            tags: the list of tags associated with the rule
            datasources: sorted list of command or files contributing to the rule
        """
        if comp in broker:
            name = dr.get_name(comp)
            rule_id = name.replace(".", "_")
            val = broker[comp]
            links = dr.get_delegate(comp).links or {}
            self.rules.append({
                "name": name,
                "id": rule_id,
                "response_type": type(val).__name__,
                "body": render(comp, val),
                "mod_doc": sys.modules[comp.__module__].__doc__ or "",
                "rule_doc": comp.__doc__ or "",
                "source_path": inspect.getabsfile(comp),
                "tags": list(dr.get_tags(comp)),
                "datasources": sorted(set(self.get_datasources(comp, broker))),
                "links": links
            })

    def preprocess(self):
        """
        Watches rules go by as they evaluate and collects information about
        them for later display in postprocess.
        """
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
