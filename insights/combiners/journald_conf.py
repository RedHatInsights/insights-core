"""
Journald configuration
======================

Combiner for parsing of journald configuration. man journald.conf describes where various
journald config files can reside and how they take precedence one over another. The combiner
implements the logic and provides an interface for querying active settings.

The journald.conf file is a key=value file with hash comments.

The parsers this combiner uses process only active settings (lines that are not commented out). The
resulting settings (after being processed by the precedence evaluation algorithm) are then provided
by the `get_active_settings_value` method and `active_settings` dictionary and by the
`get_active_setting_value_and_file_name` method and `active_settings_with_file_name` dictionary.

Options that are commented out are not returned - a rule using this parser has to be aware of which
default value is assumed by systemd if the particular option is not specified.

Priority from lowest to highest:

* built-in defaults (the same as the default commented entries in /etc/systemd/journald.conf)
* /etc/systemd/journald.conf
* \*.conf in whatever directory in lexicographic order from lowest to highest
* if two \*.conf files with the same name are both in /usr/lib and /etc, the file in /etc wholly
  overwrites the file in /usr/lib

from man journald.conf in RHEL 7.3:

CONFIGURATION DIRECTORIES AND PRECEDENCE

       Default configuration is defined during compilation, so a configuration
       file is only needed when it is necessary to deviate from those
       defaults. By default the configuration file in /etc/systemd/ contains
       commented out entries showing the defaults as a guide to the
       administrator. This file can be edited to create local overrides.

       When packages need to customize the configuration, they can install
       configuration snippets in /usr/lib/systemd/\*.conf.d/. Files in /etc/
       are reserved for the local administrator, who may use this logic to
       override the configuration files installed by vendor packages. The main
       configuration file is read before any of the configuration directories,
       and has the lowest precedence; entries in a file in any configuration
       directory override entries in the single configuration file. Files in
       the \*.conf.d/ configuration subdirectories are sorted by their filename
       in lexicographic order, regardless of which of the subdirectories they
       reside in. If multiple files specify the same option, the entry in the
       file with the lexicographically latest name takes precedence. It is
       recommended to prefix all filenames in those subdirectories with a
       two-digit number and a dash, to simplify the ordering of the files.

       To disable a configuration file supplied by the vendor, the recommended
       way is to place a symlink to /dev/null in the configuration directory
       in /etc/, with the same filename as the vendor configuration file.

Examples:

    >>> conf = shared[JournaldConfAll]
    >>> conf.get_active_setting_value('Storage')
    'auto'
    >>> 'Storage' in conf.active_settings_with_file_name
    True
    >>> conf.get_active_setting_value_and_file_name('Storage')
    ('auto', '/etc/systemd/journald.conf')
"""

from insights.core.plugins import combiner
from insights.parsers.journald_conf import EtcJournaldConf, EtcJournaldConfD, UsrJournaldConfD


# TODO - further insights work - convert this to a generic option & file priority evaluator for
#        other combiners.

