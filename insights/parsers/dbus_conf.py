"""
DBusConf - files ``/etc/dbus-1/*.conf``
=======================================

This module provides parser for the dbus configuration files in ``/etc/dbus-1/``.
The dbus configuration files are in XML format.

"""
import xml.etree.ElementTree as ET

from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.dbus_conf)
class DBusConf(Parser):
    """
    Parses ``/etc/dbus-1/*.conf`` XML content.

    This parser provides access to dbus configuration files which are in XML format.
    It parses the XML content and provides methods to check for specific limits
    like ``max_match_rules_per_connection``.

    Attributes:
        file_path (str): The path of the configuration file.
        file_name (str): The name of the configuration file.
        limits (dict): Dictionary of limit names and their values.
        raw_content (str): The raw content of the configuration file.

    Example:
        >>> type(dbus_conf)
        <class 'insights.parsers.dbus_conf.DBusConf'>
        >>> dbus_conf.file_path
        '/etc/dbus-1/system.conf'
        >>> dbus_conf.has_limit('max_match_rules_per_connection')
        False
        >>> dbus_conf.get_limit('max_match_rules_per_connection')
        None
    """

    def parse_content(self, content):
        """
        Parse the XML content of the dbus configuration file.

        Args:
            content (list): List of lines from the configuration file.
        """
        self.raw_content = '\n'.join(content)
        self.limits = {}

        try:
            # Parse the XML content
            root = ET.fromstring(self.raw_content)

            # Find all <limit> elements and extract their name and value
            for limit_elem in root.iter('limit'):
                name = limit_elem.get('name')
                if name:
                    self.limits[name] = limit_elem.text
        except ET.ParseError:
            # If XML parsing fails, fall back to simple text search
            pass

    def has_limit(self, limit_name):
        """
        Check if a limit is configured in the dbus configuration file.

        Args:
            limit_name (str): The name of the limit to check for.

        Returns:
            bool: True if the limit is configured, False otherwise.
        """
        return limit_name in self.limits

    def get_limit(self, limit_name):
        """
        Get the value of a specific limit.

        Args:
            limit_name (str): The name of the limit to get.

        Returns:
            str: The value of the limit, or None if not found.
        """
        return self.limits.get(limit_name)

    def has_option(self, option):
        """
        Check if an option (limit name) exists in the configuration file.
        This is a convenience method that checks both limits and raw content.

        Args:
            option (str): The option string to search for.

        Returns:
            bool: True if the option exists, False otherwise.
        """
        # First check in parsed limits
        if option in self.limits:
            return True
        # Fall back to raw content search for non-limit options
        return option in self.raw_content
