"""
TODO
TODO Add rhel7 SCL files - rh-php73-php, rh-php72-php
PHPConfe - file ``/etc/php.ini``
=======================================================

TODO
This module models nginx configuration as a tree. It correctly handles include
directives by splicing individual document trees into their parents until one
document tree is left.

TODO
A DSL is provided to query the tree through a select function or brackets [].
The brackets allow a more conventional lookup feel but aren't quite as powerful
as using select directly.
"""
import os
import string
from insights import combiner, parser, run
from insights.core import ConfigCombiner, ConfigParser
from insights.parsr.query import eq
from insights.parsr import (Char, EOF, Forward, LeftCurly, Lift, LineEnd,
        RightCurly, Many, Number, OneLineComment, Parser, PosMarker, SemiColon,
        QuotedString, skip_none, String, WS, WSChar)
from insights.parsr.query import Directive, Entry, Section
from insights.parsers import ParseException, SkipException
from insights.specs import Specs


# TODO php_ini - filterable to elimnate collected PII?

# TODO - parsing On/Off values - as True/False - UNIT test
# TODO - parsing multiple values - as True/False - UNIT test
# TODO - parsing values like: "memory_limit = 128M"
#        - solve in parser or just in a rule?
#        - any parser e.g. httpdConfTree already doing this?
#        - add UNIT test

import string

from insights.parsr import (EOF, HangingString, InSet, LeftBracket, Lift,
                            LineEnd, Literal, Many, OneLineComment, Opt, PosMarker, RightBracket,
                            skip_none, String, WithIndent, WS, WSChar)
from insights.parsr.query import Directive, Entry, eq, Section




@parser(Specs.php_ini, continue_on_error=False)
class PHPConf(ConfigParser):
    """
    Class for php configuration file.

    Typical content of ``/etc/php.ini`` file is::

        [PHP]
        engine = On
        short_open_tag = Off
        precision = 14
        output_buffering = 4096
        zlib.output_compression = Off
        implicit_flush = Off
        unserialize_callback_func =
        serialize_precision = -1
        disable_functions =
        disable_classes =
        zend.enable_gc = On
        zend.exception_ignore_args = On
        zend.exception_string_param_max_len = 0
        expose_php = On
        max_execution_time = 30
        max_input_time = 60
        memory_limit = 128M
        error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT
        default_mimetype = "text/html"

    Example:
        >>> php_conf["PHP"]["default_mimetype"]
        'text/html'
        >>> php_conf["PHP"]["max_execution_time"]
         30
        # TODO implement
        >>> php_conf["PHP"]["engine"]  # 'On' turns to 'True'
        True
        # TODO implement
        >>> php_conf["PHP"]["short_opeh_tag"]  # 'Off' turns to 'False'
        False
        # TODO implement
        >>> php_conf.get("PHP").get("memory_limit")
        '128M'
        >>> php_conf["PHP"]["error_reporting"].endswith("E_STRICT")
        True
        # TODO implement handling lists in php.ini - item separator?
        >>> len(php_conf["PHP"]["error_reporting"])
        3
        >>> php_conf["PHP"]["error_reporting"]
        ['E_ALL', '~E_DEPRECATED', '~E_STRICT']
    """


    def parse_doc(self, content):
        try:
            def to_directive(x):
                name, rest = x
                rest = [rest] if rest is not None else []
                return Directive(name=name.value.strip(), attrs=rest, lineno=name.lineno, src=self)

            def to_section(name, rest):
                return Section(name=name.value.strip(), children=rest, lineno=name.lineno, src=self)

            def apply_defaults(cfg):
                if "DEFAULT" not in cfg:
                    return cfg

                defaults = cfg["DEFAULT"]
                not_defaults = cfg[~eq("DEFAULT")]
                for c in not_defaults:
                    for d in defaults.grandchildren:
                        if d.name not in c:
                            c.children.append(d)

                cfg.children = list(not_defaults)
                return cfg

            content = "\n".join(content)

            header_chars = (set(string.printable) - set(string.whitespace) - set("[]")) | set(" ")
            sep_chars = set("=:")
            key_chars = header_chars - sep_chars
            value_chars = set(string.printable) - set("\n\r")

            Yes = Literal("yes", True, ignore_case=True)
            No = Literal("no", False, ignore_case=True)
            Tru = Literal("true", True, ignore_case=True)
            Fals = Literal("false", False, ignore_case=True)
            Boolean = ((Yes | No | Tru | Fals) & (WSChar | LineEnd)) % "Boolean"

            LeftEnd = (WS + LeftBracket + WS)
            RightEnd = (WS + RightBracket + WS)
            Header = (LeftEnd >> PosMarker(String(header_chars)) << RightEnd) % "Header"
            Key = WS >> PosMarker(String(key_chars)) << WS
            Sep = InSet(sep_chars, "Sep")
            Value = WS >> (Boolean | HangingString(value_chars))
            KVPair = WithIndent(Key + Opt(Sep >> Value)) % "KVPair"
            Comment = (WS >> (OneLineComment("#") | OneLineComment(";")).map(lambda x: None))

            Line = Comment | KVPair.map(to_directive)
            Sect = Lift(to_section) * Header * Many(Line).map(skip_none)
            Doc = Many(Comment | Sect).map(skip_none)
            Top = Doc << WS << EOF

            res = Entry(children=Top(content), src=self)
            return apply_defaults(res)

        except SkipException:
            raise
        except:
            raise ParseException(ParseException("Could not parse content: '{0}'".
                                                format(content)))

    def parse_content(self, content):
        super(PHPConf, self).parse_content(content)
        dict_all = {}
        for section in self.doc:
            section_dict = {}
            option_names = set(o.name for o in section)
            for name in option_names:
                options = [str(o.value) for o in section[name]]
                section_dict[name] = options[0] if len(options) == 1 else options
            dict_all[section.name] = section_dict
        self.data = dict_all
