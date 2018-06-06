#!/usr/bin/env python
"""
This module models nginx configuration as a tree. It correctly handles include
directives by splicing individual document trees into their parents and
flattening the final structure into one document.

A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
from insights import combiner, parser, run
from insights.configtree import ConfigCombiner, ConfigParser
from insights.configtree import eq, PushBack, parse_string, typed
from insights.configtree import Directive, Root, Section
from insights.specs import Specs


class LineCounter(PushBack):
    def __init__(self, *args, **kwargs):
        super(LineCounter, self).__init__(*args, **kwargs)
        self.lines = 0

    def push_back(self, item):
        if item == "\n":
            self.lines -= 1
        super(LineCounter, self).push_back(item)

    def next(self):
        v = super(LineCounter, self).next()
        if v == "\n":
            self.lines += 1
        return v

    __next__ = next


def eat_white(pb):
    try:
        while pb.peek().isspace() or pb.peek() == "#":
            if pb.peek().isspace():
                next(pb)
            if pb.peek() == "#":
                while pb.peek() != "\n":
                    next(pb)
    except StopIteration:
        pass


def parse_bare(pb):
    buf = []
    try:
        while not pb.peek().isspace() and pb.peek() not in ";{":
            buf.append(next(pb))
    except StopIteration:
        pass
    return "".join(buf)


def parse_attrs(pb):
    attrs = []
    eat_white(pb)
    while pb.peek() not in ";{":
        if pb.peek() in ('"', "'"):
            attrs.append(parse_string(pb))
        else:
            attrs.append(parse_bare(pb))
        eat_white(pb)

    if len(attrs) == 1:
        attrs = [typed(attrs[0])]

    if pb.peek() == ";":
        next(pb)  # eat it
    eat_white(pb)
    return attrs


class DocParser(object):
    def __init__(self, ctx=None):
        self.ctx = ctx

    def parse_section_body(self, pb):
        next(pb)  # eat bracket
        eat_white(pb)

        body = []
        while pb.peek() != "}":
            body.append(self.parse_statement(pb))
        next(pb)  # eat bracket
        eat_white(pb)

        return body

    def parse_statement(self, pb):
        eat_white(pb)
        pos = pb.lines
        name = parse_bare(pb)
        attrs = parse_attrs(pb)
        if pb.peek() == "{":
            body = self.parse_section_body(pb)
            el = Section(name=name, attrs=attrs, children=body, ctx=self.ctx)
        else:
            el = Directive(name=name, attrs=attrs, ctx=self.ctx)
        el.pos = pos
        eat_white(pb)
        return el

    def parse_doc(self, pb):
        results = []
        while True:
            try:
                results.append(self.parse_statement(pb))
            except StopIteration:
                break
        return Root(children=results, ctx=self.ctx)


def parse_doc(f, ctx=None):
    return DocParser(ctx).parse_doc(LineCounter(f))


@parser(Specs.nginx_conf)
class _NginxConf(ConfigParser):
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)


@combiner(_NginxConf)
class NginxConfAll(ConfigCombiner):
    def __init__(self, confs):
        super(NginxConfAll, self).__init__(confs, "nginx.conf", eq("include"))

    @property
    def conf_path(self):
        return self.main.file_path


def get_conf(root=None):
    return run(NginxConfAll, root=root).get(NginxConfAll)


if __name__ == "__main__":
    run(NginxConfAll, print_summary=True)
