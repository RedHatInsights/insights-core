from __future__ import print_function
from pprint import pprint
from insights import dr, datasource, rule
from insights.core.context import ExecutionContext
from insights.formats import Formatter, render
from colorama import Fore, Style


_counts = {'skip': 0, 'pass': 0, 'rule': 0, 'metadata': 0, 'metadata_key': 0}


def _find_context(broker):
    for k, v in broker.instances.items():
        if issubclass(k, ExecutionContext):
            return v


class HumanReadableFormat(Formatter):
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

    def progress_bar(self, c, broker):
        """ Print the formated progress information for the processed return types
        """
        v = broker.get(c)

        if v:
            if v["type"] == "skip":
                print(Fore.BLUE + "S" + Style.RESET_ALL, end="")
            elif v["type"] == "pass":
                print(Fore.GREEN + "P" + Style.RESET_ALL, end="")
            elif v["type"] == "rule":
                print(Fore.RED + "R" + Style.RESET_ALL, end="")
            elif v["type"] == "metadata":
                print(Fore.YELLOW + "M" + Style.RESET_ALL, end="")
            elif v["type"] == "metadata_key":
                print(Fore.MAGENTA + "K" + Style.RESET_ALL, end="")
            else:
                print(".", end="")
        elif c in broker.exceptions:
            print(Fore.RED + "E" + Style.RESET_ALL, end="")

    def preprocess(self, broker):
        """Print progress heading
        """
        print(Fore.CYAN + '-' * 9)
        print("Progress:")
        print('-' * 9 + Style.RESET_ALL)
        broker.add_observer(self.progress_bar, rule)

    def postprocess(self, broker):
        """Print heading for list of rules tseted and calls show_description to print list of rules and responses
        """
        if self.missing:
            self.show_missing(broker)
        if self.tracebacks:
            self.show_tracebacks(broker)
        if self.dropped:
            self.show_dropped(broker)

        print()
        print()
        print(Fore.CYAN + "-" * 13)
        print("Rules Tested:")
        print('-' * 13 + Style.RESET_ALL)

        self.show_description(broker)

    def show_missing(self, broker):
        """ Show missing requirements
        """
        if broker.missing_requirements:
            print()
            print("Missing Requirements:")
            print(broker.missing_requirements)

    def show_tracebacks(self, broker):
        """ Show tracebacks
        """
        if broker.tracebacks:
            print()
            print("Tracebacks:")
            for t in broker.tracebacks.values():
                print(t)

    def show_dropped(self, broker):
        """ Show dropped files
        """
        ctx = _find_context(broker)
        if ctx and ctx.all_files:
            ds = broker.get_by_type(datasource)
            vals = []
            for v in ds.values():
                if isinstance(v, list):
                    vals.extend(d.path for d in v)
                else:
                    vals.append(v.path)
            dropped = set(ctx.all_files) - set(vals)
            pprint("Dropped Files:")
            pprint(dropped, indent=4)

    def show_description(self, broker):
        """ Prints the formated response for the matching return type
        """
        def printit(c, v):
            name = None

            if v["type"] == "skip":
                _counts[v["type"]] += 1
                name = Fore.BLUE + dr.get_name(c) + Style.RESET_ALL
            elif v["type"] == "pass":
                _counts[v["type"]] += 1
                name = Fore.GREEN + dr.get_name(c) + Style.RESET_ALL
            elif v["type"] == "rule":
                _counts[v["type"]] += 1
                name = Fore.RED + dr.get_name(c) + Style.RESET_ALL
            elif v["type"] == "metadata":
                _counts[v["type"]] += 1
                name = Fore.YELLOW + dr.get_name(c) + Style.RESET_ALL
            elif v["type"] == "metadata_key":
                _counts[v["type"]] += 1
                name = Fore.MAGENTA + dr.get_name(c) + Style.RESET_ALL
            if name:
                print(name)
                print('-' * len(name))
                print(render(c, v))
                print()

        for c in sorted(broker.get_by_type(rule), key=dr.get_name):
            v = broker[c]
            printit(c, v)
        print()

        print(Fore.CYAN + '*' * 31 + Style.RESET_ALL)
        print(Fore.CYAN + "**** Counts By Return Type ****" + Style.RESET_ALL)
        print(Fore.CYAN + '*' * 31 + Style.RESET_ALL)
        print(Fore.BLUE + "Total Skipped Due To Rule Dependencies Not Met - {}".format(_counts['skip']) + Style.RESET_ALL)
        print(Fore.GREEN + "Total Return Type 'make_pass' - {}".format(_counts['pass']) + Style.RESET_ALL)
        print(Fore.RED + "Total Return Type 'make_fail/make_response' - {}".format(_counts['rule']) + Style.RESET_ALL)
        print(Fore.YELLOW + "Total Return Type 'make_metedata' - {}".format(_counts['metadata']) + Style.RESET_ALL)
        print(Fore.MAGENTA + "Total Return Type 'make_metadata_key' - {}".format(_counts['metadata_key']) + Style.RESET_ALL)
