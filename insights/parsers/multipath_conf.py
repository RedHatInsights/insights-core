"""
multipath.conf file content
===========================

The base class is the MultipathConfParser class, which reads the multipath
daemon's ``/etc/multipath.conf`` configuration file.
This is in a pseudo-JSON format.

MultipathConf - file ``/etc/multipath.conf``
--------------------------------------------

MultipathConfInitramfs - command ``lsinitrd -f /etc/multipath.conf``
--------------------------------------------------------------------

MultipathConfTree - file ``/etc/multipath.conf``
------------------------------------------------

MultipathConfTreeInitramfs - command ``lsinitrd -f /etc/multipath.conf``
------------------------------------------------------------------------
"""
import string

from insights.contrib import pyparsing as p
from insights.core import ConfigParser, CommandParser, LegacyItemAccess, Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsr import (EOF, Forward, LeftCurly, Lift, LineEnd, Literal,
                            Many, Number, OneLineComment, PosMarker, QuotedString,
                            RightCurly, String, WS, WSChar, skip_none)
from insights.parsr.query import Entry
from insights.specs import Specs
from insights.util import deprecated


class MultipathConfParser(Parser, LegacyItemAccess):
    """
    .. warning::
        This class is deprecated, please use function
        `insights.parsers.multipath_conf.parse_doc` instead.

    Shared parser for the file ``/etc/multipath.conf`` and output of
    ``lsinitrd -f /etc/multipath.conf`` applied to
    /boot/initramfs-<kernel-version>.img.

    Return a dict where the keys are the name of sections in multipath
    configuraion file.  If there are subsections, the value is a list of
    dictionaries with parameters as key and value.  Otherwise the value is
    just a single dictionary.

    Configuration File Example::

        defaults {
               path_selector           "round-robin 0"
               user_friendly_names      yes
        }

        multipaths {
               multipath {
                       alias                   yellow
                       path_grouping_policy    multibus
              }
               multipath {
                       wwid                    1DEC_____321816758474
                       alias                   red
              }
        }

        devices {
               device {
                       path_selector           "round-robin 0"
                       no_path_retry            queue
              }
               device {
                       vendor                  1DEC_____321816758474
                       path_grouping_policy    red
              }
        }

        blacklist {
              wwid 26353900f02796769
              devnode "^hd[a-z]"
        }

    Parse Result::

        data = {
          "blacklist": {
            "devnode": "^hd[a-z]",
            "wwid": "26353900f02796769"
          },
          "devices": [
            {
              "path_selector": "round-robin 0",
              "no_path_retry": "queue"
            },
            {
              "path_grouping_policy": "red",
              "vendor": "1DEC_____321816758474"
            }
          ],
          "defaults": {
            "path_selector": "round-robin 0",
            "user_friendly_names": "yes"
          },
          "multipaths": [
            {
              "alias": "yellow",
              "path_grouping_policy": "multibus"
            },
            {
              "alias": "red",
              "wwid": "1DEC_____321816758474"
            }
          ]
        }
    """

    def __init__(self, *args, **kwargs):
        deprecated(MultipathConfParser, "Please use the :function:`insights.parsers.multipath_conf.parse_doc instead.", "3.3.0")
        super(MultipathConfParser, self).__init__(*args, **kwargs)

    @classmethod
    def _create_parser(cls):
        """
        Need to check the specific symbol "/" in attr_value part as well.
        I checked some multipath configuraion files from the sosreport and got
        although there are some more specific symbols like "-%", it is enclosed
        in double quotes and will be accepted. Furthermore, I also checked the
        source code of "device-mapper-multipath" and got if the attr_value in
        "multipath.conf" include a "whitespace", it must be enclosed in double
        quotation marks. So, we could just add one more specific symbol "/" to
        check.
        ----------------------------------------------------------
        udev_dir                /dev
        getuid_callout          "/sbin/scsi_id -g -u -s /block/%n"
        ----------------------------------------------------------
        """
        section_name = p.Word(p.alphas + "_")
        attr_name = attr_value = p.Word(p.alphanums + "_/")
        LBRACE, RBRACE = map(p.Suppress, "{}")
        attr = p.Group(attr_name + (attr_value | p.quotedString.setParseAction(p.removeQuotes)))
        attr_list = p.Dict(p.ZeroOrMore(attr))
        simple_section = p.Group(section_name + LBRACE + attr_list + RBRACE)
        complex_section = p.Group(section_name + LBRACE + p.OneOrMore(simple_section) + RBRACE)
        simple_or_complex = p.Dict(simple_section | complex_section)
        my_conf = p.Group(p.ZeroOrMore(simple_or_complex))
        my_conf.ignore("#" + p.restOfLine)
        return my_conf

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty content.")
        self.data = MultipathConfParser._create_parser().parseString("\n".join(content))[0].asDict()


