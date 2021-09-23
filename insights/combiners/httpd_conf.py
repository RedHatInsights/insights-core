"""
Combiner for httpd configurations
=================================

Combiner for parsing part of httpd configurations. It collects all HttpdConf
generated from each configuration file and combines them to expose a
consolidated configuration tree.

.. note::
    At this point in time, you should **NOT** filter the httpd configurations
    to avoid finding directives in incorrect sections.
"""
import six
import string
from insights.contrib.ipaddress import ip_address, ip_network
from collections import namedtuple

from insights import run
from insights.core import ConfigCombiner, ConfigParser
from insights.core.plugins import combiner, parser
from insights.parsr.query import (Directive, Entry, pred, pred2, Section,
        startswith)
from insights.parsr import (Char, EOF, EOL, EndTagName, Forward, FS, GT, InSet,
        Literal, LT, Letters, Lift, LineEnd, Many, Number, OneLineComment,
        PosMarker, QuotedString, skip_none, StartTagName, String, WS, WSChar)
from insights.parsers.httpd_conf import HttpdConf, dict_deep_merge, ParsedData
from insights.specs import Specs
from insights.util import deprecated


@combiner(HttpdConf)
class HttpdConfAll(object):
    """
    .. warning::
        This combiner class is deprecated, please use
        :py:class:`insights.combiners.httpd_conf.HttpdConfTree` instead.

    A combiner for parsing all httpd configurations. It parses all sources and makes a composition
    to store actual loaded values of the settings as well as information about parsed configuration
    files and raw values.

    Note:
        ``ParsedData`` is a named tuple with the following properties:
            - ``value`` - the value of the option.
            - ``line`` - the complete line as found in the config file.
            - ``section`` - the section type that the option belongs to.
            - ``section_name`` - the section name that the option belongs to.
            - ``file_name`` - the config file name.
            - ``file_path`` - the complete config file path.

        ``ConfigData`` is a named tuple with the following properties:
            - ``file_name`` - the config file name.
            - ``file_path`` - the complete config file path.
            - ``data_dict`` - original data dictionary from parser.

    Attributes:
        data (dict): Dictionary of parsed settings in format {option: [ParsedData, ParsedData]}.
                     It stores a list of parsed values, usually only the last value is needed,
                     except situations when directives which can use selective overriding,
                     such as ``UserDir``, are used.
        config_data (list): List of parsed config files in containing ConfigData named tuples.
    """
    ConfigData = namedtuple('ConfigData', ['file_name', 'file_path', 'full_data_dict'])

    def __init__(self, httpd_conf):
        deprecated(HttpdConfAll, "Import HttpdConfTree from 'insights.combiners.httpd_conf' instead.")

        self.data = {}
        self.config_data = []

        config_files_data = []
        main_config_data = []

        for httpd_parser in httpd_conf:
            file_name = httpd_parser.file_name
            file_path = httpd_parser.file_path

            # Flag to be used for different handling of the main config file
            main_config = httpd_parser.file_name == 'httpd.conf'

            if not main_config:
                config_files_data.append(self.ConfigData(file_name, file_path,
                                                         httpd_parser.data))
            else:
                main_config_data.append(self.ConfigData(file_name, file_path,
                                                        httpd_parser.first_half))
                main_config_data.append(self.ConfigData(file_name, file_path,
                                                        httpd_parser.second_half))

        # Sort configuration files
        config_files_data.sort()

        # Add both parts of main configuration file and store as attribute.
        # These values can be used when looking for bad settings which are not actually active
        # but may become active if other configurations are changed
        if main_config_data:
            self.config_data = [main_config_data[0]] + config_files_data + [main_config_data[1]]
        else:
            self.config_data = config_files_data

        # Store active settings - the last parsed value us stored
        self.data = {}
        for _, _, full_data in self.config_data:
            copy_data = full_data.copy()
            for option, parsed_data in copy_data.items():
                if isinstance(parsed_data, dict):
                    if option not in self.data:
                        self.data[option] = {}
                    dict_deep_merge(self.data[option], parsed_data)
                else:
                    if option not in self.data:
                        self.data[option] = []
                    self.data[option].extend(parsed_data)

    def get_setting_list(self, directive, section=None):
        """
        Returns the parsed data of the specified directive as a list

        Parameters:
            directive (str): The directive to look for
            section (str or tuple): The section the directive belongs to

                    - str: The section type, e.g. "IfModule"
                    - tuple(section, section_name): e.g. ("IfModule", "prefork")

                    Note::
                        `section_name` can be ignored or can be a part of the actual name.

        Returns:
            (list of dict or named tuple `ParsedData`):
                When `section` is not None, returns the list of dict that wraps
                the section and the directive's named tuples ParsedData, in
                order how they are parsed.

                When `section` is None, returns the list of named tuples
                ParsedData, in order how they are parsed.

                If directive or section does not exist, returns empty list.
        """
        def _deep_search(data, dr, sc):
            """
            Utility function to get search the directive `dr` in the nested
            dict

            Parameters:
                data (dict): The target dictionary
                dr (str): The directive to look for
                sc (tuple): The section the directive belongs to

            Returns:
                (list of dict): List of dict that wraps the section and the
                    directive's named tuples ParsedData in order how they are parsed.
            """
            result = []
            for d, v in data.items():
                if isinstance(d, tuple):
                    if d[0] == sc[0] and sc[1] in d[1]:
                        val = v.get(dr)
                        if val:
                            result.append({d: val})
                    result.extend(_deep_search(v, dr, sc))
            return result

        if section:
            if isinstance(section, str):
                section = (section, '')
            elif isinstance(section, tuple) and len(section) == 1:
                section = (section[0], '')
            elif (not isinstance(section, tuple) or (len(section) == 0 or len(section) > 2)):
                return []
            return _deep_search(self.data, directive, section)

        return self.data.get(directive, [])

    def get_active_setting(self, directive, section=None):
        """
        Returns the parsed data of the specified directive as a list of named tuples.

        Parameters:
            directive (str): The directive to look for
            section (str or tuple): The section the directive belongs to

                    - str: The section type, e.g. "IfModule"
                    - tuple(section, section_name): e.g. ("IfModule", "prefork")

                    Note::
                        `section_name` can be ignored or can be a part of the actual name.

        Returns:
            (list or named tuple `ParsedData`):
                When `section` is not None, returns the list of named tuples
                ParsedData, in order how they are parsed.
                If directive or section does not exist, returns empty list.

                When `section` is None, returns the named tuple ParsedData of
                the directive directly.
                If directive or section does not exist, returns None.

        """
        values_list = self.get_setting_list(directive, section)
        if section is not None:
            if values_list:
                for i, val in enumerate(values_list):
                    # From each section, preserve only the last ParsedData
                    # {(section, ""): [ParsedData, ParsedData]} ---> ParsedData
                    values_list[i] = list(val.values())[0][-1]
                return values_list
            return []
        else:
            if values_list:
                return values_list[-1]

    def get_section_list(self, section):
        """
        Returns the specified sections.

        Parameters:
            section (str): The section to look for, e.g. "Directory"

        Returns:
            (list of tuple): List of tuples, each tuple has three elements - the
            first being a tuple of the section and section name, the second
            being the file name of the file where that section resides,
            the third being the full file path of the file. Therefore, the result
            looks like this: [(('VirtualHost', '192.0.2.1'), '00-z.conf',
            '/etc/httpd/conf.d/00-z.conf')]

            If section does not exist, returns empty list.
        """
        def _deep_search(data, sc):
            """
            Utility function to search for sections in the nested dict

            Parameters:
                data (dict): The target dictionary
                sc (str): The section the directive belongs to

            Returns:
                (list of tuple): List of tuples, each tuple has three elements - the
                first being a tuple of the section and section name, the second
                being the file name of the file where that section resides,
                the third being the full file path of the file. Therefore, the result
                looks like this: [(('VirtualHost', '192.0.2.1'), '00-z.conf',
                '/etc/httpd/conf.d/00-z.conf')]
            """
            result = []
            for d, v in data.items():
                if isinstance(d, tuple):
                    if d[0] == sc:
                        # file of the section
                        sect_file_name = None
                        sect_file_path = None
                        for subkey, subvalue in v.items():
                            if subvalue and isinstance(subkey, str) and isinstance(subvalue, list) and isinstance(subvalue[0], ParsedData):
                                # it is a directive, not a section, there's at least one ParsedData
                                sect_file_name = subvalue[0].file_name
                                sect_file_path = subvalue[0].file_path
                                # assuming all directives in this section come from the same file
                                break
                        result.append((d, sect_file_name, sect_file_path))
                    else:
                        result.extend(_deep_search(v, sc))
            return result

        if section:
            return _deep_search(self.data, section)

        return []


