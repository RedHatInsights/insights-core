from __future__ import print_function
import six

from pprint import pprint
from insights import dr, datasource, rule, condition, incident, parser
from insights.core.context import ExecutionContext
from insights.formats import Formatter, FormatterAdapter, render
import collections

try:
    from colorama import Fore, Style
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
        if issubclass(k, ExecutionContext):
            return v


class HumanReadableFormat(Formatter):
    def __init__(self, broker, missing=False, tracebacks=False, dropped=False):
        self.broker = broker
        self.missing = missing
        self.tracebacks = tracebacks
        self.dropped = dropped

    def preprocess(self):
        self.counts = {'skip': 0, 'pass': 0, 'rule': 0, 'metadata': 0, 'metadata_key': 0, 'exception': 0}
        response = collections.namedtuple('response', 'color intl title')
        self.responses = {'skip': response(color=Fore.BLUE, intl='S', title="Total Skipped Due To Rule Dependencies "
                                                                            "Not Met - "),
                          'pass': response(color=Fore.GREEN, intl='P', title="Total Return Type 'make_pass' - "),
                          'rule': response(color=Fore.RED, intl='R', title="Total Return Type "
                                                                           "'make_fail/make_response' - "),
                          'metadata': response(color=Fore.YELLOW, intl='M', title="Total Return Type 'make_metadata' - "),
                          'metadata_key': response(color=Fore.MAGENTA, intl='K', title="Total Return Type "
                                                                                       "'make_metadata_key' - "),
                          'exception': response(color=Fore.RED, intl='E', title="Total Exceptions Reported to Broker - ")
                          }

        print(Fore.CYAN + '-' * 9)
        print("Progress:")
        print('-' * 9 + Style.RESET_ALL)
        self.broker.add_observer(self.progress_bar, rule)
        self.broker.add_observer(self.progress_bar, condition)
        self.broker.add_observer(self.progress_bar, incident)
        self.broker.add_observer(self.progress_bar, parser)

    def progress_bar(self, c, broker):
        """ Print the formated progress information for the processed return types
        """
        v = broker.get(c)

        if v and isinstance(v, dict) and len(v) > 0 and 'type' in v:
            if v["type"] in self.responses:
                print(self.responses[v["type"]].color + self.responses[v["type"]].intl + Style.RESET_ALL, end="")
            else:
                print(".", end="")
        elif c in broker.exceptions:
            if broker.exceptions[c] > 1:
                self.counts['exception'] += len(broker.exceptions[c])
            else:
                self.counts['exception'] += 1
            print(Fore.RED + "E" + Style.RESET_ALL, end="")
        return self

    def show_missing(self):
        """ Show missing requirements
        """
        if self.broker.missing_requirements:
            print()
            print("Missing Requirements:")
            print(self.broker.missing_requirements)

    def show_tracebacks(self):
        """ Show tracebacks
        """
        if self.broker.tracebacks:
            print()
            print("Tracebacks:")
            for t in self.broker.tracebacks.values():
                print(t)

    def show_dropped(self):
        """ Show dropped files
        """
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
            pprint("Dropped Files:")
            pprint(dropped, indent=4)

    def show_description(self):
        """ Prints the formatted response for the matching return type
        """
        def printit(c, v):
            name = None

            if v["type"] in self.responses:
                self.counts[v["type"]] += 1
                name = self.responses[v["type"]].color + dr.get_name(c) + Style.RESET_ALL
            if name:
                print(name)
                print('-' * len(name))
                print(render(c, v))
                print()

        for c in sorted(self.broker.get_by_type(rule), key=dr.get_name):
            v = self.broker[c]
            printit(c, v)
        print()

        print(Fore.CYAN + '*' * 31 + Style.RESET_ALL)
        print(Fore.CYAN + "**** Counts By Return Type ****" + Style.RESET_ALL)
        print(Fore.CYAN + '*' * 31 + Style.RESET_ALL)

        for c in self.counts:
            print(self.responses[c].color + self.responses[c].title + str(self.counts[c]) + Style.RESET_ALL)

    def postprocess(self):
        if self.missing:
            self.show_missing()
        if self.tracebacks:
            self.show_tracebacks()
        if self.dropped:
            self.show_dropped()

        print()
        print()
        print(Fore.CYAN + "-" * 13)
        print("Rules Tested:")
        print('-' * 13 + Style.RESET_ALL)

        self.show_description()


class HumanReadableFormatAdapter(FormatterAdapter):
    """ Displays results in a human readable format.
    """

    @staticmethod
    def configure(p):
        p.add_argument("-m", "--missing", help="Show missing requirements.", action="store_true")
        p.add_argument("-t", "--tracebacks", help="Show stack traces.", action="store_true")
        p.add_argument("-d", "--dropped", help="Show collected files that weren't processed.", action="store_true")

    def __init__(self, args):
        self.missing = args.missing
        self.tracebacks = args.tracebacks
        self.dropped = args.dropped
        self.formatter = None

    def preprocess(self, broker):
        self.formatter = HumanReadableFormat(broker, self.missing, self.tracebacks, self.dropped)
        self.formatter.preprocess()

    def postprocess(self, broker):
        self.formatter.postprocess()
