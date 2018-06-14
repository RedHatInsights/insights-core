from insights.configtree import PushBack, parse_string, typed
from insights.configtree import Directive, Root, Section


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


def eat_white(pb, to=None):
    try:
        while pb.peek().isspace() or pb.peek() == "#":
            if pb.peek().isspace():
                if pb.peek() == to:
                    break
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


def parse_attrs(pb, end=";"):
    attrs = []
    eat_white(pb, to=end)
    while pb.peek() not in ("{}" + end):
        if pb.peek() in ('"', "'"):
            attrs.append(parse_string(pb))
        else:
            attrs.append(parse_bare(pb))
        if pb.peek() != end:
            eat_white(pb, to=end)

    if len(attrs) == 1:
        attrs = [typed(attrs[0])]

    if pb.peek() == end:
        next(pb)  # eat it
    eat_white(pb)
    return attrs


class DocParser(object):
    def __init__(self, ctx=None, line_end=";"):
        self.ctx = ctx
        self.line_end = line_end

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
        name = parse_string(pb) if pb.peek() in ("'", '"') else parse_bare(pb)
        attrs = parse_attrs(pb, end=self.line_end)
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


def parse_doc(f, ctx=None, line_end=";"):
    return DocParser(ctx, line_end=line_end).parse_doc(LineCounter(f))
