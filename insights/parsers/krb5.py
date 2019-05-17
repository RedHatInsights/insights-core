"""
Krb5Configuration - files ``/etc/krb5.conf`` and ``/etc/krb5.conf.d/*``
=======================================================================

krb5 Configuration are ``/etc/krb5.conf`` and ``/etc/krb5.conf.d/*``,
and the content format is similar to ``INI config``, but they include
values that span multiple lines. Multi-line values start with a '{'
and end with a '}', and we join them together by setting the `is_squ`
variable to True while in a multi-line value.

Example:
    >>> krb5_content = '''
    [realms]
     dns_lookup_realm = false
     ticket_lifetime = 24h
     default_ccache_name = KEYRING:persistent:%{uid}
     EXAMPLE.COM = {
      kdc = kerberos.example.com
      admin_server = kerberos.example.com
     }
     pam = {
      debug = false
      krb4_convert = false
      ticket_lifetime = 36000
     }
     [libdefaults]
      dns_lookup_realm = false
      ticket_lifetime = 24h
      EXAMPLE.COM = {
       kdc = kerberos2.example.com
       admin_server = kerberos2.example.com
     }
    # renew_lifetime = 7d
    # forwardable = true
    # rdns = false
    '''.strip()

    >>> from insights.tests import context_wrap
    >>> shared = {Krb5Configuration: Krb5Configuration(context_wrap(krb5_content))}
    >>> krb5_info = shared[Krb5Configuration]
    >>> krb5_info["libdefaults"]["dnsdsd"]
    "false"
    >>> krb5_info["realms"]["EXAMPLE.COM"]["kdc"]
    "kerberos.example.com"
    >>> krb5_info.sections()
    ["libdefaults","realms"]
    >>> krb5_info.has_section("realms")
    True
    >>> krb5_info.has_option("realms", "nosuchoption")
    False
    >>> krb5_info.options("libdefaults")
    ["dns_lookup_realm","ticket_lifetime","EXAMPLE.COM"]
"""


from .. import parser, Parser, get_active_lines, LegacyItemAccess
from insights.specs import Specs


PREFIX_FOR_LIST = ("includedir", "include", "module")


def _handle_key_value(t_dict, key, value):
    """
    Function to handle key has multi value, and return the values as list.
    """
    if key in t_dict:
        val = t_dict[key]
        if isinstance(val, str):
            val = [val]
        val.append(value)
        return val
    return value


@parser(Specs.krb5)
class Krb5Configuration(Parser, LegacyItemAccess):
    """
    Class for ``krb5.conf`` and ``krb5.conf.d`` configuration files.

    The Kerberos .ini format is like an ordinary .ini file except that values
    can include a multiple line key-value pair 'relation' that starts with a
    '{' and end with a '}' on a trailing line.  So we track whether we're in
    curly braces by setting `is_squ` when we enter a relation, and clearing
    it when we leave.  Please fill in the remainder of the logic here.

    Attributes:
        includedir (list): The directory list that `krb5.conf` includes via
            `includedir` directive
        include (list): The configuration file list that `krb5.conf` includes
            via `include` directive
        module (list): The module list that `krb5.conf` specifed via `module`
            directive
    """

    def parse_content(self, content):
        dict_all = {}
        is_squ = False
        section_name = ""
        squ_value = {}
        squ_section_name = ""
        section_value = {}
        self.includedir = []
        self.include = []
        self.module = []
        for line in get_active_lines(content):
            line = line.strip()
            if line.startswith(PREFIX_FOR_LIST):
                key, value = [i.strip() for i in line.split(None, 1)]
                getattr(self, key).append(value) if key in PREFIX_FOR_LIST else None
                continue
            if is_squ:
                # If in {} sub_section, get the key_value pair
                if "=" in line:
                    key, value = [i.strip() for i in line.split('=', 1)]
                    squ_value[key] = _handle_key_value(squ_value, key, value)
                    if line.endswith("*"):
                        section_value[squ_section_name] = squ_value
                        break
                # The {} sub_section should end with },
                # if it is, set the whole value to the sub_section name,
                # and clean the flag
                else:
                    section_value[squ_section_name] = squ_value
                    is_squ = False
                    squ_section_name = ""
                    squ_value = {}
            else:
                # [XXX] means a section, get the section name and the value
                # format is dict.
                if line.startswith("[") and line.endswith("]"):
                    # If first section, just get the section name,
                    # if not, set the value to the former section and
                    # get the section name
                    section_name = line.strip("[]")
                    section_value = {}
                    if section_name:
                        dict_all[section_name] = section_value
                # key value format is XXX = YYY, store as dict
                elif "=" in line and not line.endswith("{"):
                    key, value = [i.strip() for i in line.split('=', 1)]
                    section_value[key] = _handle_key_value(section_value, key, value)
                    if line.endswith("*"):
                        break
                # The {} sub_section should start with format XXX = {
                else:
                    is_squ = True
                    squ_section_name = line.split("=")[0].strip()
        self.data = dict_all

    def sections(self):
        """
        Return a list of section names.
        """
        return self.data.keys()

    def has_section(self, section):
        """
        Indicate whether the named section is present in the configuration.
        Return True if the given section is present, and False if not present.
        """
        return section in self.data

    def options(self, section):
        """
        Return a list of option names for the given section name.
        """
        return self.data[section].keys() if self.has_section(section) else []

    def has_option(self, section, option):
        """
        Check for the existence of a given option in a given section.
        Return True if the given option is present, and False if not present.
        """
        if section not in self.data:
            return False
        return option in self.data[section]
