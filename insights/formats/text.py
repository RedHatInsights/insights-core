from __future__ import print_function
import six
import sys
import inspect
from collections import namedtuple

from pprint import pprint
from six import StringIO
from insights import _COLOR, dr, datasource, rule, condition, incident, parser
from insights.core.context import ExecutionContext
from insights.formats import Formatter, FormatterAdapter, render


try:
    from colorama import init

    if _COLOR == "always":
        from colorama import Fore, Style
        init(strip=False)
    elif _COLOR == "auto":
        from colorama import Fore, Style
        init()
    elif _COLOR == "never":
        class Default(type):
            def __getattr__(*args):
                return ""

        class Fore(six.with_metaclass(Default)):
            pass

        class Style(six.with_metaclass(Default)):
            pass
except ImportError:
    print("Install colorama if console colors are preferred.")

    class Default(type):
        def __getattr__(*args):
            return ""

    class Fore(six.with_metaclass(Default)):
        pass

    class Style(six.with_metaclass(Default)):
        pass


def _find_context(broker):
    for k, v in broker.instances.items():
        if inspect.isclass(k) and issubclass(k, ExecutionContext):
            return v


def render_links(component):
    links = dr.get_delegate(component).links or {}
    if any(links.values()):
        space = " " * 4
        dbl_space = space * 2
        output = StringIO()
        output.write("Links:\n")
        for key in sorted(links):
            values = sorted(links[key])
            if values:
                output.write(space + key + ":\n")
                for v in values:
                    output.write(dbl_space + v + "\n")
        output.seek(0)
        return output.read()
    return ""


