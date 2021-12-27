"""
Satellite PostgreSQL database queries
=====================================

This module contains the following parsers:

SatelliteAdminSettings - command ``psql -d foreman -c 'select name, value, "default" from settings where name in (\'destroy_vm_on_host_delete\', \'unregister_delete_host\') --csv'``
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SatelliteComputeResources - command ``psql -d foreman -c 'select name, type from compute_resources' --csv``
-----------------------------------------------------------------------------------------------------------
SatelliteSCAStatus - command ``psql -d candlepin -c "select displayname, content_access_mode from cp_owner" --csv``
-------------------------------------------------------------------------------------------------------------------
SatelliteKatelloEmptyURLRepositories - command ``psql -d foreman -c 'select id, name from katello_root_repositories where url is NULL;' --csv``
-----------------------------------------------------------------------------------------------------------------------------------------------
SatelliteCoreTaskReservedResourceCount - command ``psql -d pulpcore -c 'select count(*) from core_taskreservedresource' --csv``
-------------------------------------------------------------------------------------------------------------------------------
"""

import os
import yaml
from csv import DictReader

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException
from insights.parsers import keyword_search, calc_offset


class SatellitePostgreSQLQuery(CommandParser, list):
    """
    Parent class of satellite postgresql table queries. It can not be used
    directly, A child class with overriding columns attribute is required.
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

    Raises:
        SkipException: when there isn't data in the table
        ParseException: when the output isn't in good csv format.
        NotImplementedError: when the subclass doesn't override the columns attribute.
    """

    # child class should override the columns attribute with its own column names
    columns = []

    def parse_content(self, content):
        if not self.columns:
            raise NotImplementedError("Please override the columns attribute.")
        start_index = calc_offset(content, self.columns, require_all=True)
        valid_lines = content[start_index:]
        reader = DictReader(os.linesep.join(valid_lines).splitlines(True))
        for row in reader:
            self.append(row)
        if not self:
            raise SkipException("There is no data in the table.")

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
    columns = ['name', 'value', 'default']

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
    columns = ['name', 'type']


@parser(Specs.satellite_katello_empty_url_repositories)
class SatelliteKatelloEmptyURLRepositories(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c 'select id, name from katello_root_repositories where url is NULL;' --csv``.

    Sample output::

        id,name
        54,testa
        55,testb

    Examples:
        >>> type(katello_root_repositories)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteKatelloEmptyURLRepositories'>
        >>> len(katello_root_repositories)
        2
        >>> katello_root_repositories[0]['name']
        'testa'
    """
    columns = ['id', 'name']


@parser(Specs.satellite_core_taskreservedresource_count)
class SatelliteCoreTaskReservedResourceCount(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d pulpcore -c 'select count(*) from core_taskreservedresource' --csv``.

    Sample output::

        count
        0

    Examples:
        >>> type(tasks)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteCoreTaskReservedResourceCount'>
        >>> tasks[0]['count']
        '0'
    """
    columns = ['count']


@parser(Specs.satellite_sca_status)
class SatelliteSCAStatus(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d candlepin -c "select displayname, content_access_mode from cp_owner" --csv``.

    Sample output::

        displayname,content_access_mode
        Default Organization,entitlement
        Orgq,org_environment

    Examples:
        >>> type(sat_sca_info)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteSCAStatus'>
        >>> sat_sca_info.sca_enabled
        True
    """

    columns = ['displayname', 'content_access_mode']

    @property
    def sca_enabled(self):
        """
        If the value of content_access_mode is "org_environment", it means the SCA is enabled for this organization.
        Return True if any organization has SCA enabled on the satellite else False
        """
        return bool(len(self.search(content_access_mode='org_environment')))
