from .. import add_filter, IniConfigFile, parser
from insights.specs import samba

add_filter("samba", ["["])


@parser(samba)
class SambaConfig(IniConfigFile):
    """
        smb.conf file parser.

        Unfortunately, Samba's configuration has one major change to its
        parsing of .ini files that ConfigParser does not allow: options can
        be indented.  I.e.:
-8<---------
# This line would start at column 1
    option = value
-8<---------
        Would actually set 'option' to 'value'.  ConfigParser does not do
        this - instead it assumes that any indented line is a continuation of
        a previous value.

        To solve this, we simply left strip all lines in the content in the
        parse_content method before processing by the IniConfigFile method.
        This is OK, since Samba does not use indents to continue a value.
    """

    def parse_content(self, content):
        # smb.conf is special from other ini files in the property that whatever is before the first
        # section (before the first section) belongs to the [global] section. Therefore, the
        # [global] section is appended right at the beginning so that everything that would be
        # parsed as outside section belongs to [global].
        # Python 2.7 RawConfigParser automatically merges multiple instances of the same section.
        #  (And if that ever changes, test_samba.py will catch it.)
        lstripped = ["[global]"] + [line.lstrip() for line in content]

        super(SambaConfig, self).parse_content(lstripped)

        # Create a new instance of the same dict type used by the underlying RawConfigParser.
        new_dict = self.data._dict()
        # Transform the section names so that whitespace around is stripped and they are lowercase.
        # smb.conf is special in the property that section names and option names are
        # case-insensitive and treated like lower-case.
        for old_key, old_section in self.data._sections.iteritems():
            new_key = old_key.strip().lower()
            if new_key not in new_dict:
                new_dict[new_key] = self.data._dict()
            # Merge same-named sections just as samba's `testparm` does.
            new_dict[new_key].update(old_section)
        self.data._sections = new_dict
