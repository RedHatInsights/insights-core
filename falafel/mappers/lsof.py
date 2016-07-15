from falafel.core.plugins import mapper

FILTER_LIST = ['COMMAND', 'libssl', 'libcrypto', 'libssl.so', 'multipath']


class Splitter(object):

    def __init__(self, lines):
        self.lines = lines
        # In some sosreport the lsof does not start with the header
        self.header_idx, self.header_row = [(i,l) for i,l in enumerate(lines) if 'COMMAND ' in l][0]
        self.name_idx = self.header_row.index(" NAME")
        self.pid_idx = self.header_row.index("  PID")
        _, self.mid_cols = self.header_row[:self.name_idx].split(None, 1)
        self.mid_cols = "  " + self.mid_cols
        self.indexes = {}
        for col_name in self.mid_cols.split():
            self.indexes[col_name] = self.mid_cols.index(col_name) + len(col_name)
        self.indexes["FD"] += 2

    def split_middle(self, middle):
        mid_dict = {}
        offset = 0
        for col in self.mid_cols.split():
            idx = self.indexes[col]
            mid_dict[col] = middle[offset:idx].strip()
            offset = idx
        return mid_dict

    def parse_lines(self):
        for line in self.lines[self.header_idx+1:]:
            command, rest = line[:self.pid_idx], line[self.pid_idx:]
            name = line[self.name_idx:]
            middle_dict = self.split_middle(rest[:self.name_idx - len(command)])
            middle_dict["COMMAND"] = command.strip()
            middle_dict["NAME"] = name.strip()
            yield middle_dict


@mapper('lsof', FILTER_LIST)
def get_lsof(context):
    return list(Splitter(context.content).parse_lines())
