"""
HorizonLocalSettingsConf - file ``/etc/openstack-dashboard/local_settings``
===========================================================================

This module provides class ``HorizonLocalSettingsConf`` for parsing the
keyword-and-value in local_settings file.
Filters have been added so that PII sensitive information can be filtered out.
This will result in modification of the original structure of the data.

Example ``local_settings`` file::

    import os

    from django.utils.translation import ugettext_lazy as _

    from openstack_dashboard import exceptions
    from openstack_dashboard.settings import HORIZON_CONFIG

    DEBUG = False

    LOGOUT_URL = '/dashboard/auth/logout/'

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    OPENSTACK_API_VERSIONS = {
      'identity': 3,

    }

    OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True

    OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'Default'

    HORIZON_CONFIG["images_panel"] = "legacy"

    OPENSTACK_KEYSTONE_BACKEND = {
        'can_edit_domain': True,
        'can_edit_group': True,
        'can_edit_project': True,
        'can_edit_role': True,
        'can_edit_user': True,
        'name': 'native',
    }

    API_RESULT_LIMIT = 1000
    API_RESULT_PAGE_SIZE = 20

    SECURITY_GROUP_RULES = {
        'all_tcp': {
            'name': 'ALL TCP',
            'ip_protocol': 'tcp',
            'from_port': '1',
            'to_port': '65535',
        },
        'all_udp': {
            'name': 'ALL UDP',
            'ip_protocol': 'udp',
            'from_port': '1',
            'to_port': '65535',
        },
        'all_icmp': {
            'name': 'ALL ICMP',
            'ip_protocol': 'icmp',
            'from_port': '-1',
            'to_port': '-1',
        },
        'ssh': {
            'name': 'SSH',
            'ip_protocol': 'tcp',
            'from_port': '22',
            'to_port': '22',
        },
        'smtp': {
            'name': 'SMTP',
            'ip_protocol': 'tcp',
            'from_port': '25',
            'to_port': '25',
        },
        'dns': {
            'name': 'DNS',
            'ip_protocol': 'tcp',
            'from_port': '53',
            'to_port': '53',
        },
    }

    REST_API_REQUIRED_SETTINGS = ['OPENSTACK_HYPERVISOR_FEATURES',
                                  'LAUNCH_INSTANCE_DEFAULTS',
                                  'OPENSTACK_IMAGE_FORMATS']

    LAUNCH_INSTANCE_DEFAULTS = {
        'config_drive': False,
        'enable_scheduler_hints': True,
        'disable_image': True,
        'disable_instance_snapshot': True,
        'disable_volume': False,
        'disable_volume_snapshot': False,
        'create_volume': True,
    }

    DISALLOW_IFRAME_EMBED = True

Examples:
    >>> settings['OPENSTACK_API_VERSIONS']['identity']
    '3'
    >>> settings['OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT']
    'False'
    >>> settings['OPENSTACK_KEYSTONE_DEFAULT_DOMAIN']
    'Default'
    >>> settings.has_option('OPENSTACK_API_VERSIONS')
    True
"""

import re
from ast import literal_eval
from insights import parser, Parser, get_active_lines
from insights.core.filters import add_filter
from insights.parsers import ParseException, SkipException
from insights.specs import Specs

FILTERS = ["OPENSTACK_API_VERSIONS", "OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT", "OPENSTACK_KEYSTONE_DEFAULT_DOMAIN", "identity"]
add_filter(Specs.horizon_local_settings_conf, FILTERS)


