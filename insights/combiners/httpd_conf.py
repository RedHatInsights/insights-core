"""
Combiner for httpd configurations
=================================

Combiner for parsing part of httpd configurations. It collects all HttpdConf
generated from each configuration file and combines them to expose a
consolidated configuration tree.

Note: at this point in time, you should **NOT** filter the httpd configurations
to avoid finding directives in incorrect sections.

Examples:
    >>> HTTPD_CONF_1 = '''
    ... # prefork MPM
    ... DocumentRoot "/var/www/html_cgi"
    ... <IfModule prefork.c>
    ... ServerLimit 256
    ... ThreadsPerChild 16
    ... MaxClients  256
    ... </IfModule>
    ... '''.strip()
    >>> HTTPD_CONF_2 = '''
    ... DocumentRoot "/var/www/html"
    ... # prefork MPM
    ... <IfModule prefork.c>
    ... ServerLimit 512
    ... MaxClients  512
    ... </IfModule>
    ... <VirtualHost 192.0.2.1>
    ... <IfModule !php5_module>
    ...     <IfModule !php4_module>
    ...         <FilesMatch ".php[45]?$">
    ...             Deny from all
    ...         </FilesMatch>
    ...     </IfModule>
    ... </IfModule>
    ... <IfModule mod_rewrite.c>
    ...     RewriteEngine On
    ... </IfModule>
    ... <IfModule mod_rewrite.c>
    ...     RewriteEngine Off
    ... </IfModule>
    ... </VirtualHost>
    ... '''.strip()
    >>> httpd1 = HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    >>> httpd2 = HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf.d/00-z.conf'))
    >>> shared = [{HttpdConf: [httpd1, httpd2]}]
    >>> htd_conf = shared[HttpdConfAll]
    >>> htd_conf.get_active_setting("ThreadsPerChild", ("IfModule", "prefork.c"))[0].value
    '16'
    >>> htd_conf.get_active_setting("MaxClients", ("IfModule", "prefork"))[0]
    ParsedData(value='512', line='MaxClients  512', section='IfModule', section_name='prefork.c', file_name='00-z.conf', file_path='/etc/httpd/conf.d/00-z.conf')
    >>> htd_conf.get_active_setting("DocumentRoot").value
    '/var/www/html'
    >>> htd_conf.get_active_setting("RewriteEngine", ('IfModule', 'mod_rewrite.c'))[-1].value
    'Off'
    >>> htd_conf.get_active_setting('Deny', section=('FilesMatch','".php[45]?$"'))[-1].value
    'from all'
    >>> htd_conf.get_section_list("VirtualHost")
    [(('VirtualHost', '192.0.2.1'), '00-z.conf', '/etc/httpd/conf.d/00-z.conf')]
"""
import six
from insights.contrib.ipaddress import ip_address, ip_network
from collections import namedtuple

from insights import run
from insights.core import ConfigCombiner, ConfigParser
from insights.core.plugins import combiner, parser
from insights.configtree import BinaryBool, UnaryBool
from insights.configtree import Directive, Section
from insights.configtree import DocParser, LineGetter, parse_name_attrs, startswith
from insights.configtree import caseless
from insights.parsers.httpd_conf import HttpdConf, dict_deep_merge, ParsedData
from insights.specs import Specs


@combiner(HttpdConf)
class HttpdConfAll(object):
    """
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
            elif (not isinstance(section, tuple) or
                    (len(section) == 0 or len(section) > 2)):
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


class HttpConfDocParser(DocParser):
    """
    Wrapper class so parser functions don't have to thread ctx.

    This is not an Insights parser but a document parser indirectly used by an
    Insights parser. It produces a configtree model constructed of ``Node``
    instances.
    """
    def parse_directive(self, lg):
        line = next(lg)
        name, attrs = parse_name_attrs(line)
        return Directive(name=name, attrs=attrs, ctx=self.ctx)

    def parse_section_body(self, lg):
        body = []
        while not lg.peek().startswith("</"):
            body.append(self.parse_statement(lg))
        return body

    def parse_section(self, lg):
        line = next(lg).strip("<> ")
        name, attrs = parse_name_attrs(line)
        body = None
        try:
            body = self.parse_section_body(lg)
        except:
            raise Exception("Expected end tag for %s" % name)

        end = next(lg).strip("</> ")
        if caseless(name) != caseless(end):
            raise Exception("Tag mismatch: %s != %s" % (name, end))
        return Section(name=name, attrs=attrs, children=body, ctx=self.ctx)

    def parse_statement(self, lg):
        line = lg.peek()
        pos = lg.pos
        if line.startswith("<") and not line.startswith("</"):
            el = self.parse_section(lg)
        else:
            el = self.parse_directive(lg)
        el.pos = pos
        return el


def parse_doc(f, ctx=None):
    """ Accepts an open file or a list of lines. """
    return HttpConfDocParser(ctx).parse_doc(LineGetter(f))


@parser(Specs.httpd_conf)
class _HttpdConf(ConfigParser):
    """ Parser for individual httpd configuration files. """
    def parse_doc(self, content):
        return parse_doc(content, ctx=self)


@combiner(_HttpdConf)
class HttpdConfTree(ConfigCombiner):
    """
    Exposes httpd configuration through the configtree interface. Correctly
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


@parser(Specs.httpd_conf_scl_httpd24)
class _HttpdConfSclHttpd24(ConfigParser):
    """ Parser for individual httpd configuration files. """
    def parse_doc(self, content):
        return parse_doc(content, ctx=self)


@combiner(_HttpdConfSclHttpd24)
class HttpdConfSclHttpd24Tree(ConfigCombiner):
    """
    Exposes httpd configuration Software Collection httpd24 through the configtree
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


@parser(Specs.httpd_conf_scl_jbcs_httpd24)
class _HttpdConfSclJbcsHttpd24(ConfigParser):
    """ Parser for individual httpd configuration files. """
    def parse_doc(self, content):
        return parse_doc(content, ctx=self)


@combiner(_HttpdConfSclJbcsHttpd24)
class HttpdConfSclJbcsHttpd24Tree(ConfigCombiner):
    """
    Exposes httpd configuration Software Collection jbcs-httpd24 through the configtree
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
    local machine or an archive. It's for use in interactive sessions.
    """
    return run(HttpdConfTree, root=root).get(HttpdConfTree)


is_private = UnaryBool(lambda x: ip_address(six.u(x)).is_private)
"""
Predicate to check if an ip address is private.

Example:
    conf["VirtualHost", in_network("128.39.0.0/16")]
"""

in_network = BinaryBool(lambda x, y: (ip_address(six.u(x)) in ip_network(six.u(y))))
"""
Predicate to check if an ip address is in a given network.

Example:
    conf["VirtualHost", in_network("128.39.0.0/16")]
"""


if __name__ == "__main__":
    run(HttpdConfTree, print_summary=True)
