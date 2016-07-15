from falafel.util import parse_table
from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed


class ProcessList(MapperOutput):

    @computed
    def running(self):
        return [row["COMMAND"] for row in self.data]

    def cpu_usage(self, proc):
        return [row['%CPU'] for row in self.data if row['COMMAND'] == proc][0]

    def fuzzy_match(self, proc):
        return proc in "".join(self.running)

    def __contains__(self, proc):
        return proc in self.running


@mapper('ps_auxcww')
def ps_auxcww(context):
    """
    Returns a list of dicts, where the keys in each dict are the column headers
    and each item in the list represents a process.
    """
    return ProcessList(parse_table(context.content))


@mapper('ps_aux', ['STAP', 'keystone-all', 'COMMAND'])
def ps_aux(context):
    """
    Returns a list of dicts, where the keys in each dict are the column headers
    and each item in the list represents a process.  The command and its args
    (if any) are kept together in the COMMAND key
    """
    return ProcessList(parse_table(context.content, max_splits=10))
