"""
SambaConfig - file ``/etc/samba/smb.conf``
==========================================

This parser reads the SaMBa configuration file ``/etc/samba/smb.conf``, which
is in standard .ini format, with a couple of notable features:

* SaMBa ignores spaces at the start of options, which the ConfigParser class
  normally does not.  This spacing is stripped by this parser.
* SaMBa likewise ignores spaces in section heading names.
* SaMBa allows the same section to be defined multiple times, with the
  options therein being merged as if they were one section.
* SaMBa allows options to be declared before the first section marker.
  This parser puts these options in a `global` section.
* SaMBa treats ';' as a comment prefix, similar to '#'.

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

from .. import add_filter, IniConfigFile, parser
from insights.specs import Specs

add_filter(Specs.samba, ["["])


@parser(Specs.samba)
class SambaConfig(IniConfigFile):
    """
    This parser reads the SaMBa configuration file ``/etc/samba/smb.conf``.
    """

    def parse_content(self, content):
        # smb.conf is special from other ini files in the property that
        # whatever is before the first section (before the first section)
        # belongs to the [global] section. Therefore, the [global] section is
        # appended right at the beginning so that everything that would be
        # parsed as outside section belongs to [global].
        # Python 2.7 RawConfigParser automatically merges multiple instances
        # of the same section.  (And if that ever changes, test_samba.py will
        # catch it.)
        lstripped = ["[global]"] + [line.lstrip() for line in content]

        super(SambaConfig, self).parse_content(lstripped)

        # Create a new instance of the same dict type used by the underlying
        # RawConfigParser.
        new_dict = self.data._dict()
        # Transform the section names so that whitespace around is stripped
        # and they are lowercase. smb.conf is special in the property that
        # section names and option names are case-insensitive and treated
        # like lower-case.
        for old_key, old_section in self.data._sections.items():
            new_key = old_key.strip().lower()
            if new_key not in new_dict:
                new_dict[new_key] = self.data._dict()
            # Merge same-named sections just as samba's `testparm` does.
            new_dict[new_key].update(old_section)
        self.data._sections = new_dict
