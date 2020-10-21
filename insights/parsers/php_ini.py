"""
php_ini - file ``/etc/php.ini``
===============================

This module provides the ``PHPConfig`` class parser, for reading the
options in the ``/etc/php.ini`` file.

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

The class has one attribute ``data`` which is a nested ``dict`` representing sections
of the input INI file. Each section is represented as ``dict`` where keys are name
of options and values are values of those options.

Example:
    >>> php_conf["PHP"]["default_mimetype"].value
    'text/html'
    >>> php_config.data['PHP']['default_mimetype']
    'text/html'
    >>> php_conf.data['Session']['session.cache_limiter']
    'nocache'
    >>> php_conf["PHP"]["max_execution_time"].value
     30
    >>> php_conf["PHP"]["engine"].value  # 'On' turns to 'True'
    True
    >>> php_conf["PHP"]["short_opeh_tag"].value  # 'Off' turns to 'False'
    False
    >>> php_c['PHP']['precision'].value
    14
    >>> php_conf.get("PHP").get("memory_limit")  # '128M' is converted into bytes
    134217728
"""
import string
from insights import parser
from insights.core import ConfigParser
from insights.core.filters import add_filter
from insights.parsr.query import eq
from insights.parsr import (Char, EOF, HangingString, InSet,
        LeftBracket, Lift, LineEnd, Literal, RightBracket,
        Many, Number, OneLineComment, Opt, PosMarker,
        QuotedString, skip_none, String, WithIndent, WS, WSChar)
from insights.parsr.query import Directive, Entry, Section
from insights.parsers import ParseException, SkipException
from insights.specs import Specs


# Filter to ensure that the section headings will always be included.
add_filter(Specs.php_ini, "[")


@parser(Specs.php_ini, continue_on_error=False)
class PHPConf(ConfigParser):
    """
    Class for php configuration file.
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

            def make_bytes(number, char_multiple):
                if char_multiple.lower() == 'k':
                    return number * 2**10
                if char_multiple.lower() == 'm':
                    return number * 2**20
                if char_multiple.lower() == 'g':
                    return number * 2**30

            content = "\n".join(content)

            header_chars = (set(string.printable) - set(string.whitespace) - set("[]")) | set(" ")
            sep_chars = set("=")
            key_chars = header_chars - sep_chars
            value_chars = set(string.printable) - set("\n\r")

            On = Literal("on", True, ignore_case=True)
            Off = Literal("off", False, ignore_case=True)
            Tru = Literal("true", True, ignore_case=True)
            Fals = Literal("false", False, ignore_case=True)
            Boolean = ((On | Off | Tru | Fals) & (WSChar | LineEnd)) % "Boolean"
            Num = Number & (WSChar | LineEnd)
            QuoStr = QuotedString & (WSChar | LineEnd)
            # Handle php.ini shorthand notation for memory limits: 1G, 8M, 50K
            # https://www.php.net/manual/en/faq.using.php#faq.using.shorthandbytes
            MemNum = (Lift(make_bytes) * Number * (Char('K') | Char('M') | Char('G'))) & (WSChar | LineEnd)

            LeftEnd = (WS + LeftBracket + WS)
            RightEnd = (WS + RightBracket + WS)
            Header = (LeftEnd >> PosMarker(String(header_chars)) << RightEnd) % "Header"
            Key = WS >> PosMarker(String(key_chars)) << WS
            Sep = InSet(sep_chars, "Sep")
            Value = WS >> (Boolean | MemNum | Num | QuoStr | HangingString(value_chars))
            KVPair = WithIndent(Key + Opt(Sep >> Value)) % "KVPair"
            Comment = (WS >> (OneLineComment(";")).map(lambda x: None))

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
