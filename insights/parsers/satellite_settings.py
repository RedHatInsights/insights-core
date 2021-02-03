"""
SatelliteSettings - command ``psql -d foreman -c 'select name, value, "default" from settings where name in (\'destroy_vm_on_host_delete\', \'unregister_delete_host\')'``
==========================================================================================================================================================================

The SatelliteSettings parser reads the output of
``psql -d foreman -c 'select name, value, "default" from settings where name in (\'destroy_vm_on_host_delete\', \'unregister_delete_host\')'``.

Sample output of ``psql -d foreman -c 'select name, value, "default" from settings where name in (\'destroy_vm_on_host_delete\', \'unregister_delete_host\')'``::

            name            |  value   |  default
    ---------------------------+----------+-----------
    unregister_delete_host    | --- true+| --- false+
                            | ...      | ...
    destroy_vm_on_host_delete |          | --- true +
                            |          | ...
    (2 rows)


Examples::

    >>> type(settings)
    <class 'insights.parsers.satellite_settings.SatelliteSettings'>
    >>> 'unregister_delete_host' in settings
    True
    >>> settings['unregister_delete_host']
    True
    >>> len(settings)
    2
    >>> settings['destroy_vm_on_host_delete']
    True
"""

import os
import yaml

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException


@parser(Specs.satellite_settings)
class SatelliteSettings(CommandParser, dict):
    """
    Read the ``psql -d foreman -c '"select name, value, "defualt" from settings where name in ('destroy_vm_on_host_delete', 'unregister_delete_host')"``
    and save the data to itself as a dict.
    """

    def parse_content(self, content):
        columns = ['name', 'value', 'default']
        if len(content) >= 4 and all(column in content[0] for column in columns):
            rows = content[2:]  # skip title and '---'
            name = val = new_val = ''
            for row in rows:
                if '|' not in row:
                    continue
                data = row.split('|')
                if len(data) != len(columns):
                    raise SkipException("The returned data is in bad format")
                if not name:
                    name, val, default_val = [item.strip() for item in data]
                else:
                    _, new_val, new_default_val = [item.strip() for item in data]
                    if val.endswith('+'):
                        val = val.rstrip(' +') + os.linesep + new_val
                    if default_val.endswith('+'):
                        default_val = default_val.rstrip(' +') + os.linesep + new_default_val
                if not (val.endswith('+') or default_val.endswith('+')):
                    real_val = val or default_val
                    try:
                        self[name] = yaml.safe_load(real_val)
                    except Exception:
                        raise ParseException('Could not parse the value for satellite settings of name %s ' % name)
                    name = val = new_val = ''
        if not self:
            raise SkipException("Cannot get the satellite settings")