class DocParser(object):
    def __init__(self, ctx):
        self.ctx = ctx

        Complex = Forward()
        Comment = (WS >> OneLineComment("#")).map(lambda x: None)

        First = InSet(string.ascii_letters + "_/")
        Rest = String(string.ascii_letters + "_/" + string.digits)
        Name = (First + Rest).map("".join)

        Num = Number & (WSChar | LineEnd)

        StartName = WS >> PosMarker(StartTagName(Letters)) << WS
        EndName = WS >> EndTagName(Letters, ignore_case=True) << WS

        Cont = Char("\\") + EOL
        AttrStart = Many(WSChar)
        AttrEnd = (Many(WSChar) + Cont) | Many(WSChar)

        OpAttr = (Literal("!=") | Literal("<=") | Literal(">=") | InSet("<>")) & WSChar
        BareAttr = String(set(string.printable) - (set(string.whitespace) | set("<>'\"")))
        EmptyAttr = String('"\'', min_length=2)
        Attr = AttrStart >> (Num | QuotedString | OpAttr | BareAttr | EmptyAttr) << AttrEnd
        Attrs = Many(Attr)

        StartTag = (WS + LT) >> (StartName + Attrs) << (GT + WS)
        EndTag = (WS + LT + FS) >> EndName << (GT + WS)

        Simple = WS >> (Lift(self.to_directive) * PosMarker(Name) * Attrs) << WS
        Stanza = Simple | Complex | Comment | Many(WSChar | EOL, lower=1).map(lambda x: None)
        Complex <= (Lift(self.to_section) * StartTag * Many(Stanza).map(skip_none)) << EndTag
        Doc = Many(Stanza).map(skip_none)

        self.Top = Doc + EOF

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
        except:
            raise


