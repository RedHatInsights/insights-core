"""
HorizonLocalSettingsConf - file ``/etc/openstack-dashboard/local_settings``
===========================================================================

This module provides class ``HorizonLocalSettingsConf`` for parsing the
keyword-and-value in local_settings file.
Filters have been added so that PII sensitive information can be filtered out.
This will result in modification of the original structure of the data.

Example ``local_settings`` filtered data::

    OPENSTACK_API_VERSIONS = {
        'identity': 3,
    }
    POLICY_FILES = {
        'identity': 'keystone_policy.json',
        'identity.users': False,
        'identity.projects': False,
        'identity.groups': False,
        'identity.roles': False
    }
    OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
    OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'
    CACHES = {
        'default': {
        }
    }

Examples:
    >>> settings['OPENSTACK_API_VERSIONS']['identity']
    '3'
    >>> settings['OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT']
    'True'
    >>> settings['OPENSTACK_KEYSTONE_DEFAULT_DOMAIN']
    'Default'
    >>> settings.has_option('OPENSTACK_API_VERSIONS')
    True
"""

import re
from ast import literal_eval
from insights import parser, Parser, get_active_lines, LegacyItemAccess
from insights.core.filters import add_filter
from insights.parsers import ParseException, SkipException
from insights.specs import Specs

FILTERS = ["OPENSTACK_API_VERSIONS", "OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT", "OPENSTACK_KEYSTONE_DEFAULT_DOMAIN", "identity", "{", "}"]
add_filter(Specs.horizon_local_settings_conf, FILTERS)


@parser(Specs.horizon_local_settings_conf)
class HorizonLocalSettingsConf(LegacyItemAccess, Parser):
    """
       Class to parse ``local_settings`` openstack-dashboard configuration file.

       Generally, local_settings file contains data in key=value format with
       values having data types as string, numbers, list, tuple or dict.
       The class provides attribute ``data`` as dictionary with lines parsed
       line by line based on keys.

       Attributes:
           data (dict): A dictionary containing all the configuration parameters and values.
               Sample data::

                   {
                       'OPENSTACK_API_VERSIONS': {'identity': '3'},
                       'OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT': 'True',
                       'OPENSTACK_KEYSTONE_DEFAULT_DOMAIN': 'Default',
                        .......
                   }

       Raises:
        SkipException: When file is empty or value is not present for a key.
        ParseException: When no valid keys are found.
    """

    def parse_content(self, content):
        """
           Each line is searched for the first assignment operator to get the key
           and then the values are extracted and converted to the corresponding data types.
        """
        # No content found or file is empty
        if len(content) == 0:
            raise SkipException("Empty file")

        self.data = {}
        # Check if line does not starts with lowercase letters
        local_settings = "\n".join([setting for setting in get_active_lines(content) if not re.match(r"^[a-z]+", setting)])

        # Check if line contains a key
        keys = []
        for setting in local_settings.split("\n"):
            key = re.findall(r"^[A-Za-z_\[\]\"]*\s*=", setting)
            keys.extend(key) if len(key) > 0 else None

        # No valid keys are found
        if len(keys) == 0:
            raise ParseException("No valid keys found.")

        # Extract the keys and corresponding values from data and store in a dictionary
        for index, key in enumerate(keys):
            start = local_settings.index(key) + len(key) + 1
            d_key = key.strip("=").strip()
            # Value is not present for a key
            if (index < len(keys) - 1 and start == local_settings.index(keys[index + 1])) or \
                    (index + 1 == len(keys) and not local_settings[start:]):
                raise SkipException("Value not present for the key {0}.".format(d_key))
            # Extract the value of a key
            if keys.index(key) < len(keys) - 1:
                self.data[d_key] = local_settings[start:local_settings.index(keys[index + 1])]
            else:
                self.data[d_key] = local_settings[start:len(local_settings) + 1]
            self.data[d_key] = self.data[d_key].replace("'", "\"").strip("\n")

        # Convert the values from String to corresponding data types
        for k, v in self.data.items():
            # Boolean or Constant or Numbers to String
            if v[0].isalnum():
                self.data[k] = str(v)
            # String
            elif v.startswith("\""):
                self.data[k] = str(v[1:-1])
            # List or Tuple to List
            elif v[0] in ["[", "("]:
                v = v + "]" if v.startswith("[") and not v.endswith("]") else (v + ")")
                v = v[1:-1].replace("\"", "").split(",")
                for elem in v:
                    v[v.index(elem)] = elem.strip() if elem.strip("\n").startswith(" ") else elem.strip("\n")
                self.data[k] = v
            # Dictionary
            elif v.startswith("{"):
                v = re.sub(r":\s+([A-Za-z._0-9]+)", r': "\1"', v.replace("\n", "").strip())
                self.data[k] = literal_eval(v)

    def __getitem__(self, key):
        """Returns the value of the key from dictionary ``settings``"""
        return self.data[key]

    def has_option(self, key):
        """Returns ``True`` if settings has key ``key``"""
        return key in self.data.keys()
