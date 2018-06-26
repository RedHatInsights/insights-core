"""
This module models ini configuration as a tree.

A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
import re

from insights.configtree import Directive, DocParser, LineGetter, Section
from insights.configtree import eq, first, last, typed


class ConfigParser(DocParser):
    def parse_directive(self, lg):
        line = next(lg)
        parts = [p.strip() for p in re.split(":|=", line, 1)]

        name = parts[0].strip()
        attrs = parts[1:]

        try:
            # handle continuations
            spaces = " " * (line.expandtabs().find(name) + 1)
            while lg.peek().expandtabs().startswith(spaces):
                attrs.append(next(lg).lstrip())
        except:
            pass

        if attrs:
            attrs = ["\n".join(attrs)] if len(attrs) > 1 else [typed(attrs[0])]
        return Directive(name=name, attrs=attrs, ctx=self.ctx)

    def parse_section_body(self, lg):
        body = []
        try:
            while not lg.peek().lstrip().startswith("["):
                body.append(self.parse_statement(lg))
        except StopIteration:
            pass
        return body

    def parse_section(self, lg):
        name = next(lg).strip("[] ")
        body = self.parse_section_body(lg)
        return Section(name=name, children=body, ctx=self.ctx)

    def parse_statement(self, lg):
        line = lg.peek()
        pos = lg.pos
        if line.lstrip().startswith("["):
            el = self.parse_section(lg)
        else:
            el = self.parse_directive(lg)
        el.pos = pos
        return el


def squash(doc):
    seen = set()
    add = seen.add
    names = [c.name for c in doc if not (c.name in seen or add(c.name))]
    results = [doc.select(n, one=last, roots=False) for n in names]
    doc.children = results
    for c in doc:
        squash(c)


def set_defaults(cfg):
    if "DEFAULT" not in cfg:
        return

    defaults = cfg.select("DEFAULT", one=first)
    for c in cfg[~eq("DEFAULT")]:
        for d in defaults:
            if d.name not in c:
                c.children.append(d)

    cfg.children = list(cfg[~eq("DEFAULT")])


def parse_doc(f, ctx=None, overwrite=False):
    """ Accepts an open file or a list of lines. """
    lg = LineGetter(f, comment_marker=("#", ";"), strip=False)
    cfg = ConfigParser(ctx).parse_doc(lg)
    set_defaults(cfg)
    if overwrite:
        squash(cfg)
    return cfg
