"""
HttpdConf - files ``/etc/httpd/conf/httpd.conf`` and ``/etc/httpd/conf.d/*``
============================================================================

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
    True
    >>> httpd_conf[('IfModule','mod_mime_magic.c')]
    {'MIMEMagicFile': [ParsedData(value='conf/magic', line='MIMEMagicFile conf/magic', section='IfModule', section_name='mod_mime_magic.c', file_name='path', file_path='/path')]}
    >>> httpd_conf[('IfModule','prefork.c')]['StartServers'][0].value
    '8'
    >>> 'ThreadsPerChild' in httpd_conf[('IfModule','prefork.c')]
    False
    >>> httpd_conf[('IfModule','worker.c')]['MaxRequestsPerChild'][-1].value
    '0'

"""
from collections import namedtuple

import re
from copy import deepcopy
from .. import Parser, parser, get_active_lines, LegacyItemAccess
from insights.specs import Specs

ParsedData = namedtuple('ParsedData', ['value', 'line', 'section', 'section_name', 'file_name', 'file_path'])
"""namedtuple: Type for storing the parsed httpd configuration's directive information."""


@parser(Specs.httpd_conf)
class HttpdConf(LegacyItemAccess, Parser):
    """
    Get the key value pairs separated on the first space, ignoring leading
    and trailing spaces.

    If the file is ``httpd.conf``, it also stores first half, before
    ``IncludeOptional conf.d/*.conf`` line, and the rest, to the ``first_half``
    and ``second_half`` attributes respectively.

    Attributes:
        data (dict): Dictionary of parsed data with key being the option and value a list of
                     named tuples with the following properties:
                     - ``value`` - the value of the keyword.
                     - ``line`` - the complete line as found in the config file.
                     The reason why it is a list is to store data for directives which can use
                     selective overriding such as ``UserDir``.
        first_half (dict): Parsed data from main config file before inclusion of other files in the
                           same format as ``data``.
        second_half (dict): Parsed data from main config file after inclusion of other files in the
                            same format as ``data``.
    """

    def __init__(self, *args, **kwargs):
        self.data = {}
        self.first_half = {}
        self.second_half = {}
        super(HttpdConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        def add_to_dict_list(dictionary, key, element):
            """
            Utility function to create a dictionary of lists instead of using defaultdict, because
            rule would be able to unknowingly modify defaultdict structures.

            Args:
                dictionary (dict): The changed dictionary.
                key (str): The dictionary key to be changed. If it is in the dictionary, ``element``
                           is going to be appended to ``dictionary[key]`` list. If the ``key`` is
                           not in the dictionary, it is created so that
                           ``dictionary[key] = [element]``.
                element (Object): A value to be appended to the list under ``dictionary[key]``.
            """
            if key not in dictionary:
                dictionary[key] = [element]
            else:
                dictionary[key].append(element)

        where_to_store = self.first_half  # Set which part of file is the parser at

        # Flag to be used for different parsing of the main config file
        main_config = self.file_name == 'httpd.conf'

        section = []  # Can be treated as a stack
        for line in get_active_lines(content):
            if main_config and where_to_store is not self.second_half:
                # Dividing line looks like 'IncludeOptional conf.d/*.conf'
                if re.search(r'^\s*IncludeOptional\s+conf\.d', line):
                    where_to_store = self.second_half

            # new section start
            if line.startswith('<') and not line.startswith('</'):
                splits = line.strip('<>').split(None, 1)
                section.append(((splits[0], splits[1] if len(splits) == 2 else ''), {}))
            # one section end
            elif line.startswith('</'):
                sec, pd = section.pop()
                # for nested section
                if section:
                    if sec not in section[-1][-1]:
                        section[-1][-1][sec] = {}
                    dict_deep_merge(section[-1][-1][sec], pd)
                else:
                    if sec not in self.data:
                        self.data[sec] = {}
                        if main_config:
                            where_to_store[sec] = {}
                    dict_deep_merge(self.data[sec], pd)
                    if main_config:
                        dict_deep_merge(where_to_store[sec], pd)
            else:
                try:
                    option, value = [s.strip() for s in line.split(None, 1)]
                except ValueError:
                    continue  # Skip lines which are not 'Option Value'

                value = value.strip('\'"')

                if section:
                    cur_sec = section[-1][0]
                    parsed_data = ParsedData(value, line, cur_sec[0], cur_sec[1], self.file_name, self.file_path)
                    # before: section = [(('IfModule', 'worker.c'), {})]
                    add_to_dict_list(section[-1][-1], option, parsed_data)
                    # after:  section = [(('IfModule', 'worker.c'), [{'MaxClients': (256, 'MaxClients 256')}])]
                else:
                    parsed_data = ParsedData(value, line, None, None, self.file_name, self.file_path)
                    add_to_dict_list(self.data, option, parsed_data)
                    if main_config:
                        add_to_dict_list(where_to_store, option, parsed_data)


def dict_deep_merge(tgt, src):
    """
    Utility function to merge the source dictionary `src` to the target
    dictionary recursively

    Note:
        The type of the values in the dictionary can only be `dict` or `list`

    Parameters:
        tgt (dict): The target dictionary
        src (dict): The source dictionary
    """
    for k, v in src.items():
        if k in tgt:
            if isinstance(tgt[k], dict) and isinstance(v, dict):
                dict_deep_merge(tgt[k], v)
            else:
                tgt[k].extend(deepcopy(v))
        else:
            tgt[k] = deepcopy(v)
