"""
PS
==

This combiner provides information about running processes based on the ``ps`` command.
More specifically this consolidates data from
:py:class:`insights.parsers.ps.PsEo`,
:py:class:`insights.parsers.ps.PsAuxcww`,
:py:class:`insights.parsers.ps.PsEoCmd`,
:py:class:`insights.parsers.ps.PsEf`,
:py:class:`insights.parsers.ps.PsAux`,
:py:class:`insights.parsers.ps.PsAuxww` and
:py:class:`insights.parsers.ps.PsAlxwww` parsers (in that specific order).

Note:
    The final dataset can vary depending on availability of the parsers for a given
    ``ExecutionContext`` and added filters. The underlying filterable datasources
    for this combiner can be filtered by passing :py:class:`insights.combiners.ps.Ps`
    to :py:func:`insights.core.filters.add_filter` function along with a filter pattern.
    Please see :py:mod:`insights.core.filters` for more information on filtering.


Examples:

    >>> sorted(ps_combiner.pids)
    [1, 2, 3, 8, 9, 10, 11, 12, 13]
    >>> '[kthreadd]' in ps_combiner.commands
    True
    >>> '[kthreadd]' in ps_combiner
    True
    >>> ps_combiner[2] == {
    ... 'PID': 2,
    ... 'USER': 'root',
    ... 'UID': 0,
    ... 'PPID': 0,
    ... '%CPU': 0.0,
    ... '%MEM': 0.0,
    ... 'VSZ': 0.0,
    ... 'RSS': 0.0,
    ... 'TTY': '?',
    ... 'STAT': 'S',
    ... 'START': '2019',
    ... 'TIME': '1:04',
    ... 'COMMAND': '[kthreadd]',
    ... 'COMMAND_NAME': '[kthreadd]',
    ... 'ARGS': '',
    ... 'F': '1',
    ... 'PRI': 20,
    ... 'NI': '0',
    ... 'WCHAN': 'kthrea'
    ... }
    True
"""

from insights.core.plugins import combiner
from insights.parsers import keyword_search
from insights.parsers.ps import PsAlxwww, PsAuxww, PsAux, PsAuxcww, PsEo, PsEf, PsEoCmd