@parser(Specs.multipath_conf)
class MultipathConf(MultipathConfParser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.multipath_conf.MultipathConfTree` instead.

    Parser for the file ``/etc/multipath.conf``.

    Examples:
        >>> conf = shared[MultipathConf]
        >>> conf.data['blacklist']['devnode']  # Access via data property
        '^hd[a-z]'
        >>> conf['defaults']['user_friendly_names']  # Pseudo-dict access
        'yes'
        >>> len(conf['multipaths'])
        2
        >>> conf['multipaths'][0]['alias']
        'yellow'
    """

    def __init__(self, *args, **kwargs):
        deprecated(MultipathConf, "Import MultipathConfTree from insights.parsers.multipath_conf instead.", "3.3.0")
        super(MultipathConf, self).__init__(*args, **kwargs)


@parser(Specs.multipath_conf_initramfs)
class MultipathConfInitramfs(MultipathConfParser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.multipath_conf.MultipathConfTreeInitramfs` instead.

    Parser for the output of ``lsinitrd -f /etc/multipath.conf`` applied to
    /boot/initramfs-<kernel-version>.img.

    Examples:
        >>> conf = shared[MultipathConfInitramfs]
        >>> conf.data['blacklist']['devnode']  # Access via data property
        '^hd[a-z]'
        >>> conf['defaults']['user_friendly_names']  # Pseudo-dict access
        'yes'
        >>> len(conf['multipaths'])
        2
        >>> conf['multipaths'][0]['alias']
        'yellow'
    """

    def __init__(self, *args, **kwargs):
        deprecated(MultipathConfInitramfs, "Import MultipathConfTreeInitramfs from insights.parsers.multipath_conf instead.", "3.3.0")
        super(MultipathConfInitramfs, self).__init__(*args, **kwargs)


def parse_doc(content, ctx):
    def to_entry(name, rest):
        if isinstance(rest, list):
            return Entry(name=name.value, children=rest, lineno=name.lineno, src=ctx)
        return Entry(name=name.value, attrs=[rest], lineno=name.lineno, src=ctx)

    Stmt = Forward()
    Num = Number & (WSChar | LineEnd)
    NULL = Literal("none", value=None)
    Comment = (WS >> OneLineComment("#").map(lambda x: None))
    BeginBlock = (WS >> LeftCurly << WS)
    EndBlock = (WS >> RightCurly << WS)
    Bare = String(set(string.printable) - (set(string.whitespace) | set("#{}'\"")))
    Name = WS >> PosMarker(String(string.ascii_letters + "_")) << WS
    Value = WS >> (Num | NULL | QuotedString | Bare) << WS
    EmptyString = String('"\'', min_length=2)
    Value = WS >> (Num | NULL | QuotedString | EmptyString | Bare) << WS
    Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
    Stanza = (Lift(to_entry) * Name * (Block | Value)) | Comment
    Stmt <= WS >> Stanza << WS
    Doc = Many(Stmt).map(skip_none)
    Top = Doc + EOF

    return Entry(children=Top(content)[0])


@parser(Specs.multipath_conf)
class MultipathConfTree(ConfigParser):
    """
    Exposes multipath configuration through the parsr query interface.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)


def get_tree(root=None):
    """
    This is a helper function to get a multipath configuration component for
    your local machine or an archive. It's for use in interactive sessions.
    """
    from insights import run
    return run(MultipathConfTree, root=root).get(MultipathConfTree)


@parser(Specs.multipath_conf_initramfs)
class MultipathConfTreeInitramfs(ConfigParser, CommandParser):
    """
    Exposes the multipath configuration from initramfs image through the
    parsr query interface.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """

    bad_lines = [
        'no <initramfs file> specified and the default image'
    ]

    def __init__(self, context):
        super(MultipathConfTreeInitramfs, self).__init__(
                context, extra_bad_lines=self.bad_lines)

    def parse_doc(self, content):
        return parse_doc("\n".join(content), ctx=self)


def get_tree_from_initramfs(root=None):
    """
    This is a helper function to get a multipath configuration(from initramfs
    image) component for your local machine or an archive. It's for use in
    interactive sessions.
    """
    from insights import run
    return run(MultipathConfTreeInitramfs, root=root).get(MultipathConfTreeInitramfs)
