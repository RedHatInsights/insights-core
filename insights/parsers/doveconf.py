"""
Doveconf - command ``doveconf``
===============================
"""
import string

from insights import parser, add_filter
from insights.combiners.nginx_conf import EmptyQuotedString
from insights.core import ConfigParser
from insights.parsr import (EOF, InSet,
                            Lift, Many, OneLineComment, PosMarker,
                            QuotedString, skip_none, String, WS, WSChar, LeftCurly, RightCurly, Forward,
                            EOL)
from insights.parsr.query import Directive, Entry, Section
from insights.specs import Specs

add_filter(Specs.doveconf, [
    "{",
    "}"
])


@parser(Specs.doveconf, continue_on_error=False)
class Doveconf(ConfigParser):
    """
    Class for parsing the ``doveconf`` command.
    Sample input::

        # 2.2.36 (1f10bfa63): /etc/dovecot/dovecot.conf
        auth_anonymous_username = anonymous
        auth_cache_negative_ttl = 1 hours
        auth_policy_request_attributes = login=%{requested_username} pwhash=%{hashed_password} remote=%{rip} device_id=%{client_id} protocol=%s
        auth_policy_server_api_header =
        log_timestamp = "%b %d %H:%M:%S "
        login_access_sockets =
        namespace inbox {
          disabled = no
          location =
          mailbox Drafts {
            auto = no
            driver =
            special_use = \Drafts
          }
          mailbox Junk {
            auto = no
          }
          order = 0
          prefix =
          subscriptions = yes
        }
        passdb {
          args =
          auth_verbose = default
        }
        service aggregator {
          chroot = .
          client_limit = 0
          fifo_listener replication-notify-fifo {
            group =
            mode = 0600
          }
          group =
          unix_listener replication-notify {
            mode = 0600
          }
          user = $default_internal_user
          vsz_limit = 18446744073709551615 B
        }
        valid_chroot_dirs =
        verbose_proctitle = no

    Example:
        >>> doveconf['auth_anonymous_username'].value
        'anonymous'
        >>> doveconf['auth_cache_negative_ttl'].value
        '1 hours'
        >>> doveconf['auth_cache_size'].value
        '0'
        >>> doveconf['auth_policy_request_attributes'].value
        'login=%{requested_username} pwhash=%{hashed_password} remote=%{rip} device_id=%{client_id} protocol=%s'
        >>> doveconf['log_timestamp'].value
        '"%b %d %H:%M:%S "'
        >>> doveconf['namespace'][0].value
        'inbox'
        >>> doveconf['namespace'][0]["mailbox"][1].value
        'Junk'
    """
    def _parse_doc(self):

        def to_directive(name, attrs):
            return Directive(name=name.value, attrs=attrs, lineno=name.lineno, src=self)

        def to_directive_noval(name, sep):
            return Directive(name=name.value, attrs=[], lineno=name.lineno, src=self)

        def to_section(name, attrs, body):
            return Section(name=name.value, attrs=attrs, children=body, lineno=name.lineno, src=self)

        sep_chars = set("=")
        Sep = InSet(sep_chars, "Sep")

        name_chars = string.ascii_letters + "_/"
        Name = Many(WSChar) >> PosMarker(String(name_chars) | EmptyQuotedString(name_chars)) << Many(WSChar)

        BareStringDir = String(set(string.printable) - set("\r\n"))
        BareStringBlk = String(set(string.printable) - (set(string.whitespace) | set("{}'\"")))
        BlockBeg = Many(WSChar) >> LeftCurly << WS
        BlockEnd = Many(WSChar) >> RightCurly << (EOL | EOF)

        Comment = OneLineComment("#").map(lambda x: None) << (EOL | EOF)

        Stmt = Forward()

        _AttrDir = Many(WSChar) >> (BareStringDir | QuotedString)
        AttrDir = Sep >> Many(_AttrDir)
        AttrDirNoVal = Sep << Many(WSChar)
        Dir = (Lift(to_directive) * Name * AttrDir) << (EOL | EOF)
        DirNoVal = (Lift(to_directive_noval) * Name * AttrDirNoVal) << (EOL | EOF)

        _AttrBlk = Many(WSChar) >> (BareStringBlk | QuotedString)
        AttrsBlk = Many(_AttrBlk)
        BlockBody = BlockBeg >> Many(Stmt).map(skip_none) << BlockEnd
        Block = (Lift(to_section) * Name * AttrsBlk * BlockBody)

        Stmt <= WS >> (Block | Dir | DirNoVal | Comment) << WS

        Doc = Many(Stmt).map(skip_none)
        Top = Doc + EOF

        return Top

    def __init__(self, *args, **kwargs):
        self.Top = self._parse_doc()
        super(Doveconf, self).__init__(*args, **kwargs)

    def parse_doc(self, content):
        return Entry(children=self.Top("\n".join(content))[0], src=self)
