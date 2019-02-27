from __future__ import print_function
import datetime
import sys
import inspect
from collections import namedtuple

from pprint import pprint
from insights import dr, datasource, rule, condition, incident, parser
from insights.core.context import ExecutionContext
from insights.formats import Formatter, FormatterAdapter, render


def _find_context(broker):
    for k, v in broker.instances.items():
        if inspect.isclass(k) and issubclass(k, ExecutionContext):
            return v


class MarkdownFormat(Formatter):
    """
    This class prints a markdown formatted of rule hits. It should be used
    as a context manager and given an instance of an
    ``insights.core.dr.Broker``. ``dr.run`` should be called within the context
    using the same broker.

    Args:
        broker (Broker): the broker to watch and provide a summary about.
        missing (bool): shows rules with missing dependencies if True.
        tracebacks (bool): shows tracebacks if any exceptions were raised.
            Useful for debugging.
        dropped (bool): Shows any files that weren't collected if running
            against an archive. Included for a corner case and typically not
            used in general.
        stream (file-like): Output is written to stream. Defaults to sys.stdout.
    """
    response = namedtuple('response', 'label title')

    def __init__(self,
                 broker,
                 missing=False,
                 tracebacks=False,
                 dropped=False,
                 fail_only=False,
                 stream=sys.stdout):
        super(MarkdownFormat, self).__init__(broker, stream)
        self.broker = broker
        self.missing = missing
        self.tracebacks = tracebacks
        self.dropped = dropped
        self.fail_only = fail_only
        self.stream = stream

        self.counts = {'skip': 0, 'pass': 0, 'rule': 0, 'metadata': 0, 'metadata_key': 0, 'fingerprint': 0, 'exception': 0}
        self.responses = {
            'skip': self.response(label="SKIP", title="Missing Deps: "),
            'pass': self.response(label="PASS", title="Passed      : "),
            'rule': self.response(label="FAIL", title="Failed      : "),
            'metadata': self.response(label="META", title="Metadata    : "),
            'metadata_key': self.response(label="META", title="Metadata Key: "),
            'fingerprint': self.response(label="FINGERPRINT", title="Fingerprint : "),
            'exception': self.response(label="EXCEPT", title="Exceptions  : ")
        }

    def print_header(self, header, level):
        hdr = '#' * level + ' ' + header
        print(hdr, file=self.stream)

    def preprocess(self):
        self.broker.add_observer(self.count_exceptions, rule)
        self.broker.add_observer(self.count_exceptions, condition)
        self.broker.add_observer(self.count_exceptions, incident)
        self.broker.add_observer(self.count_exceptions, parser)

    def count_exceptions(self, c, broker):
        """
        Count exceptions as processing proceeds
        """
        if c in broker.exceptions:
            self.counts['exception'] += len(broker.exceptions[c])
        return self

    def show_tracebacks(self):
        """ Show tracebacks """
        if self.broker.tracebacks:
            print(file=self.stream)
            self.print_header("Tracebacks", 2)
            print("```", file=self.stream)
            for t in self.broker.tracebacks.values():
                print(t, file=self.stream)
            print("```", file=self.stream)

    def show_dropped(self):
        """ Show dropped files """
        ctx = _find_context(self.broker)
        if ctx and ctx.all_files:
            ds = self.broker.get_by_type(datasource)
            vals = []
            for v in ds.values():
                if isinstance(v, list):
                    vals.extend(d.path for d in v)
                else:
                    vals.append(v.path)
            dropped = set(ctx.all_files) - set(vals)
            print(file=self.stream)
            self.print_header("Dropped Files", 2)
            print("```", file=self.stream)
            pprint(dropped, indent=4, stream=self.stream)
            print("```", file=self.stream)

    def show_description(self):
        """ Prints the formatted response for the matching return type """
        def print_missing(c, v):
            resp = self.responses[v["type"]]
            name = "[%s] %s" % (resp.label, dr.get_name(c))
            self.print_header(name, 3)
            print(file=self.stream)
            print('*Missing Dependencies*:', file=self.stream)
            req_all, req_any = v.missing
            if req_all:
                print(file=self.stream)
                print('* Requires:', file=self.stream)
                for m in req_all:
                    print('    * {}'.format(dr.get_name(m)), file=self.stream)
            if req_any:
                print(file=self.stream)
                for m in req_any:
                    print('* At Least One Of:', file=self.stream)
                    if type(m) == list:
                        for c in m:
                            print('    * {}'.format(dr.get_name(c)), file=self.stream)
                    else:
                        print('    * {}'.format(dr.get_name(m)), file=self.stream)
            print(file=self.stream)

        def printit(c, v):
            print("```", file=self.stream)
            print(render(c, v), file=self.stream)
            print("```", file=self.stream)
            print(file=self.stream)

        for c in sorted(self.broker.get_by_type(rule), key=dr.get_name):
            v = self.broker[c]
            _type = v.get('type')
            if _type in self.responses:
                self.counts[_type] += 1
            if _type:
                if self.missing and _type == 'skip':
                    print_missing(c, v)
                elif ((self.fail_only and _type == 'rule') or
                      (not self.fail_only and _type != 'skip')):
                    printit(c, v)
        print(file=self.stream)

        self.print_header("Rule Execution Summary", 2)
        print("```", file=self.stream)
        for c in self.counts:
            print(' ' + self.responses[c].title + str(self.counts[c]), file=self.stream)
        print("```", file=self.stream)

    def postprocess(self):
        self.print_header("Insights Core Run ({})".format(datetime.datetime.now().strftime('%x %X')), 1)
        print(file=self.stream)
        self.print_header("Command Line", 2)
        print("`{}`".format(" ".join(sys.argv)))
        print(file=self.stream)
        if self.tracebacks:
            self.show_tracebacks()
        if self.dropped:
            self.show_dropped()

        print(file=self.stream)
        self.print_header("Rules Executed", 2)
        self.show_description()


class MarkdownFormatAdapter(FormatterAdapter):
    """ Displays results in a human readable format. """

    @staticmethod
    def configure(p):
        p.add_argument("-m", "--missing", help="Show missing requirements.", action="store_true")
        p.add_argument("-t", "--tracebacks", help="Show stack traces.", action="store_true")
        p.add_argument("-d", "--dropped", help="Show collected files that weren't processed.", action="store_true")
        p.add_argument("-F", "--fail-only", help="Show FAIL results only. Conflict with '-m' or '-f', will be dropped when using them together", action="store_true")

    def __init__(self, args):
        self.missing = args.missing
        self.tracebacks = args.tracebacks
        self.dropped = args.dropped
        self.fail_only = args.fail_only
        self.formatter = None
        if self.missing and self.fail_only:
            print('Options conflict: -m and -F, drops -F', file=sys.stderr)
            self.fail_only = False

    def preprocess(self, broker):
        self.formatter = MarkdownFormat(broker,
                self.missing, self.tracebacks, self.dropped, self.fail_only)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()
