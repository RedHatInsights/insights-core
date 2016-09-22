import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class Formatter(object):
    def __init__(self, args):
        self.screen_height, self.screen_width = get_screen_width()
        self.screen_width = args.max_width if args.max_width else self.screen_width
        self.list_missing = args.list_missing
        self.list_plugins = args.list_plugins

    def display_list(self, items):
        col_size = max(map(len, items))
        col_cnt = self.screen_width / col_size
        col_size = col_size + ((self.screen_width % col_size) / col_cnt)

        sorted_items = sorted(items)
        chunk_iter = (sorted_items[i:i + col_cnt] for i in xrange(0, len(sorted_items), col_cnt))
        for chunks in chunk_iter:
            row = ''.join(item.ljust(col_size) for item in chunks)
            logger.console(row)

        logger.console("\n")

    def heading(self, text):
        logger.console("\n" + "  {0}  ".format(text).center(self.screen_width, "="))

    def hanging_indent(self, line, indent_size, word_wrap=True):
        line = line.rstrip()
        if len(line) <= self.screen_width:
            return line

        def do_wrap(l, i):
            if word_wrap and i < len(l):
                rightmost_space = l.rfind(" ", 0, i)
                return rightmost_space if rightmost_space > -1 else i
            else:
                return i

        lines = [line[0:do_wrap(line, self.screen_width)]]
        line = line[do_wrap(line, self.screen_width):]
        while line:
            line = line.strip()
            end_idx = min(len(line), do_wrap(line, self.screen_width - indent_size))
            lines.append(" " * indent_size + line[:end_idx])
            line = line[end_idx:]
        return "\n".join(lines)

    def display_dict_of_lists(self, d):
        key_field_size = max(map(len, d.keys())) + 1
        missing_fmt = "{}: {}"
        for symbolic_file, modules in d.iteritems():
            line = missing_fmt.format(symbolic_file.ljust(key_field_size), ", ".join(modules))
            logger.console(self.hanging_indent(line, key_field_size + 2))

    def display_dict_of_strings(self, d):
        key_field_size = max(map(len, d.keys())) + 1
        missing_fmt = "{}: {}"
        for key, value in d.iteritems():
            line = missing_fmt.format(key.ljust(key_field_size), value)
            logger.console(self.hanging_indent(line, key_field_size + 2))

    def display_results(self, results):
        result_count = 0
        for module, result in sorted(results.iteritems()):
            if result:
                logger.console(module + ":")
                key_field_size = max(map(len, result.keys()))
                for k, v in sorted(result.iteritems()):
                    if isinstance(v, list):
                        v = ", ".join(map(str, v)).rstrip()
                    elif isinstance(v, str):
                        v = '"{}"'.format(v)
                    line = "    {} : {}".format(k.ljust(key_field_size), v)
                    logger.console(self.hanging_indent(line, key_field_size + 7, word_wrap=False))
                logger.console("-" * self.screen_width)
                result_count = result_count + 1
        logger.console("Result count: {}".format(result_count))

    def display_system_data(self, system_data):
        d = {key: system_data[key] for key in system_data.keys() if key != "metadata"}
        d.update(system_data.get("metadata", {}))
        self.display_dict_of_strings(d)

    def format_results(self, system, reports, archives):
        if archives:
            self.heading("Multi Archive (%s nested archives)" % len(archives))
        items = {}
        missing = defaultdict(list)
        for module, eligible, output in list(reports):
            items[module] = output
            if eligible:
                for e in eligible.split(","):
                    missing[e.strip()].append(module)
        if not items:
            logger.console("No plugins executed")
            return
        if self.list_plugins:
            self.heading("Executed modules")
            self.display_list(items.keys())
        if self.list_missing:
            if missing:
                self.heading("Missing files")
                self.display_dict_of_lists(missing)
            else:
                logger.console("No files were missing")
        self.heading("System Data")
        self.display_system_data(system)
        self.heading("Results")
        self.display_results(items)
        if archives:
            self.list_plugins = False
            for each in archives:
                self.format_results(each.get("system", {}),
                                    each.get("reports", []),
                                    None)


def get_screen_width():
    try:
        import fcntl
        import termios
        import struct
        screen_height, screen_width = struct.unpack('hh', fcntl.ioctl(1, termios.TIOCGWINSZ, 'neat'))
    except:
        return 24, 80
    else:
        return screen_height, screen_width
