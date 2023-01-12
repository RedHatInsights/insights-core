"""
HttpdConf - files ``/etc/httpd/conf/httpd.conf`` and ``/etc/httpd/conf.d/*``
============================================================================
"""
import string

from insights.core import ConfigParser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsr import (Char, EOF, EOL, EndTagName, Forward, FS, GT, InSet, Literal,
                            LT, Letters, Lift, LineEnd, Many, Number, OneLineComment,
                            PosMarker, QuotedString, StartTagName, String, WS, WSChar,
                            skip_none)
from insights.parsr.query import Directive, Entry, Section
from insights.specs import Specs


class DocParser(object):
    def __init__(self, ctx):
        self.ctx = ctx

        Complex = Forward()
        Comment = (WS >> OneLineComment("#")).map(lambda x: None)

        Cont = Char("\\") + EOL
        First = InSet(string.ascii_letters + "_/")
        Rest = String(string.ascii_letters + "_/" + string.digits)
        FirstRest = (First + Rest).map("".join)
        Name = (FirstRest << (Many(WSChar) + Cont)) | FirstRest

        Num = Number & (WSChar | LineEnd)

        StartName = WS >> PosMarker(StartTagName(Letters)) << WS
        EndName = WS >> EndTagName(Letters, ignore_case=True) << WS

        AttrStart = Many(WSChar)
        AttrEnd = (Many(WSChar) + Cont) | Many(WSChar)

        BareAttr = String(set(string.printable) - (set(string.whitespace) | set("<>'\"")))
        OpAttr = (Literal("!=") | Literal("<=") | Literal(">=") | InSet("<>")) & WSChar + BareAttr
        EmptyAttr = String('"\'', min_length=2)
        Attr = AttrStart >> (Num | QuotedString.map(self.remove_cont) | OpAttr | BareAttr | EmptyAttr) << AttrEnd
        Attrs = Many(Attr)

        StartTag = (WS + LT) >> (StartName + Attrs) << (GT + WS)
        EndTag = (WS + LT + FS) >> EndName << (GT + WS)

        Simple = WS >> (Lift(self.to_directive) * PosMarker(Name) * Attrs) << WS
        Stanza = Simple | Complex | Comment | Many(WSChar | EOL, lower=1).map(lambda x: None)
        Complex <= (Lift(self.to_section) * StartTag * Many(Stanza).map(skip_none)) << EndTag
        Doc = Many(Stanza).map(skip_none)

        self.Top = Doc + EOF

    def remove_cont(self, val):
        return "".join([x.strip().strip("\\") for x in val.split("\n")])

    def typed(self, val):
        try:
            v = val.lower()
            if v in ("on", "yes", "true"):
                return True
            if v in ("off", "no", "false"):
                return False
        except:
            pass
        return val

    def to_directive(self, name, attrs):
        attrs = attrs if len(attrs) > 1 else [self.typed(a) for a in attrs]
        return Directive(name=name.value, attrs=attrs, lineno=name.lineno,
                         src=self.ctx)

    def to_section(self, tag, children):
        name, attrs = tag
        attrs = attrs if len(attrs) > 1 else [self.typed(a) for a in attrs]
        return Section(name=name.value, attrs=attrs, children=children,
                       lineno=name.lineno, src=self.ctx)

    def __call__(self, content):
        try:
            return self.Top(content)
        except Exception:
            raise ParseException("There was an exception when parsing one of the httpd config files.")


class HttpdConfBase(ConfigParser):
    """
    Parse the keyword-and-value-but-also-vaguely-XML of an Apache configuration
    file.

    Generally, each line is split on the first space into key and value, leading
    and trailing space being ignored.

    Sample (edited) httpd.conf file::

        ServerRoot "/etc/httpd"
        LoadModule auth_basic_module modules/mod_auth_basic.so
        LoadModule auth_digest_module modules/mod_auth_digest.so

        <Directory />
            Options FollowSymLinks
            AllowOverride None
        </Directory>

        <IfModule mod_mime_magic.c>
        #   MIMEMagicFile /usr/share/magic.mime
            MIMEMagicFile conf/magic
        </IfModule>

        ErrorLog "|/usr/sbin/httplog -z /var/log/httpd/error_log.%Y-%m-%d"

        SSLProtocol -ALL +SSLv3
        #SSLProtocol all -SSLv2

        NSSProtocol SSLV3 TLSV1.0
        #NSSProtocol ALL

        # prefork MPM
        <IfModule prefork.c>
        StartServers       8
        MinSpareServers    5
        MaxSpareServers   20
        ServerLimit      256
        MaxClients       256
        MaxRequestsPerChild  200
        </IfModule>

        # worker MPM
        <IfModule worker.c>
        StartServers         4
        MaxClients         300
        MinSpareThreads     25
        MaxSpareThreads     75
        ThreadsPerChild     25
        MaxRequestsPerChild  0
        </IfModule>

    Examples:

        >>> httpd_conf['ServerRoot'][-1].value
        '/etc/httpd'
        >>> httpd_conf['LoadModule'][0].value
        'auth_basic_module modules/mod_auth_basic.so'
        >>> httpd_conf['LoadModule'][-1].value
        'auth_digest_module modules/mod_auth_digest.so'
        >>> httpd_conf['Directory', '/']['Options'][-1].value
        'FollowSymLinks'
        >>> type(httpd_conf[('IfModule','prefork.c')]) == type({})
        False
        >>> httpd_conf[('IfModule','prefork.c')]['StartServers'][0].value
        8
        >>> 'ThreadsPerChild' in httpd_conf[('IfModule','prefork.c')]
        False
        >>> httpd_conf[('IfModule','worker.c')]['MaxRequestsPerChild'][-1].value
        0
    """
    def __init__(self, *args, **kwargs):
        self.parse = DocParser(self)
        super(HttpdConfBase, self).__init__(*args, **kwargs)

    def parse_doc(self, content):
        if isinstance(content, list):
            content = "\n".join(content)
        result = self.parse(content)[0]
        return Entry(children=result, src=self)


@parser(Specs.httpd_conf)
class HttpdConf(HttpdConfBase):
    pass


@parser(Specs.httpd_conf_scl_httpd24)
class HttpdConfSclHttpd24(HttpdConfBase):
    pass


@parser(Specs.httpd_conf_scl_jbcs_httpd24)
class HttpdConfSclJbcsHttpd24(HttpdConfBase):
    pass
