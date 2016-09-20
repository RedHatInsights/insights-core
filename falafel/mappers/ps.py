from .. import MapperOutput, mapper, computed, parse_table


class ProcessList(MapperOutput):

    @computed
    def running(self):
        return [row["COMMAND"] for row in self.data if "COMMAND" in row]

    def cpu_usage(self, proc):
        for row in self.data:
            if proc == row["COMMAND"]:
                return row["%CPU"]

    def fuzzy_match(self, proc):
        return proc in "".join(self.running)

    def __contains__(self, proc):
        return proc in self.running

    def __iter__(self):
        for row in self.data:
            yield row


@mapper('ps_auxcww')
class PsAuxcww(ProcessList):

    @classmethod
    def parse_content(cls, content):
        """
        Returns a list of dicts, where the keys in each dict are the column headers
        and each item in the list represents a process.
        """
        if len(content) > 0 and "COMMAND" in content[0]:
            return parse_table(content)
        else:
            raise ValueError("PsAuxcww: Unable to parse content: {} ({})".format(len(content), content[0]))


@mapper('ps_aux', ['STAP', 'keystone-all', 'COMMAND'])
class PsAux(ProcessList):

    @classmethod
    def parse_content(cls, content):
        """
        Returns a list of dicts, where the keys in each dict are the column headers
        and each item in the list represents a process.  The command and its args
        (if any) are kept together in the COMMAND key
        """
        if len(content) > 0 and "COMMAND" in content[0]:
            return parse_table(content, max_splits=10)


@mapper('ps_auxwww')  # we don't want to filter the ps_auxwww file
class PsAuxwww(PsAux):
    pass