@parser(Specs.horizon_local_settings_conf)
class HorizonLocalSettingsConf(Parser):
    """
       Class to parse ``local_settings`` openstack-dashboard configuration file.

       Generally, local_settings file contains data in key=value format with
       values having data types as string, numbers, list, tuple or dict.
       The class provides attribute ``settings`` as dictionary with lines parsed
       line by line based on keys.

       Attributes:
           settings (dict): A dictionary containing all the configuration parameters and values.
               Sample data::

                   {
                       'DEBUG': 'False',
                       'LOGOUT_URL': '/dashboard/auth/logout/',
                       'SECURE_PROXY_SSL_HEADER': ['HTTP_X_FORWARDED_PROTO', 'https'],
                       'OPENSTACK_API_VERSIONS': {'identity': '3'},
                       'OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT': 'True',
                       'OPENSTACK_KEYSTONE_DEFAULT_DOMAIN': 'Default',
                       'HORIZON_CONFIG["images_panel"]': 'legacy',
                       'OPENSTACK_KEYSTONE_BACKEND': {
                           'can_edit_domain': 'True',
                           'can_edit_group': 'True',
                           'can_edit_project': 'True',
                           'can_edit_role': 'True',
                           'can_edit_user': 'True',
                           'name': 'native'
                        },
                        'API_RESULT_LIMIT': '1000',
                        'POLICY_FILES_PATH': '/etc/openstack-dashboard',
                        'REST_API_REQUIRED_SETTINGS': ['OPENSTACK_HYPERVISOR_FEATURES', 'LAUNCH_INSTANCE_DEFAULTS', 'OPENSTACK_IMAGE_FORMATS'],
                        .......
                   }
    """

    def parse_content(self, data):
        """
           Each line is searched for the first assignment operator to get the key
           and then the values are extracted and converted to the corresponding data types.
        """
        # No data found or file is empty
        if len(data) == 0:
            raise ParseException("Empty file")

        self.settings = {}
        # Check if line does not starts with lowercase letters
        local_settings = "\n".join([setting for setting in get_active_lines(data) if not re.match(r"^[a-z]+", setting)])

        # Check if line contains a key
        keys = []
        for setting in local_settings.split("\n"):
            key = re.findall(r"^[A-Z_\[\]\"]*\s*=", setting)
            keys.extend(key) if len(key) > 0 else None

        # No valid keys are found
        if len(keys) == 0:
            raise ParseException("No valid keys found.")

        # Extract the keys and corresponding values from data and store in a dictionary
        for key in range(len(keys)):
            start = local_settings.index(keys[key]) + len(keys[key]) + 1
            d_key = keys[key].strip("=").strip()
            # Value is not present for a key
            if (key < len(keys) - 1 and start == local_settings.index(keys[key + 1])) or \
                    (key + 1 == len(keys) and not local_settings[start:]):
                raise SkipException("Value not present for the key {0}.".format(d_key))
            newline_index = local_settings[start:].find("\n")
            if newline_index != -1:
                check = local_settings[start:start + newline_index]
            else:
                check = local_settings[start:start + local_settings[start:].find("\"", 2) + 1]
            if re.match(r"^[A-Za-z0-9\"]", check.replace("'", "\"")):
                self.settings[d_key] = check
            else:
                if key < len(keys) - 1:
                    self.settings[d_key] = local_settings[start:local_settings.index(keys[key + 1])]
                else:
                    self.settings[d_key] = local_settings[start:len(local_settings) + 1]
            self.settings[d_key] = self.settings[d_key].replace("'", "\"").strip("\n")

        # Convert the values from String to corresponding data types
        for k, v in self.settings.items():
            # Boolean or Constant or Numbers to String
            if v[0].isalnum():
                self.settings[k] = str(v)
            # String
            elif v.startswith("\""):
                self.settings[k] = str(v[1:-1])
            # List or Tuple to List
            elif v.startswith("[") or v.startswith("("):
                v = v[1:-1].replace("\"", "").split(",")
                for elem in v:
                    v[v.index(elem)] = elem.strip() if elem.strip("\n").startswith(" ") else elem.strip("\n")
                self.settings[k] = v
            # Dictionary
            elif v.startswith("{"):
                v = v + "}" if not v.endswith("}") else v
                v = re.sub(r":\s+([A-Za-z._0-9]+)", r': "\1"', v.replace("\n", "").strip())
                if v.count("{") == 1:
                    dup_list = re.findall(r"\"[A-Za-z0-9._]+\":", v)
                    dup_key = [key[:-1] for key in dup_list if (dup_list.count(key) > 1)]
                    first_key = {}
                    for dup in dup_key:
                        pattern = r"{0}:\s*\".+?\",|{1}:\s*[A-Za-z0-9_.],".format(dup, dup)
                        first_key[dup[1:-1]] = re.findall(pattern.strip(","), v)[0].split(":")[1].strip()
                        v = re.sub(pattern, "", v)
                        v = v[0] + dup + ": " + first_key[dup[1:-1]] + v[1:]
                self.settings[k] = literal_eval(v)

    def __getitem__(self, key):
        """Returns the value of the key from dictionary ``settings``"""
        return self.settings[key]

    def has_option(self, key):
        """Returns ``True`` if settings has key ``key``"""
        return key in self.settings.keys()
