"""
SambaConfig - file ``/etc/samba/smb.conf``
==========================================
"""
import re

from insights.core import IniConfigFile
from insights.core.filters import add_filter
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsr import iniparser
from insights.specs import Specs

add_filter(Specs.samba, ["["])

add_filter(Specs.testparm_s, ["["])
add_filter(Specs.testparm_s, ["Server role:"])

add_filter(Specs.testparm_v_s, ["["])
add_filter(Specs.testparm_v_s, ["Server role:"])


@parser(Specs.samba)
class SambaConfig(IniConfigFile):
    """
    This parser reads the Samba configuration file ``/etc/samba/smb.conf``, which
    is in standard .ini format, with a couple of notable features:

    Note: It is needed for better resolution descriptions when it is necessary to know what exactly
    is in the configuration file. For generic tasks use ``SambaConfigs`` or ``SambaConfigsAll``
    instead.

    * Samba ignores spaces at the start of options, which the ConfigParser class
      normally does not. This spacing is stripped by this parser.
    * Samba likewise ignores spaces in section heading names.
    * Samba allows the same section to be defined multiple times, with the
      options therein being merged as if they were one section.
    * Samba allows options to be declared before the first section marker.
      This parser puts these options in a `global` section.
    * Samba treats ';' as a comment prefix, similar to '#'.

    Sample configuration file::

        # This is the main Samba configuration file. You should read the
        # smb.conf(5) manual page in order to understand the options listed
        #...
        #======================= Global Settings =====================================

        [global]
            workgroup = MYGROUP
            server string = Samba Server Version %v
            max log size = 50

        [homes]
            comment = Home Directories
            browseable = no
            writable = yes
        ;   valid users = %S
        ;   valid users = MYDOMAIN\%S

        [printers]
            comment = All Printers
            path = /var/spool/samba
            browseable = no
            guest ok = no
            writable = no
            printable = yes

        # A publicly accessible directory, but read only, except for people in
        # the "staff" group
        [public]
           comment = Public Stuff
           path = /home/samba
           public = yes
           writable = yes
           printable = no
           write list = +staff

    Examples:
        >>> type(conf)
        <class 'insights.parsers.samba.SambaConfig'>
        >>> sorted(conf.sections()) == [u'global', u'homes', u'printers', u'public']
        True
        >>> global_options = conf.items('global')  # get a section as a dictionary
        >>> type(global_options) == type({})
        True
        >>> conf.get('public', 'comment') == u'Public Stuff'  # Accessor for section and option
        True
        >>> conf.getboolean('public', 'writable')  # Type conversion, but no default
        True
        >>> conf.getint('global', 'max log size')  # Same for integer conversion
        50
    """
    def parse_doc(self, content):
        # smb.conf is special from other ini files in the property that
        # whatever is before the first section (before the first section)
        # belongs to the [global] section. Therefore, the [global] section is
        # appended right at the beginning so that everything that would be
        # parsed as outside section belongs to [global].
        # Python 2.7 RawConfigParser automatically merges multiple instances
        # of the same section.  (And if that ever changes, test_samba.py will
        # catch it.)
        lstripped = ["[global]"] + [line.lstrip() for line in content]
        return iniparser.parse_doc("\n".join(lstripped), self, return_defaults=True, return_booleans=False)

    def parse_content(self, content):
        super(SambaConfig, self).parse_content(content)
        self._dict = dict()

        # Transform the section names so that whitespace around is stripped
        # and they are lowercase. smb.conf is special in the property that
        # section names and option names are case-insensitive and treated
        # like lower-case.
        for section in self.doc:
            section_dict = dict()
            _section = section.name.lower()

            for opt in section:
                options = []
                for o in section[opt.name]:
                    if o.value is not None:
                        options.append(str(o.value))
                    else:
                        options.append(o.value)

                section_dict[opt.name.lower()] = options[-1]

            if _section in self._dict:
                self._dict[_section].update(section_dict)
            else:
                self._dict[_section] = section_dict


@parser(Specs.testparm_s)
class SambaConfigs(SambaConfig):
    """
    This parser reads the Samba configuration from command `testparm -s` which is more reliable
    than parsing the config file, as it includes configuration in internal registry. It also
    includes server role.

    Note: This is the most suitable parser when only user changes to the configuration are important
    for the detection logic, i.e. misconfiguration.

    Attributes:
        server_role (string): Server role as reported by the command.
    """
    def parse_content(self, content):
        # Parse server role
        # The output of `testparm` sometimes includes progress lines such as
        # `Processing section "[homes]"`. These lines are output before the server
        # role definition, so only pass output from that line onward.
        server_role_line = None
        for i, line in enumerate(content):
            r = re.search(r"Server role:\s+(\S+)", line)
            if r:
                self.server_role = r.group(1)
                server_role_line = i
                break

        if server_role_line is None:
            raise ParseException("Server role not found.")

        super(SambaConfigs, self).parse_content(content[server_role_line:])


@parser(Specs.testparm_v_s)
class SambaConfigsAll(SambaConfigs):
    """
    This parser reads the Samba configuration from command `testparm -v -s` which is more reliable
    than parsing the config file, as it includes configuration in internal registry. It also
    includes all default values and server role.

    Note: This parser is needed for cases when active value of specific option is needed for the
    detection logic, irrespective of its origin from user changes or defaults, i.e. security
    vulnerabilities.

    Attributes:
        server_role (string): Server role as reported by the command.
    """
    pass
