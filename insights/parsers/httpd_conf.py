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

# for compatibility with existing rules
# TODO: deprecate in a future version of insights and use only ParsedData2
ParsedData = namedtuple('ParsedData', ['value', 'line', 'section', 'section_name', 'file_name', 'file_path'])
"""namedtuple: Type for storing the parsed httpd configuration's directive information."""

ParsedData2 = namedtuple('ParsedData', ['option', 'value', 'line', 'section', 'section_name', 'file_name', 'file_path'])
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
        nomerge_data (list): List of options and sections. Options are ParsedData2. Sections are
                             tuples with two elements:
                             - tuple of section and section name.
                             - list of options and sections (which can again contain ParsedData2 or
                               tuples for nested sections).
        nomerge_first_half (dict): Parsed data from main config file before inclusion of other files
                                   in the same format as ``nomerge_data``.
        nomerge_second_half (dict): Parsed data from main config file after inclusion of other files
                                    in the same format as ``nomerge_data``.
    """

    def __init__(self, *args, **kwargs):
        self.data = {}
        self.first_half = {}
        self.second_half = {}
        self.nomerge_data = []
        self.nomerge_first_half = []
        self.nomerge_second_half = []
        super(HttpdConf, self).__init__(*args, **kwargs)

    def parse_content(self, content):

        # Flag to be used for different parsing of the main config file
        main_config = self.file_name == 'httpd.conf'

        section = []  # Can be treated as a stack
        for line in get_active_lines(content):

            # new section start
            if line.startswith('<') and not line.startswith('</'):
                splits = line.strip('<>').split(None, 1)
                section.append(((splits[0], splits[1] if len(splits) == 2 else ''), []))
            # one section end
            elif line.startswith('</'):
                sec, pd = section.pop()
                # for nested section
                if section:
                    section[-1][-1].append((sec, pd))
                else:
                    self.nomerge_data.append((sec, pd))
            else:
                try:
                    option, value = [s.strip() for s in line.split(None, 1)]
                except ValueError:
                    continue  # Skip lines which are not 'Option Value'

                value = value.strip('\'"')

                if section:
                    cur_sec = section[-1][0]
                    parsed_data = ParsedData2(option, value, line, cur_sec[0], cur_sec[1], self.file_name, self.file_path)
                    # before: section = [(('IfModule', 'worker.c'), [])]
                    section[-1][-1].append(parsed_data)
                    # after:  section = [(('IfModule', 'worker.c'), [{'MaxClients': ('MaxClients', 256, 'MaxClients 256')}])]
                else:
                    parsed_data = ParsedData2(option, value, line, None, None, self.file_name, self.file_path)
                    self.nomerge_data.append(parsed_data)

        where_to_store = self.nomerge_first_half  # Set which part of file is the parser at
        if main_config:
            for d in self.nomerge_data:
                # assuming that the line doesn't appear inside a section
                if isinstance(d, ParsedData2) and re.search(r'^\s*IncludeOptional\s+conf\.d', d.line):
                    where_to_store = self.nomerge_second_half
                where_to_store.append(d)

        self.data = convert_nomerge_to_merge(self.nomerge_data)
        self.first_half = convert_nomerge_to_merge(self.nomerge_first_half)
        self.second_half = convert_nomerge_to_merge(self.nomerge_second_half)


def convert_nomerge_to_merge(data):
    """
    Utility function that creates a merged representation of the httpd conf data.
    In the merged representation, all observed values of a particular option are in a single list
    in a dictionary keyed by the option, and all observed contents of sections are in a single
    dict in a dictionary keyed by the section.

    Note:
        Before June 2018, this was the only format of the data and it is sufficient for most rules,
        but not for all.

    Parameters:
        data (list): A list of objects, representing a httpd conf file. The list can contain only
                     two types of objects:
                     - ``ParsedData2`` - individual options,
                     - ``tuple[tuple[str, str], list[union[ParsedData2, tuple]]]`` - sections with
                       contents.

    Returns:
        dict[union[str, tuple[str, str]], union[list, dict]] - httpd conf representation where all
                                                               options of the same name have values
                                                               in a single list and all sections of
                                                               the same type and name have contents
                                                               in a single dict.
    """
    merged = {}
    for d in data:
        if isinstance(d, ParsedData2):
            if d.option not in merged:
                merged[d.option] = []
            merged[d.option].append(ParsedData(value=d.value,
                                               line=d.line,
                                               section=d.section,
                                               section_name=d.section_name,
                                               file_name=d.file_name,
                                               file_path=d.file_path))
        else:
            # making sure the section is identified by a tuple
            ((_sec, _sec_name), pd) = d
            sec = (_sec, _sec_name)
            pd_processed = convert_nomerge_to_merge(pd)
            if sec not in merged:
                merged[sec] = {}
            dict_deep_merge(merged[sec], pd_processed)
    return merged


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