def parse_doc(content, ctx=None):
    """ Parse a configuration document into a tree that can be queried. """
    if isinstance(content, list):
        content = "\n".join(content)
    parse = DocParser(ctx)
    result = parse(content)[0]
    return Entry(children=result, src=ctx)


@parser(Specs.httpd_conf, continue_on_error=False)
class _HttpdConf(ConfigParser):
    """ Parser for individual httpd configuration files. """
    def __init__(self, *args, **kwargs):
        self.parse = DocParser(self)
        super(_HttpdConf, self).__init__(*args, **kwargs)

    def parse_doc(self, content):
        if isinstance(content, list):
            content = "\n".join(content)
        result = self.parse(content)[0]
        return Entry(children=result, src=self)


@combiner(_HttpdConf)
class HttpdConfTree(ConfigCombiner):
    """
    Exposes httpd configuration through the parsr query interface. Correctly
    handles all include directives.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, confs):
        includes = startswith("Include")
        super(HttpdConfTree, self).__init__(confs, "httpd.conf", includes)

    @property
    def conf_path(self):
        res = self.main.find("ServerRoot")
        return res.value if res else "/etc/httpd"


@parser(Specs.httpd_conf_scl_httpd24, continue_on_error=False)
class _HttpdConfSclHttpd24(ConfigParser):
    """ Parser for individual httpd configuration files. """
    def parse_doc(self, content):
        return parse_doc(content, ctx=self)


@combiner(_HttpdConfSclHttpd24)
class HttpdConfSclHttpd24Tree(ConfigCombiner):
    """
    Exposes httpd configuration Software Collection httpd24 through the parsr query
    interface. Correctly handles all include directives.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, confs):
        includes = startswith("Include")
        super(HttpdConfSclHttpd24Tree, self).__init__(confs, "httpd.conf", includes)

    @property
    def conf_path(self):
        res = self.main.find("ServerRoot")
        return res.value if res else "/opt/rh/httpd24/root/etc/httpd"


@parser(Specs.httpd_conf_scl_jbcs_httpd24, continue_on_error=False)
class _HttpdConfSclJbcsHttpd24(ConfigParser):
    """ Parser for individual httpd configuration files. """
    def parse_doc(self, content):
        return parse_doc(content, ctx=self)


@combiner(_HttpdConfSclJbcsHttpd24)
class HttpdConfSclJbcsHttpd24Tree(ConfigCombiner):
    """
    Exposes httpd configuration Software Collection jbcs-httpd24 through the parsr query
    interface. Correctly handles all include directives.

    See the :py:class:`insights.core.ConfigComponent` class for example usage.
    """
    def __init__(self, confs):
        includes = startswith("Include")
        super(HttpdConfSclJbcsHttpd24Tree, self).__init__(confs, "httpd.conf", includes)

    @property
    def conf_path(self):
        res = self.main.find("ServerRoot")
        return res.value if res else "/opt/rh/jbcs-httpd24/root/etc/httpd"


def get_tree(root=None):
    """
    This is a helper function to get an httpd configuration component for your
    local machine or an archive. Use it in interactive sessions.
    """
    return run(HttpdConfTree, root=root).get(HttpdConfTree)


is_private = pred(lambda x: ip_address(six.u(x)).is_private)
"""
Predicate to check if an ip address is private.

Example:
    conf["VirtualHost", in_network("128.39.0.0/16")]
"""

in_network = pred2(lambda x, y: (ip_address(six.u(x)) in ip_network(six.u(y))))
"""
Predicate to check if an ip address is in a given network.

Example:
    conf["VirtualHost", in_network("128.39.0.0/16")]
"""


if __name__ == "__main__":
    run(HttpdConfTree, print_summary=True)
