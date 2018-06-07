#!/usr/bin/env python
"""
This module models httpd configuration as a tree. It correctly handles Include
directives by splicing individual document trees into their parents and
flattening the final structure into one document.

A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
from insights import combiner, parser, run
from insights.configtree import ConfigCombiner, ConfigParser
from insights.configtree import Directive, Section, first
from insights.configtree import DocParser, LineGetter, parse_name_attrs, startswith
from insights.specs import Specs


class HttpConfDocParser(DocParser):
    """ Wrapper class so parser functions don't have to thread ctx. """
    def parse_directive(self, lg):
        line = next(lg)
        name, attrs = parse_name_attrs(line)
        return Directive(name=name, attrs=attrs, ctx=self.ctx)

    def parse_section_body(self, lg):
        body = []
        while not lg.peek().startswith("</"):
            body.append(self.parse_statement(lg))
        return body

    def parse_section(self, lg):
        line = next(lg).strip("<> ")
        name, attrs = parse_name_attrs(line)
        body = None
        try:
            body = self.parse_section_body(lg)
        except:
            raise Exception("Expected end tag for %s" % name)

        end = next(lg).strip("</> ")
        if not name == end:
            raise Exception("Tag mismatch: %s != %s" % (name, end))
        return Section(name=name, attrs=attrs, children=body, ctx=self.ctx)

    def parse_statement(self, lg):
        line = lg.peek()
        pos = lg.pos
        if line.startswith("<") and not line.startswith("</"):
            el = self.parse_section(lg)
        else:
            el = self.parse_directive(lg)
        el.pos = pos
        return el


def parse_doc(f, ctx=None):
    """ Accepts an open file or a list of lines. """
    return HttpConfDocParser(ctx).parse_doc(LineGetter(f))


@parser(Specs.httpd_conf)
class _HttpdConf(ConfigParser):
    def parse_doc(self, content):
        return parse_doc(content, ctx=self)


@combiner(_HttpdConf)
class HttpdConfAll(ConfigCombiner):
    def __init__(self, confs):
        includes = startswith("Include")
        super(HttpdConfAll, self).__init__(confs, "httpd.conf", includes)

    @property
    def conf_path(self):
        res = self.main.select("ServerRoot", one=first)
        return res.value if res else "/etc/httpd"


def get_conf(root=None):
    return run(HttpdConfAll, root=root).get(HttpdConfAll)


if __name__ == "__main__":
    run(HttpdConfAll, print_summary=True)
