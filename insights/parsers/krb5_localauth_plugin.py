"""
Krb5 localauth_plugin configuration - file ``/var/lib/sss/pubconf/krb5.include.d/localauth_plugin``
===================================================================================================
"""
from insights.core import Parser, LegacyItemAccess
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.krb5_localauth_plugin)
class Krb5LocalauthPlugin(Parser, LegacyItemAccess):
    """
    This parser is used to parse the file "/var/lib/sss/pubconf/krb5.include.d/localauth_plugin"

    Sample input::

        [plugins]
         localauth = {
          module = sssd:/usr/lib64/sssd/modules/sssd_krb5_localauth_plugin.so
         }

    Examples:

        >>> type(conf)
        <class 'insights.parsers.krb5_localauth_plugin.Krb5LocalauthPlugin'>
        >>> conf['plugins']['localauth']['module']
        'sssd:/usr/lib64/sssd/modules/sssd_krb5_localauth_plugin.so'
    """
    def parse_content(self, content):
        dict_all = {}
        section_name = ""
        sub_section = ""
        for line in get_active_lines(content):
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                section_name = line.strip("[]")
                section_value = {}
                if section_name:
                    dict_all[section_name] = section_value
            elif "=" in line and line.endswith("{"):
                sub_section = line.split("=")[0].strip()
                dict_all[section_name][sub_section] = {}
            elif "=" in line and not line.endswith("{"):
                key, value = line.split("=", 1)
                dict_all[section_name][sub_section][key.strip()] = value.strip()
        self.data = dict_all
