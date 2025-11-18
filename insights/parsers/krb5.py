"""
Configuration Parsers for Krb5
==============================

Below parsers are included:

Krb5Configuration - files ``/etc/krb5.conf`` and ``/etc/krb5.conf.d/*``
-----------------------------------------------------------------------

Krb5LocalauthPlugin - file ``/var/lib/sss/pubconf/krb5.include.d/localauth_plugin``
-----------------------------------------------------------------------------------
"""

from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import parse_bool


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


class Krb5ConfBase(Parser, dict):
    """
    Base Class to process the Kerberos relevant configurations.

    The Kerberos Configuration are generally in .ini format. it is like an
    ordinary .ini file except that values can include a multiple line key-value
    pair 'relation' that starts with a '{' and end with a '}' on a trailing line.
    So we track whether we're in curly braces by setting `is_squ` when we enter
    a relation, and clearing it when we leave.  Please fill in the remainder of
    the logic here.

    """

    RESERVED_ATTRS = None

    def parse_content(self, content):
        if self.RESERVED_ATTRS is None:
            raise RuntimeError('Not applied when "RESERVED_ATTRS" does not exist')
        for key in self.RESERVED_ATTRS:
            setattr(self, key, [])
        dict_all = {}
        is_squ = False
        section_name = ""
        squ_value = {}
        squ_section_name = ""
        section_value = {}
        unchangeable_tags = []
        for line in content:
            line = line.strip()
            if not line or line.startswith('#'):
                # skip empty and commented lines
                continue
            if line.startswith(self.RESERVED_ATTRS):
                key, value = [i.strip() for i in line.split(None, 1)]
                if key in self.RESERVED_ATTRS:
                    getattr(self, key).append(value)
                    continue
            if is_squ:
                # If in {} sub_section, get the key_value pair
                if "=" in line:
                    key, value = [i.strip() for i in line.split('=', 1)]
                    if key not in unchangeable_tags:
                        value = value.split()[0] if value else value
                        squ_value[key] = _handle_key_value(squ_value, key, value)
                    if line.endswith("*"):
                        unchangeable_tags.append(key)
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
                    if key not in unchangeable_tags:
                        value = value.split()[0] if value else value
                        section_value[key] = _handle_key_value(section_value, key, value)
                    if line.endswith("*"):
                        unchangeable_tags.append(key)
                # The {} sub_section should start with format XXX = {
                else:
                    is_squ = True
                    squ_section_name = line.split("=")[0].strip()
        if dict_all:
            self.update(dict_all)
        elif not any(getattr(self, key) for key in self.RESERVED_ATTRS):
            raise SkipComponent()

    @property
    def data(self):
        """
        Keep backward compatibility. The "data" atrribute is deprecated,
        the parser itself is dictionary.

        .. warning::
            This will be removed from 3.8.0.
        """
        return self

    def sections(self):
        """
        Return a list of section names.
        """
        return sorted(self.keys())

    def has_section(self, section):
        """
        Indicate whether the named section is present in the configuration.
        Return True if the given section is present, and False if not present.
        """
        return section in self

    def options(self, section):
        """
        Return a list of option names for the given section name.
        """
        return sorted(self[section].keys()) if self.has_section(section) else []

    def has_option(self, section, option):
        """
        Check for the existence of a given option in a given section.
        Return True if the given option is present, and False if not present.
        """
        return False if section not in self else option in self[section]

    def getboolean(self, section, option):
        """Parse option as bool

        Returns None is not a krb5.conf boolean string.
        """
        return parse_bool(self[section][option], default=None)


@parser(Specs.krb5)
class Krb5Configuration(Krb5ConfBase):
    """
    Krb5 Configuration are ``/etc/krb5.conf`` and ``/etc/krb5.conf.d/*``.

    See :class:`Krb5ConfBase` for details.

    Attributes:
        includedir (list): The directory list that `krb5.conf` includes via
            `includedir` directive
        include (list): The configuration file list that `krb5.conf` includes
            via `include` directive
        module (list): The module list that `krb5.conf` specifed via `module`
            directive

    Sample content::

        include /etc/krb5test.conf
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
          dnsdsd = false
          ticket_lifetime = 24h
          EXAMPLE.COM = {
           kdc = kerberos2.example.com
           admin_server = kerberos2.example.com
         }

    Example:
        >>> type(krb5_conf)
        <class 'insights.parsers.krb5.Krb5Configuration'>
        >>> krb5_conf["libdefaults"]["dnsdsd"]
        'false'
        >>> krb5_conf["realms"]["EXAMPLE.COM"]["kdc"]
        'kerberos.example.com'
        >>> krb5_conf.sections()
        ['libdefaults', 'realms']
        >>> krb5_conf.has_section("realms")
        True
        >>> krb5_conf.has_option("realms", "nosuchoption")
        False
        >>> krb5_conf.options("libdefaults")
        ['EXAMPLE.COM', 'dns_lookup_realm', 'dnsdsd', 'ticket_lifetime']
        >>> krb5_conf.include
        ['/etc/krb5test.conf']
    """

    RESERVED_ATTRS = ("includedir", "include", "module")


@parser(Specs.krb5_localauth_plugin)
class Krb5LocalauthPlugin(Krb5ConfBase):
    """
    Krb5 Configuration parser for `/var/lib/sss/pubconf/krb5.include.d/localauth_plugin`

    Sample input::

        [plugins]
         localauth = {
          module = sssd:/usr/lib64/sssd/modules/sssd_krb5_localauth_plugin.so
         }

    Examples:
        >>> type(krb5_LP)
        <class 'insights.parsers.krb5.Krb5LocalauthPlugin'>
        >>> krb5_LP['plugins']['localauth']['module']
        'sssd:/usr/lib64/sssd/modules/sssd_krb5_localauth_plugin.so'
    """

    RESERVED_ATTRS = ()
