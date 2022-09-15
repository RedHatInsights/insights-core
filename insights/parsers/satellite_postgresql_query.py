"""
Satellite PostgreSQL database queries
=====================================

This module contains the following parsers:

SatelliteAdminSettings - command ``psql -d foreman -c 'select name, value, "default" from settings where name in (\'destroy_vm_on_host_delete\', \'unregister_delete_host\') --csv'``
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SatelliteComputeResources - command ``psql -d foreman -c 'select name, type from compute_resources' --csv``
-----------------------------------------------------------------------------------------------------------
SatelliteCoreTaskReservedResourceCount - command ``psql -d pulpcore -c 'select count(*) from core_taskreservedresource' --csv``
-------------------------------------------------------------------------------------------------------------------------------
SatelliteKatellloReposWithMultipleRef - command ``psql -d foreman -c "select repository_href, count(*) from katello_repository_references group by repository_href having count(*) > 1;" --csv``
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SatelliteLogsTableSize - command ``psql -d foreman -c "select pg_total_relation_size('logs') as logs_size" --csv``
------------------------------------------------------------------------------------------------------------------
SatelliteProvisionParamSettings - command ``psql -d foreman -c "select name, value from parameters where name='package_upgrade' and reference_id in (select id from operatingsystems where name='RedHat' and major='9')" --csv``
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SatelliteQualifiedCapsules - command ``psql -d foreman -c "select name from smart_proxies where download_policy = 'background'" --csv``
---------------------------------------------------------------------------------------------------------------------------------------
SatelliteQualifiedKatelloRepos - command ``psql -d foreman -c "select id, name, url, download_policy from katello_root_repositories where download_policy = 'background' or url is NULL" --csv``
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
SatelliteSCAStatus - command ``psql -d candlepin -c "select displayname, content_access_mode from cp_owner" --csv``
-------------------------------------------------------------------------------------------------------------------
"""

import os
import yaml
from csv import DictReader

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException
from insights.parsers import keyword_search, calc_offset
from insights.util import deprecated


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
        ParseException: when the output isn't in good csv format or the yaml values aren't in good yaml format
        NotImplementedError: when the subclass doesn't override the columns attribute.
    """

    # child class should override the columns attribute with its own column names
    columns = []
    # child class should define the columns_in_yaml when some columns value are in yaml format,
    # which should be transfered to python object
    columns_in_yaml = []

    def _parse_yaml(self, value):
        if value:
            try:
                return yaml.safe_load(value)
            except Exception:
                raise ParseException("Bad format value: %s" % value)
        return value

    def parse_content(self, content):
        if not self.columns:
            raise NotImplementedError("Please override the columns attribute.")
        start_index = calc_offset(content, self.columns, require_all=True)
        if 'Last login:' in content[-1]:
            valid_lines = content[start_index:-1]
        else:
            valid_lines = content[start_index:]
        reader = DictReader(os.linesep.join(valid_lines).splitlines(True))
        for row in reader:
            for name in self.columns_in_yaml:
                row[name] = self._parse_yaml(row[name])
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
    columns_in_yaml = ['value', 'default']

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


@parser(Specs.satellite_katello_empty_url_repositories)
class SatelliteKatelloEmptyURLRepositories(SatellitePostgreSQLQuery):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.satellite_postgresql_query.SatelliteQualifiedKatelloRepos` instead.

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

    def __init__(self, *args, **kwargs):
        deprecated(
            SatelliteKatelloEmptyURLRepositories,
            "Please use the SatelliteQualifiedKatelloRepos parser in the current module.",
            "3.1.25"
        )
        super(SatelliteKatelloEmptyURLRepositories, self).__init__(*args, **kwargs)


@parser(Specs.satellite_logs_table_size)
class SatelliteLogsTableSize(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c "select pg_total_relation_size('logs') as logs_size" --csv``.

    Sample output::

        logs_size
        565248

    Examples:
        >>> type(logs_table)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteLogsTableSize'>
        >>> logs_table[0]['logs_size']
        565248

    Raises:
        ParseException: when the size is not in integer type
    """
    columns = ['logs_size']

    def parse_content(self, content):
        super(SatelliteLogsTableSize, self).parse_content(content)
        for row in self:
            if not row['logs_size'].isdigit():
                raise ParseException('Not expected logs size %s.' % row['logs_size'])
            row['logs_size'] = int(row['logs_size'])


@parser(Specs.satellite_provision_param_settings)
class SatelliteProvisionParamSettings(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c "select name, value from parameters where name='package_upgrade' and reference_id in (select id from operatingsystems where name='RedHat' and major='9')" --csv``.

    Sample output::

        name,value
        package_upgrade,"--- false
        ...
        "

    Examples:
        >>> type(param_settings)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteProvisionParamSettings'>
        >>> len(param_settings)
        1
        >>> param_settings[0]['value']
        False
    """
    columns = ['name', 'value']
    columns_in_yaml = ['value']


@parser(Specs.satellite_katello_repos_with_muliple_ref)
class SatelliteKatellloReposWithMultipleRef(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c "select repository_href, count(*) from katello_repository_references group by repository_href having count(*) > 1;" --csv``.

    Sample output::

        repository_href,count
        /pulp/api/v3/repositories/rpm/rpm/64e1ddf8-025e-45f2-b2f0-04b874674671/,3
        /pulp/api/v3/repositories/rpm/rpm/sfwrsrw45sfse-45f2-b2f0-04b874675688/,2

    Examples:
        >>> type(multi_ref_katello_repos)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteKatellloReposWithMultipleRef'>
        >>> len(multi_ref_katello_repos)
        2
        >>> multi_ref_katello_repos[0]['repository_href']
        '/pulp/api/v3/repositories/rpm/rpm/64e1ddf8-025e-45f2-b2f0-04b874674671/'
    """
    columns = ['repository_href', 'count']


@parser(Specs.satellite_qualified_katello_repos)
class SatelliteQualifiedKatelloRepos(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c "select id, name, url, download_policy from katello_root_repositories where download_policy = 'background' or url is NULL" --csv``.

    Sample output::

        id,name,url,download_policy
        2,Red Hat Satellite Tools 6.8 for RHEL 7 Server RPMs x86_64,,on_demand
        3,Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8,https://cdn.redhat.com/content/dist/rhel8/8/x86_64/appstream/os,background
        4,Red Hat Enterprise Linux 7 Server RPMs x86_64 7Server,https://cdn.redhat.com/content/dist/rhel/server/7/7Server/x86_64/os,background

    Examples:
        >>> type(repos)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteQualifiedKatelloRepos'>
        >>> len(repos)
        3
        >>> repos[0]['name']
        'Red Hat Satellite Tools 6.8 for RHEL 7 Server RPMs x86_64'
    """
    columns = ['id', 'name', 'url', 'download_policy']


@parser(Specs.satellite_qualified_capsules)
class SatelliteQualifiedCapsules(SatellitePostgreSQLQuery):
    """
    Parse the output of the command ``psql -d foreman -c "select name from smart_proxies where download_policy = 'background'" --csv``.

    Sample output::

        name
        capsule1.test.com
        capsule2.test.com

    Examples:
        >>> type(capsules)
        <class 'insights.parsers.satellite_postgresql_query.SatelliteQualifiedCapsules'>
        >>> len(capsules)
        2
        >>> capsules[0]['name']
        'capsule1.test.com'
    """
    columns = ['name']


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
