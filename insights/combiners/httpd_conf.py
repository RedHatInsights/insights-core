"""
Combiner for httpd configurations
=================================

Combiner for parsing part of httpd configurations. It collects all
HttpdConf generated from each httpd configuration files and get the valid
settings by sorting the file's in alphanumeric order. It provides an interface
to get the valid value of specific directive.

It also correctly handles position of ``IncludeOptional conf.d/*.conf`` line.

Note: at this point in time, you should **NOT** filter the httpd configurations
to avoid find "directives" from incorrect "Sections"

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
from collections import namedtuple

from insights.core.plugins import combiner
from insights.parsers.httpd_conf import HttpdConf, dict_deep_merge, ParsedData
from insights.util import deprecated


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
    # TODO document the changes (merged_data_dict, unmerged_data_list) in docstrings
    # TODO somehow deprecate the name 'full_data_dict' in favor of 'merged_data_dict'
    ConfigData = namedtuple('ConfigData', ['file_name', 'file_path', 'full_data_dict', 'unmerged_data_list'])

    def __init__(self, httpd_conf):
        self.merged_data_active_first = {}
        self.merged_data_active_last = {}
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
                                                         httpd_parser.data,
                                                         httpd_parser.nomerge_data))
            else:
                main_config_data.append(self.ConfigData(file_name, file_path,
                                                        httpd_parser.first_half,
                                                        httpd_parser.nomerge_first_half))
                main_config_data.append(self.ConfigData(file_name, file_path,
                                                        httpd_parser.second_half,
                                                        httpd_parser.nomerge_second_half))

        # Sort configuration files
        config_files_data.sort()

        # Add both parts of main configuration file and store as attribute.
        # These values can be used when looking for bad settings which are not actually active
        # but may become active if other configurations are changed
        if main_config_data:
            self.config_data = [main_config_data[0]] + config_files_data + [main_config_data[1]]
        else:
            self.config_data = config_files_data

        # Store active settings - the first/last parsed value is stored
        for _, _, merged_data, _ in self.config_data:
            copy_data = merged_data.copy()
            for option, parsed_data in copy_data.items():
                if isinstance(parsed_data, dict):
                    # last version of the data is preserved
                    if option not in self.merged_data_active_last:
                        self.merged_data_active_last[option] = {}
                    dict_deep_merge(self.merged_data_active_last[option], parsed_data)
                    # first version of the data is preserved
                    if option not in self.merged_data_active_first:
                        self.merged_data_active_first[option] = {}
                    tmp_contents = {}
                    # first, put in the new data
                    dict_deep_merge(tmp_contents, parsed_data)
                    first_contents = self.merged_data_active_first[option]
                    # second, overwrite the new data with the first version
                    dict_deep_merge(tmp_contents, first_contents)
                    # third, save that
                    # TODO: Find out whether it would be possible to save it in fewer steps without
                    #       the copying. I've seen [jsvoboda] hard to debug mistakes caused by
                    #       using references to the same instance instead of shallow copies, so I
                    #       took the safer route.
                    dict_deep_merge(self.merged_data_active_first[option], parsed_data)
                else:
                    # any method has to take the last element to get the active one
                    if option not in self.merged_data_active_last:
                        self.merged_data_active_last[option] = []
                    self.merged_data_active_last[option].extend(parsed_data)
                    # any method has to take the first element to get the active one
                    if option not in self.merged_data_active_first:
                        self.merged_data_active_first[option] = []
                    self.merged_data_active_first[option].extend(parsed_data)

    # TODO explain in docstring that it is merged
    # TODO create an alternative that uses unmerged data (and mention it in the docstring)
    def get_setting_list(self, directive, section=None):
        """
        Returns the parsed data of the specified directive as a list.

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
            return _deep_search(self.merged_data_active_last, directive, section)

        return self.merged_data_active_last.get(directive, [])

    def get_setting_active_first(self, directive, section=None):
        pass
        # TODO

    def get_setting_active_last(self, directive, section=None):
        """
        Returns the parsed data of the specified directive as a list of named tuples. Returns only
        the last value in the file load order, the previous values of the requested directive are
        considered shadowed and inactive.

        Note:
            Use ``get_setting_active_first``  to get the opposite behavior of using the first
            found matching directive and ignoring all others in the file load order.
            Use ``get_setting_list`` to get all matching directives without any shadowing/ignoring.

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

    def get_active_setting(self, directive, section=None):
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
        deprecated(self.get_active_setting, "Use get_setting_active_last() instead. Alternatively, consider using get_setting_list() because for many rules it is safer to hit on all matches than to presume which matched directives are or are not shadowed.")
        return self.get_setting_active_last(directive, section=section)

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
            return _deep_search(self.merged_data_active_last, section)

        return []
