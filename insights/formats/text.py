from __future__ import print_function
from pprint import pprint
from insights import dr, datasource, rule
from insights.core.context import ExecutionContext
from insights.formats import Formatter


def _find_context(broker):
    for k, v in broker.instances.items():
        if issubclass(k, ExecutionContext):
            return v


class HumanReadableFormat(Formatter):
    """ Displays results in a human readable format. """

    @staticmethod
    def configure(p):
        p.add_argument("-m", "--missing", help="Show missing requirements.", action="store_true")
        p.add_argument("-t", "--tracebacks", help="Show stack traces.", action="store_true")
        p.add_argument("-d", "--dropped", help="Show collected files that weren't processed.", action="store_true")

    def __init__(self, args):
        self.missing = args.missing
        self.tracebacks = args.tracebacks
        self.dropped = args.dropped

    def postprocess(self, broker):
        if self.missing:
            self.show_missing(broker)
        if self.tracebacks:
            self.show_tracebacks(broker)
        if self.dropped:
            self.show_dropped(broker)

        self.show_description(broker)

    def show_missing(self, broker):
        if broker.missing_requirements:
            print()
            print("Missing Requirements:")
            if broker.missing_requirements:
                print(broker.missing_requirements)

    def show_tracebacks(self, broker):
        if broker.tracebacks:
            print()
            print("Tracebacks:")
            for t in broker.tracebacks.values():
                print(t)

    def show_dropped(self, broker):
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
        def printit(c, v):
            name = dr.get_name(c)
            print(name)
            print('-' * len(name))
            print(dr.to_str(c, v))
            print()
            print()

        print()
        for c in sorted(broker.get_by_type(rule), key=dr.get_name):
            v = broker[c]
            if v["type"] != "skip":
                printit(c, v)