class HumanReadableFormat(Formatter):
    """
    This class prints a human readable summary of rule hits. It should be used
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
    def __init__(self, broker,
            missing=False,
            tracebacks=False,
            dropped=False,
            show_rules=None,
            stream=sys.stdout):
        super(HumanReadableFormat, self).__init__(broker, stream=stream)
        self.missing = missing
        self.tracebacks = tracebacks
        self.dropped = dropped
        self.show_rules = [] if show_rules is None else show_rules

    def print_header(self, header, color):
        ln = len(header)
        print(color + '-' * ln, file=self.stream)
        print(header, file=self.stream)
        print('-' * ln + Style.RESET_ALL, file=self.stream)

    def preprocess(self):
        response = namedtuple('response', 'color label intl title')
        self.responses = {
            'skip': response(color=Fore.BLUE, label="SKIP", intl='S', title="Missing Deps: "),
            'pass': response(color=Fore.GREEN, label="PASS", intl='P', title="Passed      : "),
            'rule': response(color=Fore.RED, label="FAIL", intl='F', title="Failed      : "),
            'info': response(color=Fore.WHITE, label="INFO", intl='I', title="Info        : "),
            'none': response(color=Fore.BLUE, label="RETURNED NONE", intl='N', title="Ret'd None  : "),
            'metadata': response(color=Fore.YELLOW, label="META", intl='M', title="Metadata    : "),
            'metadata_key': response(color=Fore.MAGENTA, label="META", intl='K', title="Metadata Key: "),
            'fingerprint': response(color=Fore.YELLOW, label="FINGERPRINT", intl='P', title="Fingerprint : "),
            'exception': response(color=Fore.RED, label="EXCEPT", intl='E', title="Exceptions  : "),
        }

        self.counts = {}
        for key in self.responses:
            self.counts[key] = 0

        self.print_header("Progress:", Fore.CYAN)
        self.broker.add_observer(self.progress_bar, rule)
        self.broker.add_observer(self.progress_bar, condition)
        self.broker.add_observer(self.progress_bar, incident)
        self.broker.add_observer(self.progress_bar, parser)

    def progress_bar(self, c, broker):
        """
        Print the formated progress information for the processed return types
        """
        v = broker.get(c)

        if v and isinstance(v, dict) and len(v) > 0 and 'type' in v:
            if v["type"] in self.responses:
                print(self.responses[v["type"]].color + self.responses[v["type"]].intl + Style.RESET_ALL, end="", file=self.stream)
            else:
                print(".", end="", file=self.stream)
        elif c in broker.exceptions:
            self.counts['exception'] += len(broker.exceptions[c])
            print(Fore.RED + "E" + Style.RESET_ALL, end="", file=self.stream)
        return self

    def show_tracebacks(self):
        """ Show tracebacks """
        if self.broker.tracebacks:
            print(file=self.stream)
            print("Tracebacks:", file=self.stream)
            for t in self.broker.tracebacks.values():
                print(t, file=self.stream)

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
            pprint("Dropped Files:", stream=self.stream)
            pprint(dropped, indent=4, stream=self.stream)

    def show_description(self):
        """ Prints the formatted response for the matching return type """

        def printit(c, v):
            resp = self.responses[v["type"]]
            name = "[%s] %s" % (resp.label, dr.get_name(c))
            underline = "-" * len(name)
            name = "%s%s%s" % (resp.color, name, Style.RESET_ALL)
            print(name, file=self.stream)
            print(underline, file=self.stream)
            if v.get('type') != 'none':
                print(render_links(c), file=self.stream)
                print(render(c, v), file=self.stream)
            print(file=self.stream)

        for c in sorted(self.broker.get_by_type(rule), key=dr.get_name):
            v = self.broker[c]
            _type = v.get('type')
            if _type is None:
                continue

            if _type in self.responses:
                self.counts[_type] += 1

            if (
                    (self.missing and _type == 'skip') or
                    (self.show_rules and _type in self.show_rules) or
                    (not self.show_rules and _type not in ['skip', 'none'])
            ):
                printit(c, v)

        print(file=self.stream)

        self.print_header("Rule Execution Summary", Fore.CYAN)
        for c in self.counts:
            print(self.responses[c].color + self.responses[c].title + str(self.counts[c]) + Style.RESET_ALL, file=self.stream)

    def postprocess(self):
        if self.tracebacks:
            self.show_tracebacks()
        if self.dropped:
            self.show_dropped()

        print(file=self.stream)
        print(file=self.stream)
        self.print_header("Rules Executed", Fore.CYAN)
        self.show_description()


class HumanReadableFormatAdapter(FormatterAdapter):
    """ Displays results in a human readable format. """

    @staticmethod
    def configure(p):
        p.add_argument("-t", "--tracebacks", help="Show stack traces.", action="store_true")
        p.add_argument("-d", "--dropped", help="Show collected files that weren't processed.", action="store_true")
        p.add_argument("-m", "--missing", help="Show missing requirements.", action="store_true")
        p.add_argument("-S", "--show-rules", default=[], nargs="+",
                       choices=["fail", "info", "pass", "none", "metadata", "fingerprint"],
                       metavar="TYPE",
                       help="Show results per rule's type: 'fail', 'info', 'pass', 'none', 'metadata', and 'fingerprint'")
        p.add_argument("-F", "--fail-only",
                       help="Show FAIL results only. Conflict with '-m', will be dropped when using them together. This option is deprecated by '-S fail'",
                       action="store_true")

    def __init__(self, args=None):
        self.tracebacks = args.tracebacks
        self.dropped = args.dropped
        self.missing = args.missing
        fail_only = args.fail_only
        if self.missing and fail_only:
            print(Fore.YELLOW + 'Options conflict: -m and -F, drops -F', file=sys.stderr)
            fail_only = None
        self.show_rules = []  # Empty by default, means show ALL types (excludes "none")
        if not args.show_rules and fail_only:
            self.show_rules = ['rule']
        elif args.show_rules:
            self.show_rules = [opt.replace('fail', 'rule') for opt in args.show_rules]

    def preprocess(self, broker):
        self.formatter = HumanReadableFormat(
            broker,
            self.missing,
            self.tracebacks,
            self.dropped,
            self.show_rules,
        )
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()
