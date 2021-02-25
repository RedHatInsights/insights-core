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


class SatellitePostgreSQLQuery(CommandParser, list):
    """
    It is the parent class of satellite postgresql queries.
    In satellite postgresql database, the value of some column in some table
    may cross multiple lines. To make it recognizable, it is regarded the first
    column value won't cross multiple lines.
    It considers:
    1. if the first column isn't empty, it is the starting of a new row.
    2. if the first column is empty, it is still the value of last row.

    Sample Output::

                   name            |  url          |  value
        ---------------------------+---------------+-----
         abc                       |               | --- false+
                                   |               | ...
         def                       | http://xx.com | --- true +
                                   |               | ...
         (2 rows)

    Examples::

        >>> type(query)
        <class 'insights.parsers.satellite_postgresql_query.SatellitePostgreSQLQuery'>
        >>> 'abc' in query
        True
        >>> query.get_column_value('abc', 'value')
        ['--- false+', '...']
        >>> query.get_column_value('def', 'url')
        'http://xx.com'

    Raises::

        SkipException: when there is no valid data in the table
        ParseException: when the row is not matched to columns or
                        the count of rows isn't the same with the
                        row count output
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("There is no data in the table")
        self._columns = [item.strip() for item in content[0].split('|')]
        self._first_columm = self._columns[0]
        for row in content[1:]:  # skip the first column line
            if row.strip(' +-'):
                if row.strip().startswith('(') and row.strip().endswith('rows)'):
                    try:
                        self.count = int(row.split()[0].strip('('))
                    except Exception:
                        raise ParseException('The row count is not in int format')
                    break
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
        if self.count != len(self):
            raise ParseException('The count of rows is not equal to the number of the last row')

    def __contains__(self, first_column_value):
        return True if any(
            row[self._first_columm] == first_column_value for row in self
        ) else False

    def get_column_value(self, first_column_value, column_name):
        '''
        Returns:
            An empty_string when there is no value,
            the first element when the value has only one line,
            the value itself when the value has multiple lines

        Args:
            first_column_value(str): the value of the first column to identify the row
            column_name(str): the colunm name you want to get the value for
        '''

        if column_name not in self._columns:
            raise ParseException("No column name %s found" % column_name)
        for row in self:
            if row[self._first_columm] == first_column_value:
                if isinstance(row[column_name], list):
                    if len(row[column_name]) == 0:
                        return ''
                    if len(row[column_name]) == 1:
                        return row[column_name][0]
                return row[column_name]
        raise ParseException("No column value %s found" % first_column_value)


@parser(Specs.satellite_settings)
class SatelliteAdminSettings(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c '"select name, value, "default" from settings where name in ('destroy_vm_on_host_delete', 'unregister_delete_host')"``
    and save the data to itself as a dict.

    Sample output::

                name               |  value   |  default
        ---------------------------+----------+-----------
        unregister_delete_host     | --- true+| --- false+
                                   | ...      | ...
        destroy_vm_on_host_delete  |          | --- true +
                                   |          | ...
        (2 rows)

    Examples::

        >>> type(settings)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteAdminSettings'>
        >>> settings.get_settting('unregister_delete_host')
        True
        >>> len(settings)
        2
        >>> settings.get_settting('destroy_vm_on_host_delete')
        True

    Raises::

        ParseException: when the value of the columns "default" or "value" is
                        not valid yaml.
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

    def get_settting(self, setting_name):
        '''It is only valid when there are default, value columns in the table'''
        if all(item in self[0].keys() for item in ['default', 'value']):
            if self.get_column_value(setting_name, 'value') == '':
                return self.get_column_value(setting_name, 'default')
            return self.get_column_value(setting_name, 'value')
        raise ParseException('No default, value columns in the table.')
