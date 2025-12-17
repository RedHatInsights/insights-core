"""
DBusConfAll - files ``/etc/dbus-1/*.conf``
==========================================

Combiner for accessing all the dbus configuration files. This combiner
combines all dbus configuration files from ``/etc/dbus-1/`` directory
into a single dictionary for easy access.

"""
from insights.core.plugins import combiner
from insights.parsers.dbus_conf import DBusConf


@combiner(optional=[DBusConf])
class DBusConfAll(dict):
    """
    Combiner for accessing all the dbus configuration files.

    This combiner provides a unified view of all dbus configuration files.
    It also provides methods to check if a limit is configured in any of the
    configuration files.

    Examples:
        >>> type(dbus_confs)
        <class 'insights.combiners.dbus_conf.DBusConfAll'>
        >>> '/etc/dbus-1/system.conf' in dbus_confs
        True
        >>> dbus_confs.has_limit_in_any('max_match_rules_per_connection')
        False
    """

    def __init__(self, confs):
        super(DBusConfAll, self).__init__()
        if confs:
            for conf in confs:
                self[conf.file_path] = conf

    def has_limit_in_any(self, limit_name):
        """
        Check if a limit is configured in any of the configuration files.

        Args:
            limit_name (str): The limit name to search for.

        Returns:
            bool: True if the limit is configured in any file, False otherwise.
        """
        for conf in self.values():
            if conf.has_limit(limit_name):
                return True
        return False

    def has_option_in_any(self, option):
        """
        Check if an option exists in any of the configuration files.

        Args:
            option (str): The option string to search for.

        Returns:
            bool: True if the option exists in any file, False otherwise.
        """
        for conf in self.values():
            if conf.has_option(option):
                return True
        return False

    def get_limit_from_any(self, limit_name):
        """
        Get the value of a limit from the first configuration file that has it.

        Args:
            limit_name (str): The limit name to search for.

        Returns:
            tuple: (file_path, value) or (None, None) if not found.
        """
        for path, conf in self.items():
            if conf.has_limit(limit_name):
                return (path, conf.get_limit(limit_name))
        return (None, None)

    def get_files_with_limit(self, limit_name):
        """
        Get list of files that have the specified limit configured.

        Args:
            limit_name (str): The limit name to search for.

        Returns:
            list: List of file paths that have the limit configured.
        """
        files = []
        for path, conf in self.items():
            if conf.has_limit(limit_name):
                files.append(path)
        return files
