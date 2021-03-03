"""
Satellite PostgreSQL database queries
=====================================

This module contains the following parsers:

SatelliteAdminSettings - command ``psql -d foreman -c 'select name, value, "default" from settings where name in (\'destroy_vm_on_host_delete\', \'unregister_delete_host\')'``
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""

import os
import yaml

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException
from insights.parsers import keyword_search


class SatellitePostgreSQLQuery(CommandParser, list):
    """
    Parent class of satellite postgresql table queries.
    In some satellite postgresql table, the value of some column goes across
    multiple lines. To distinguish different rows, the value of
    first column shouldn't go across multiple lines.

    For each row, if the value of the first column:

    1. is not empty, then it is the starting of a new row.

    2. is empty, then it is still the value of last row.

    It saves the rows data into a list. Each row is saved into a dict.
    The key is the column name, the value is the value of the column.

    Resultant data structure::

        [
            {
                'name': 'abc',
                'url': [],
                'value': ['--- false+', '...']
            },
            {
                'name': 'def',
                'url': ['http://xx.com'],
                'value': ['--- true +', '...']
            }
        ]

    Sample Output::

                   name            |  url          |  value
        ---------------------------+---------------+-------
         abc                       |               | --- false+
                                   |               | ...
         def                       | http://xx.com | --- true +
                                   |               | ...
         (2 rows)


    Examples::

        >>> type(query)
        <class 'insights.parsers.satellite_postgresql_query.SatellitePostgreSQLQuery'>
        >>> query.get_column('url', name='def')
        'http://xx.com'
        >>> query.get_column('value', name='def')
        ['--- true +', '...']

    Raises::

        SkipException: when there is no valid data in the table
        ParseException: when the row is not matched to columns or
                        the count of rows isn't the same with the
                        row count output
    """

    def _get_row_count(self, line):
        try:
            return int(line.split()[0].strip('('))
        except Exception:
            raise ParseException('The row count is not in int format')

    def parse_content(self, content):
        """
        It parses the rows in the table, and save all the rows data in a list.
        Each row is saved to a dict. The key is the column name, the value
        is the mapping value of the column in the row.
        Except the value of the first column is saved to a string,
        all the other columns are saved to a list in case it goes across
        multiple lines.

        Raises::

            SkipException: when there is no valid data in the table
            ParseException: when the count number in the last count line
                            like "(2 rows)", isn't in int format, or
                            the data of some row isn't matched to the
                            length of columns, or the count of rows in
                            the table isn't the same with the last count line.
        """
        if not content:
            raise SkipException("There is no data in the table")
        self._columns = [item.strip() for item in content[0].split('|')]
        for row in content[2:-1]:  # skip the first two lines and bottom count line
            row_data = [item.strip() for item in row.split('|')]
            if len(row_data) != len(self._columns):
                raise ParseException("Invalid line: '{0}'".format(row_data))
            if row_data[0]:
                data = {}
                data[self._columns[0]] = row_data[0]
                data.update(dict(zip(self._columns[1:], [[] for i in range(1, len(self._columns))])))
                self.append(data)
                for i in range(1, len(self._columns)):
                    if row_data[i]:
                        data[self._columns[i]].append(row_data[i])
            else:
                for i in range(1, len(self._columns)):
                    if row_data[i]:
                        data[self._columns[i]].append(row_data[i])
        if not len(self):
            raise SkipException("There is no data")
        self.count = self._get_row_count(content[-1])
        if self.count != len(self):
            raise ParseException('The count of rows is not equal to the number of the last row')

    def get_column(self, column_name, **row_criteria):
        """
        Get the value of some column by searching the table with row_criteria.
        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details.  If no search
        parameters are given, no rows are returned.

        It simplify the value of the column according to actual usage.

        Returns::

            An empty_string when there is no value,
            the first element when the value has only one line,
            the value itself when the value has multiple lines

        Args::

            column_name(str): the colunm name you want to get the value for
            row_criteria(dict): key-value pairs to identify one row

        Raises::

            ParseException: when the column doesn't exist in the table, or no
                            rows found by the criteria or multiple rows found.
                            It's unusual that getting column of multiple rows.
                            So it isn't supported.
        """
        if column_name not in self._columns:
            raise ParseException("Column %s not found in the table" % column_name)
        rows = keyword_search(self, **row_criteria)
        if len(rows) > 1:
            raise ParseException("Multiple rows returned, only support getting column for one row.")
        elif len(rows) == 0:
            raise ParseException("No rows found")
        else:
            row = rows[0]
            if isinstance(row[column_name], list):
                if len(row[column_name]) == 0:
                    return ''
                if len(row[column_name]) == 1:
                    return row[column_name][0]
            return row[column_name]


@parser(Specs.satellite_settings)
class SatelliteAdminSettings(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c '"select name, value, "default" from settings where name in ('destroy_vm_on_host_delete', 'unregister_delete_host')"``.

    Sample output::

                name               |  value   |  default
        ---------------------------+----------+-----------
        unregister_delete_host     | --- true+| --- false+
                                   | ...      | ...
        destroy_vm_on_host_delete  |          | --- true +
                                   |          | ...
        (2 rows)

    Examples::

        >>> type(table)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteAdminSettings'>
        >>> table.get_setting('unregister_delete_host')
        True
        >>> table.get_setting('destroy_vm_on_host_delete')
        True

    Raises::

        ParseException: when the value of the columns "default" or "value"
                        is not valid yaml.
    """

    def _parse_yaml(self, lines):
        if lines:
            try:
                return yaml.safe_load(os.linesep.join([line.rstrip(' +') for line in lines]))
            except Exception:
                raise ParseException("Bad format value: %s" % os.linesep.join(lines))
        return ''

    def parse_content(self, content):
        super(SatelliteAdminSettings, self).parse_content(content)
        for row in self:
            if 'value' in row:
                row['value'] = self._parse_yaml(row['value'])

            if 'default' in row:
                row['default'] = self._parse_yaml(row['default'])

    def get_setting(self, setting_name):
        """
        Get the actual value of setting_name.
        It is only valid when there are default, value columns in the table.

        Raises::

            ParseException: when there are no default, value columns in the table
        """
        if all(item in self._columns for item in ['default', 'value']):
            if self.get_column('value', name=setting_name) == '':
                return self.get_column('default', name=setting_name)
            return self.get_column('value', name=setting_name)
        raise ParseException('No default, value columns in the table.')
