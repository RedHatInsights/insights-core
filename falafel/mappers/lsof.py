from .. import Scannable, mapper

# XXX: some of this should be delegated to rules
FILTER_LIST = ['COMMAND', 'libssl', 'libcrypto', 'libssl.so']


@mapper('lsof', FILTER_LIST)
class Lsof(Scannable):

    def _calc_indexes(self, line):
        self.header_row = line
        self.name_idx = self.header_row.index(" NAME")
        self.pid_idx = self.header_row.index("  PID")
        _, self.mid_cols = self.header_row[:self.name_idx].split(None, 1)
        self.mid_cols = "  " + self.mid_cols
        self.indexes = {}
        for col_name in self.mid_cols.split():
            self.indexes[col_name] = self.mid_cols.index(col_name) + len(col_name)
        self.indexes["FD"] += 2

    def parse_content(self, content):
        # In some sosreport the lsof does not start with the header
        content = iter(content)

        line = next(content)
        while 'COMMAND ' not in line:
            next(content)

        self._calc_indexes(line)
        for line in content:
            command, rest = line[:self.pid_idx], line[self.pid_idx:]
            name = line[self.name_idx:]
            middle_dict = self.split_middle(rest[:self.name_idx - len(command)])
            middle_dict["COMMAND"] = command.strip()
            middle_dict["NAME"] = name.strip()
            for scanner in self.scanners:
                scanner(middle_dict)

    def split_middle(self, middle):
        mid_dict = {}
        offset = 0
        for col in self.mid_cols.split():
            idx = self.indexes[col]
            mid_dict[col] = middle[offset:idx].strip()
            offset = idx
        return mid_dict
