"""
Satellite PostgreSQL database queries
=====================================

This module contains the following parsers:

SatelliteAdminSettings - command ``psql -d foreman -c 'select name, value, "default" from settings where name in (\'destroy_vm_on_host_delete\', \'unregister_delete_host\') --csv'``
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SatelliteComputeResources - command ``psql -d foreman -c 'select name, type from compute_resources'``
-----------------------------------------------------------------------------------------------------
"""

import os
import yaml
from csv import DictReader

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException
from insights.parsers import keyword_search


class SatellitePostgreSQLQuery(CommandParser, list):
    """
    Parent class of satellite postgresql table queries.
    It saves the rows data into a list. Each row is saved into a dict.
    The key is the column name, the value is the value of the column.

    Resultant data structure::

        [
            {
                'name': 'abc',
                'url': '',
                'value': 'test'
            },
            {
                'name': 'def',
                'url': 'http://xx.com',
                'value': ''
            }
        ]

    Sample Output::

        name,url,value
        abc,,test
        def,http://xx.com,


    Examples:
        >>> type(query)
        <class 'insights.parsers.satellite_postgresql_query.SatellitePostgreSQLQuery'>
        >>> rows = query.search(name='abc')
        >>> len(rows)
        1
        >>> rows[0]['value']
        'test'
        >>> columns=query.get_columns()
        >>> 'url' in columns
        True
        >>> 'name' in columns
        True

    Raises:
        SkipException: when there isn't data in the table
        ParseException: when the output isn't in good csv format
    """

    def parse_content(self, content):
        if not content or len(content) == 1:
            raise SkipException("There is no data in the table")
        try:
            # keep the line break for yaml parse in some table
            reader = DictReader(os.linesep.join(content).splitlines(True))
        except Exception:
            raise ParseException("The content isn't in csv format")
        for row in reader:
            self.append(row)

    def get_columns(self):
        return list(self[0].keys())

    def search(self, **kwargs):
        """
        Get the rows by searching the table with kwargs.
        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details. If no search
        parameters are given, no rows are returned.

        It simplify the value of the column according to actual usage.

        Returns:
            list: A list of dictionaries of rows that match the given
            search criteria.

        Examples:
            >>> query.search(name__startswith='abc') == [
            ... {'name': 'abc', 'url': '', 'value': 'test'},
            ... {'name': 'abcdef', 'url': '', 'value': 'test2'}
            ... ]
            True
            >>> query.search(name__startswith='abc', value='test') == [
            ... {'name': 'abc', 'url': '', 'value': 'test'}
            ... ]
            True
        """

        return keyword_search(self, **kwargs)


@parser(Specs.satellite_settings)
class SatelliteAdminSettings(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c '"select name, value, "default" from settings where name in ('destroy_vm_on_host_delete', 'unregister_delete_host') --csv"``.

    Sample output::

        name,value,default
        unregister_delete_host,"--- true
        ...","--- false
        ..."
        destroy_vm_on_host_delete,,"--- true
        ..."

    Examples:
        >>> type(table)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteAdminSettings'>
        >>> table.get_setting('unregister_delete_host')
        True
        >>> table.get_setting('destroy_vm_on_host_delete')
        True
    """

    def _parse_yaml(self, value):
        if value:
            try:
                return yaml.safe_load(value)
            except Exception:
                raise ParseException("Bad format value: %s" % value)
        return value

    def parse_content(self, content):
        """
        The "default" and "value" columns must be selected, or else the
        settings value can't be determined.
        The "default" and "value" column are in yaml format, it is transfer to
        python object.

        Raises:
            SkipException: when value or default column isn't found in the
                            table.
            ParseException: when the value or default in bad yaml format.
        """
        super(SatelliteAdminSettings, self).parse_content(content)
        if not all(item in self.get_columns() for item in ['default', 'value']):
            raise SkipException('No default, value columns in the table.')
        for row in self:
            row['default'] = self._parse_yaml(row['default'])
            row['value'] = self._parse_yaml(row['value'])

    def get_setting(self, setting_name):
        """
        Get the actual value of setting_name.
        If the value column isn't empty, the value of the setting_name is the
        value column, or else it's the default column.

        Args:
            setting_name (str): the value of name column which is searched in the table.

        Returns:
            It depends on the setting, maybe boolean, string, int or a list.
            None if the setting_name doesn't exist in the table.
        """
        rows = self.search(name=setting_name)
        if rows:
            value = rows[0].get('value')
            return rows[0].get('default') if value == '' else value


@parser(Specs.satellite_compute_resources)
class SatelliteComputeResources(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c 'select name, type from compute_resources' --csv``.

    .. note::
        Please refer to its super-class :class:`insights.parsers.satellite_postgresql_query.SatellitePostgreSQLQuery` for more
        details.

    Sample output::

        name,type
        test_compute_resource1,Foreman::Model::Libvirt
        test_compute_resource2,Foreman::Model::RHV

    Examples:
        >>> type(resources_table)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteComputeResources'>
        >>> rows=resources_table.search(type='Foreman::Model::Libvirt')
        >>> len(rows)
        1
        >>> rows[0]['name']
        'test_compute_resource1'
    """
    pass
