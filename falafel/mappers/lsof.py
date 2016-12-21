from .. import Mapper, mapper

# XXX: some of this should be delegated to rules
FILTER_LIST = ['COMMAND', 'libssl', 'libcrypto', 'libssl.so']


@mapper('lsof', FILTER_LIST)
class Lsof(Mapper):

    def parse_content(self, content):
        self.lines = content
        # In some sosreport the lsof does not start with the header
        self.header_lines = [(i, l) for i, l in enumerate(self.lines) if 'COMMAND ' in l]
        if self.header_lines:
            self.header_idx, self.header_row = self.header_lines[0]
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
        # If no header line could be found, then we are dead in the water
        if self.header_lines:
            for line in self.lines[self.header_idx + 1:]:
                command, rest = line[:self.pid_idx], line[self.pid_idx:]
                name = line[self.name_idx:]
                middle_dict = self.split_middle(rest[:self.name_idx - len(command)])
                middle_dict["COMMAND"] = command.strip()
                middle_dict["NAME"] = name.strip()
                yield middle_dict

    def __iter__(self):
        return iter(self.parse_lines())