@combiner([PsAlxwww, PsAuxww, PsAux, PsEf, PsAuxcww, PsEo, PsEoCmd])
class Ps(object):
    """
    ``Ps`` combiner consolidates data from the parsers in ``insights.parsers.ps`` module.
    """

    # data attributes type conversion map
    __CONVERSION_MAP = {
        'PID': int,
        'UID': int,
        'PPID': int,
        '%CPU': float,
        '%MEM': float,
        'VSZ': float,
        'RSS': float,
        'PRI': int
    }

    # empty base row
    __EMPTY_ROW = {
        'PID': None,
        'USER': None,
        'UID': None,
        'PPID': None,
        '%CPU': None,
        '%MEM': None,
        'VSZ': None,
        'RSS': None,
        'TTY': None,
        'STAT': None,
        'START': None,
        'TIME': None,
        'COMMAND': None,
        'COMMAND_NAME': None,
        'ARGS': None,
        'F': None,
        'PRI': None,
        'NI': None,
        'WCHAN': None
    }

    def __init__(self, ps_alxwww, ps_auxww, ps_aux, ps_ef, ps_auxcww, ps_eo, ps_eo_cmd):
        self._pid_data = {}

        # order of parsers is important here
        if ps_eo:
            self.__update_data(ps_eo)
        if ps_auxcww:
            self.__update_data(ps_auxcww)
        if ps_eo_cmd:
            self.__update_data(ps_eo_cmd)
        if ps_ef:
            # mapping configurations to combine PsEf data
            mapping = {
                'UID': ('USER', True),
                # cpu value (integer value) from PsEf parser should not override an existing value
                'C': ('%CPU', False),
                'CMD': ('COMMAND', True),
                'STIME': ('START', True)
            }
            self.__update_data(ps_ef, mapping)
        if ps_aux:
            self.__update_data(ps_aux)
        if ps_auxww:
            self.__update_data(ps_auxww)
        if ps_alxwww:
            self.__update_data(ps_alxwww)

        self.__convert_data_types()

        self._commands = set(row['COMMAND'] for row in self._pid_data.values())

    @property
    def pids(self):
        """
        Returns the list of running process IDs (integers).


        Returns:
            list: the PIDs from the PID column.
        """
        return list(self._pid_data.keys())

    @property
    def processes(self):
        """
        Returns the list of dictionaries, where each item in the list represents a process
        and the keys in each dictionary are the column headers.

        Returns:
            list: the list of running processes.
        """
        return list(self._pid_data.values())

    @property
    def commands(self):
        """
        Returns the set of full command strings for each command
        including optional path and arguments, unless underlying parser
        contains command names only.

        Returns:
            set: the set with command strings.
        """
        return self._commands

    def search(self, **kwargs):
        """
        Search the process list for matching rows based on key-value pairs.

        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details.  If no search
        parameters are given, no rows are returned.

        Returns:
            list: A list of dictionaries of processes that match the given
            search criteria.

        Examples:
            >>> ps_combiner.search(COMMAND__contains='[rcu_bh]') == [
            ... {'PID': 9, 'USER': 'root', 'UID': 0, 'PPID': 2, '%CPU': 0.1, '%MEM': 0.0,
            ...  'VSZ': 0.0, 'RSS': 0.0, 'TTY': '?', 'STAT': 'S', 'START': '2019', 'TIME': '0:00',
            ...  'COMMAND': '[rcu_bh]', 'COMMAND_NAME': '[rcu_bh]', 'ARGS': '', 'F': '1', 'PRI': 20,
            ...  'NI': '0', 'WCHAN': 'rcu_gp'}
            ... ]
            True
            >>> ps_combiner.search(USER='root', COMMAND='[kthreadd]') == [
            ... {'PID': 2, 'USER': 'root', 'UID': 0, 'PPID': 0, '%CPU': 0.0, '%MEM': 0.0,
            ...  'VSZ': 0.0, 'RSS': 0.0, 'TTY': '?', 'STAT': 'S', 'START': '2019', 'TIME': '1:04',
            ...  'COMMAND': '[kthreadd]', 'COMMAND_NAME': '[kthreadd]', 'ARGS': '', 'F': '1', 'PRI': 20,
            ...  'NI': '0', 'WCHAN': 'kthrea'}
            ... ]
            True
        """
        return keyword_search(self._pid_data.values(), **kwargs)

    def __contains__(self, command):
        """
        Check if a specific command is running.

        Args:
            command (str): a command string.

        Returns:
            bool: True if command is running, otherwise False.
        """
        return command in self._commands

    def __getitem__(self, pid):
        """
        Retrieve a specific process by its PID.

        Args:
            pid (int): process ID integer value.

        Returns:
            dict: dictionary that represents a process with each key
                as the column header.
        """
        return self._pid_data.get(pid)

    def __iter__(self):
        for row in self._pid_data.values():
            yield row

    def __update_data(self, ps_parser, mapping=None):
        """
        Updates internal dictionary with the processes data from the parser.
        New PIDs will be added to the dictionary and existing ones will be
        updated. ``mapping`` needs to specify attribute mapping metadata
        for proper consolidation of data.

        Args:
            ps_parser (insights.parsers.ps.Ps): Ps parser implementation instance.
            mapping (dict): parser data mapping configurations.

        Returns:
            None
        """
        def update_row(input_row, mapping):
            pid = int(input_row['PID'])
            # if new PID then add base empty row to the dictionary using `setdefault`
            pid_row = self._pid_data.setdefault(pid, self.__EMPTY_ROW.copy())
            temp_row = self.__map_row(pid, input_row, mapping)
            pid_row.update(temp_row)

        [update_row(row, mapping) for row in ps_parser.data if row['PID'].isdigit()]

    def __convert_data_types(self):
        """
        Convert types in the final dataset for attributes defined
        in ``__CONVERSION_MAP`` dictionary.

        Returns:
            None
        """
        def convert_attr(attr_name, row):
            if row[attr_name] is not None:
                type_ctor = self.__CONVERSION_MAP[attr_name]
                row[attr_name] = type_ctor(row[attr_name])

        [convert_attr(attr_name, row)
         for attr_name in self.__CONVERSION_MAP
         for row in self._pid_data.values()
         if attr_name in row]

    def __map_row(self, pid, row, mapping):
        """
        Creates new data row based on provided mapping configurations
        in ``mapping`` dictionary. If no mappings provided, original data row
        will be copied without any changes.

        Args:
            pid (int): a process PID.
            row (dict): a data row dictionary from a Ps parser.
            mapping(dict): ps data mapping configurations,
            the format for this is:
            ``original_attribute_name: (destination_attiribute_name, override_value_if_populated_flag)``

        Returns:
            dict: Modified data row that represents a process.
        """
        r_row = {}
        if mapping:
            for attr_name in row:
                if attr_name in mapping:
                    # `dest_name` is mapping destination attribute name
                    # `override` is bool flag to identify if already populated
                    #  attribute value should be overridden/updated
                    dest_name, override = mapping[attr_name]
                    # don't map attribute if destination is None
                    if dest_name is None:
                        continue
                    if not override:
                        # don't update attribute value if already populated for this PID
                        if self._pid_data.setdefault(pid, self.__EMPTY_ROW.copy)[dest_name] is not None:
                            continue
                    r_row[dest_name] = row[attr_name]
                else:
                    r_row[attr_name] = row[attr_name]
        else:
            r_row = row.copy()
        return r_row
