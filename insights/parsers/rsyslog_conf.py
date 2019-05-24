"""
Parser - file ``/etc/rsyslog.conf``
===================================

RsyslogConf - file ``/etc/rsyslog.conf`` RHEL-6/7
-------------------------------------------------
RsyslogConf8 - file ``/etc/rsyslog.conf`` RHEL-8
-------------------------------------------------

The rsyslog configuration files can include statements with two different
line based formats along with snippets of 'RainerScript' that can span
multiple lines.

See http://www.rsyslog.com/doc/master/configuration/basic_structure.html#statement-types

Due to high parsing complexity, this parser presents a simple line-based
view of the file that meets the needs of the current rules.

Example:
    >>> type(rsl)
    <class 'insights.parsers.rsyslog_conf.RsyslogConf'>
    >>> len(rsl)
    5
    >>> len(list(rsl))
    5
    >>> any('imtcp' in n for n in rsl)
    True
"""
from .. import Parser, parser, get_active_lines

import re
from insights.specs import Specs
from insights.components.rhel_version import IsRhel6, IsRhel7, IsRhel8


@parser(Specs.rsyslog_conf, [IsRhel6, IsRhel7])
class RsyslogConf(Parser):
    """
    Parses `/etc/rsyslog.conf` info simple lines.

    Skips lines that begin with hash ("#") or are only whitespace.

    Attributes:
        data (list): List of lines in the file that don't start
            with '#' and aren't whitespace.
        config_items(dict): Configuration items opportunistically found in the
            configuration file, with their values as given.
    """

    def parse_content(self, content):
        self.data = get_active_lines(content)

        self.config_items = {}
        # Config items are e.g. "$Word value #optional comment"
        config_re = re.compile(r'^\s*\$(?P<name>\S+)\s+(?P<value>.*?)(?:\s+#.*)?$')
        for line in self.data:
            lstrip = line.strip()
            match = config_re.match(lstrip)
            if match:
                self.config_items[match.group('name')] = match.group('value')

    def config_val(self, item, default=None):
        """
        Return the given configuration item, or the default if not defined.

        Parameters:
            item(str): The configuration item name
            default: The default if the item is not found (defaults to None)

        Returns:
            The related value in the `config_items` dictionary.
        """
        return self.config_items.get(item, default)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for d in self.data:
            yield d


@parser(Specs.rsyslog_conf, IsRhel8)
class RsyslogConf8(Parser):
    """
    This combiner is designed for RHEL-8 and other versions of RHEL. There is
    a difference between configuration ``/etc/rsyslog.conf`` file on RHEL-8 and
    other versions of RHEL.

    Example:
        >>> type(rsys)
        <class 'insights.parsers.rsyslog_conf.RsyslogConf8'>
        >>> len(rsys.module_details)
        5
        >>> len(rsys.include_details)
        1
    """

    def parse_content(self, content):
        self._module_details = {}
        self._include_details = {}
        self._input_details = {}
        self._global_details = {}
        self._log_details = {}

        self.data = get_active_lines(content)
        for line in self.data:
            # Parse module and its configurations on two different line
            if ('$' not in line) and (line.startswith('module')) and '(' in line and (not line.endswith(')')):
                module_name = re.split(r'\W+', line)[2]
                self._module_details[module_name] = {}
            # Parse module and its configurations on two different line.
            elif ('$' not in line) and ('module' not in line) and '(' not in line and line.endswith(')'):
                line_split = re.findall(r'[a-z.:/*A-Z0-9_]+', line)
                log_level = line_split[0]
                status = line_split[1]
                self._module_details[module_name][log_level] = status
            # Parse module and its configurations on one line.
            elif ('$' not in line) and (line.startswith('module')) and '(' in line and (line.endswith(')')):
                line_split = re.findall(r'[a-z:A-Z0-9_]+', line)
                module_name = line_split[2]
                self._module_details[module_name] = {}
                if len(line_split) > 3:
                    timestamp_format = line_split[3]
                    timestamp = line_split[4]
                    self._module_details[module_name][timestamp_format] = timestamp
            # Parse included configration files and modes.
            elif ('$' not in line) and (line.startswith('include')) and '(' in line and (line.endswith(')')):
                line_split = re.findall(r'[a-z.:/*A-Z0-9_]+', line)
                file_path = line_split[2]
                self._include_details[file_path] = {}
                file_mode = line_split[3]
                modes = line_split[4]
                self._include_details[file_path][file_mode] = modes
            # Parse input module and its ports.
            elif ('$' not in line) and (line.startswith('input')) and '(' in line and (line.endswith(')')):
                line_split = re.findall(r'[a-z.:/*A-Z0-9_]+', line)
                input_type = line_split[2]
                port = line_split[4]
                self._input_details[input_type] = port
            # Parse global workspace.
            elif ('$' not in line) and (line.startswith('global')) and '(' in line and (line.endswith(')')):
                line_split = re.findall(r'[a-z.:/*A-Z0-9_]+', line)
                global_dir = line_split[1]
                path = line_split[2]
                self._global_details[global_dir] = path
            # Parse other configuations
            else:
                line_split = line.split()
                self._log_details[line_split[0]] = line_split[1]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for d in self.data:
            yield d

    @property
    def module_details(self):
        """
        This will return the dict of all the configured modules on success else
        it will return empty dict `{}` on failure.

        Returns (dict): module details.
        """
        return self._module_details

    @property
    def input_details(self):
        """
        This will return the dict of all the configured input methods on success else
        it will return empty dict `{}` on failure.

        Returns (dict): configuration input details .
        """
        return self._input_details

    @property
    def include_details(self):
        """
        This will return the dict of all included configuration files on success else
        it will return empty dict `{}` on failure.

        Returns (dict): included configuration details.
        """
        return self._include_details

    @property
    def global_details(self):
        """
        This will return the dict of all global dir for all the confiburation files on
        success else it will return empty dict `{}` on failure.

        Returns (dict): included configuration details.
        """
        return self._global_details

    @property
    def log_details(self):
        """
        This will return the dict of all log confiburation details on success else it
        will return empty dict `{}` on failure.

        Returns (dict): included configuration details.
        """
        return self._log_details