@combiner(EtcJournaldConf, optional=[EtcJournaldConfD, UsrJournaldConfD])
class JournaldConfAll(object):
    """
    Combiner for accessing files from the parsers EtcJournaldConf, EtcJournaldConfD, UsrJournaldConfD
    and evaluating effective active settings based on the rules of file priority and file shadowing
    as described in man journald.conf.

    Can be later refactored to a combiner for parsing all configuration files with key=option lines,
    like journald files.

    Rules of evaluation:

    * Files from EtcJournaldConfD wholly shadow/overwrite files from UsrJournaldConfD with identical
      names.
    * Files ordered by name from lowest priority to highest (a.conf has lower priority than b.conf).
    * Option values overwritten by the file with the highest priority.
    * The one central file has either the lowest priority or the highest priority, based on the
      central_file_lowest_prio argument.

    That is:

    * An entire file in UsrJournaldConfD is overwritten by a same-named file from EtcJournaldConfD.
    * A single option value is overwritten when another file with a higher priority has an option
      with the same option name.

    Example of file precedence::

        /etc/systemd/journald.conf:
            key0=value0
            key1=value1

        /usr/lib/systemd/journald.conf.d/a.conf:
            key2=value2
            key3=value3
            key4=value4
            key1=value5

        /usr/lib/systemd/journald.conf.d/b.conf:
            key5=value6
            key6=value7
            key1=value8
            key2=value9
            key4=value10

        /usr/lib/systemd/journald.conf.d/c.conf:
            key7=value11
            key5=value12
            key1=value13

        /etc/systemd/journald.conf.d/b.conf:
            key1=value14
            key5=value15

        the resulting configuration:
            key0=value0
            key1=value13 # c.conf has highest priority
            key2=value2 # b.conf from /usr is shadowed by b.conf from /etc so value from a.conf is used
            key3=value3
            key4=value4 # b.conf from /usr is shadowed by b.conf from /etc so value from a.conf is used
            key5=value12 # c.conf has higher priority than b.conf
            # key6 doesn't exist because b.conf from /usr is shadowed by b.conf from /etc
            key7=value11
    """
    def __init__(self, journal_conf, journal_conf_d, usr_journal_conf_d):

        # preparation for future possible refactoring into a more general combiner
        central_file_lowest_prio = True

        # comments in this method describe journald configuration; it should work for similar ones
        etc_confd = {}  # parser instances indexed by file name
        usr_confd = {}  # parser instances indexed by file name
        if journal_conf_d:
            for parser_instance in journal_conf_d:
                etc_confd[parser_instance.file_name] = parser_instance
        if usr_journal_conf_d:
            for parser_instance in usr_journal_conf_d:
                usr_confd[parser_instance.file_name] = parser_instance

        files_shadowed_not_used = set()  # full file paths of files that are shadowed by others
        effective_confd = {}  # deduplicated *.conf files, taking shadowing /usr by /etc into account
        for file_name, parser_instance in usr_confd.items():
            effective_confd[file_name] = parser_instance
        # /etc/systemd/journald.conf.d/*.conf shadow /usr/lib/systemd/journald.conf.d/*.conf files
        #  with the same name. The following loop overwrites these same-named files by their /etc
        #  counterparts:
        for file_name, parser_instance in etc_confd.items():
            if file_name in effective_confd:
                shadowed_file_name = effective_confd[file_name].file_path
                if shadowed_file_name:
                    # empty and None file names are not added (that is invalid anyway)
                    files_shadowed_not_used.add(shadowed_file_name)
            effective_confd[file_name] = parser_instance

        files_shadowed_not_used = sorted(files_shadowed_not_used)  # deterministic behavior, sorted paths
        sorted_file_names = sorted(effective_confd.keys(), key=str)

        parsers_list = [effective_confd[file_name] for file_name in sorted_file_names]
        if central_file_lowest_prio:
            parsers_list = [journal_conf] + parsers_list
        else:
            parsers_list = parsers_list + [journal_conf]

        files_used_priority_order = []  # from lowest to highest priority, not including empty files
        # storing only the active values as (val, file_name), taking precedence rules into account
        resulting_options_with_file_name = {}
        # *.conf files from the lowest priority to the highest, so that the last value stays
        for parser_instance in parsers_list:
            if parser_instance.active_settings:  # do not iterate if empty or None
                if parser_instance.file_path:
                    # empty and None file names are not added (that is invalid anyway), see test_11
                    files_used_priority_order.append(parser_instance.file_path)
                for k, v in parser_instance.active_settings.items():
                    resulting_options_with_file_name[k] = (v, parser_instance.file_path)

        # not named simply as `active_settings` so as not to confuse the contents with the
        #  `active_settings` dictionary in parsers/journald_conf.py
        #   (dict[str, str] vs. dict[str, tuple[str, str]])
        self.active_settings_with_file_name = resulting_options_with_file_name

        # Not saving directly to self so that if this function fails in the middle, nothing is saved
        #  for the offshoot chance that an exception would be swallowed and the invalid instance
        #  used - prevents incomplete data from being used.
        self.files_shadowed_not_used = files_shadowed_not_used
        self.files_used_priority_order = files_used_priority_order
        super(JournaldConfAll, self).__init__()

    def get_active_setting_value(self, setting_name):
        """
        Access active setting value by setting name.

        Args:
            setting_name (string): Setting name
        """
        return self.active_settings_with_file_name[setting_name][0]

    def get_active_setting_value_and_file_name(self, setting_name):
        """
        Access active setting value by setting name. Returns the active setting value and file name
        of the file in which it is defined. Other files that also specify the setting but are
        shadowed are ignored and not reported.

        Args:
            setting_name (string): Setting name

        Returns:
            tuple[str, str]: setting value, file name
        """
        return self.active_settings_with_file_name[setting_name]
