#!/usr/bin/env python
"""
This module models logrotate configuration as a tree. It correctly handles
include directives by splicing individual document trees into their parents and
flattening the final structure into one document.

A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
import operator
import os
from fnmatch import fnmatch

from insights import combiner, parser, run
from insights.configtree import ConfigCombiner, ConfigParser, eq
from insights.configtree import parse_string, Directive, Section
from insights.configtree.dictlike import eat_white, DocParser, LineCounter
from insights.specs import Specs


class LogRotateDocParser(DocParser):
    script_words = set([
        "prerotate",
        "postrotate",
        "firstaction",
        "lastaction",
        "preremove",
    ])

    def parse_attrs(self, pb):
        attrs = super(LogRotateDocParser, self).parse_attrs(pb)
        if attrs and attrs[0] == "=":
            attrs = attrs[1:]
        return attrs

    def parse_script_body(self, pb):
        results = []
        eat_white(pb)
        word = self.parse_bare(pb)
        try:
            while word != "endscript":
                pb.push_all(word)
                line = []
                while pb.peek() != self.line_end:
                    line.append(next(pb))
                results.append("".join(line))
                eat_white(pb)
                word = self.parse_bare(pb)
        except StopIteration:
            pass
        return "\n".join(results)

    def parse_statement(self, pb):
        eat_white(pb)
        pos = pb.lines
        name = parse_string(pb) if pb.peek() in ("'", '"') else self.parse_bare(pb)
        attrs = self.parse_attrs(pb)
        if name in LogRotateDocParser.script_words:
            body = self.parse_script_body(pb)
            el = Directive(name=name, attrs=[body], ctx=self.ctx)
        elif pb.peek() == "{":
            body = self.parse_section_body(pb)
            el = Section(name=name, attrs=attrs, children=body, ctx=self.ctx)
        else:
            el = Directive(name=name, attrs=attrs, ctx=self.ctx)
        el.pos = pos
        eat_white(pb)
        return el


def parse_doc(f, ctx=None):
    return LogRotateDocParser(ctx, line_end="\n").parse_doc(LineCounter(f))


@parser(Specs.logrotate_conf)
class LogRotateConf(ConfigParser):
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)


@combiner(LogRotateConf)
class LogRotateConfAll(ConfigCombiner):
    def __init__(self, confs):
        include = eq("include")
        main_file = "logrotate.conf"
        super(LogRotateConfAll, self).__init__(confs, main_file, include)

    @property
    def conf_path(self):
        return os.path.dirname(self.main.file_path)

    def find_matches(self, confs, pattern):
        results = []
        for c in confs:
            if os.path.isdir(pattern) and c.file_path.startswith(pattern):
                results.append(c)
            elif fnmatch(c.file_path, pattern):
                results.append(c)
        return sorted(results, key=operator.attrgetter("file_name"))


def get_conf(root=None):
    return run(LogRotateConfAll, root=root).get(LogRotateConfAll)
