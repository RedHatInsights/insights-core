from .. import IniConfigFile, mapper


@mapper("samba", filters=["["])
class SambaConfig(IniConfigFile):
    """
        smb.conf file mapper.

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
        lstripped = [line.lstrip() for line in content]
        return super(SambaConfig, self).parse_content(lstripped)
