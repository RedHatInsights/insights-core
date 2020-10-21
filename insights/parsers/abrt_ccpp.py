"""
AbrtCCppConf - file "/etc/abrt/plugins/CCpp.conf"
=================================================

The AbrtCCppConf class parses the file ``/etc/abrt/plugins/CCpp.conf``.
On success it returns ``dict`` containing abrtcpp setting else it returns ``None``.

Sample Data::


    # Configuration file for CCpp hook

    # CCpp hook writes its template to the "/proc/sys/kernel/core_pattern" file
    # and stores the original template in the "/var/run/abrt/saved_core_pattern"
    # file. If you want CCpp hook to create a core dump file named according to
    # the original template as well, set 'MakeCompatCore' to 'yes'.
    # If the original template string starts with "|", the string "core" is used
    # instead of the template.
    # For more information about naming core dump files see 'man 5 core'.
    MakeCompatCore = yes

    # The option allows you to set limit for the core file size in MiB.
    #
    # This value is compared to value of the MaxCrashReportSize configuration
    # option from (/etc/abrt.conf) and the lower value is used as the limit.
    #
    # If MaxCoreFileSize is 0 then the value of MaxCrashReportSize is the limit.
    # If MaxCrashReportSize is 0 then the value of MaxCoreFileSize is the limit.
    # If both values are 0 then the core file size is unlimited.
    MaxCoreFileSize = 0

    # Do you want a copy of crashed binary be saved?
    # (useful, for example, when _deleted binary_ segfaults)
    SaveBinaryImage = no

    # When this option is set to 'yes', core backtrace is generated
    # from the memory image of the crashing process. Only the crash
    # thread is present in the backtrace.
    CreateCoreBacktrace = yes

    # Save full coredump? If set to 'no', coredump won't be saved
    # and you won't be able to report the crash to Bugzilla. Only
    # useful with CreateCoreBacktrace set to 'yes'. Please
    # note that if this option is set to 'no' and MakeCompatCore
    # is set to 'yes', the core is still written to the current
    # directory.
    SaveFullCore = yes

    # Used for debugging the hook
    #VerboseLog = 2

    # Specify where you want to store debuginfos (default: /var/cache/abrt-di)
    #
    DebuginfoLocation = /var/cache/abrt-di

    # ABRT will ignore crashes in executables whose absolute path matches one of
    # specified patterns.
    #
    #IgnoredPaths =

    # ABRT will process only crashes of either allowed users or users who are
    # members of allowed group. If no allowed users nor allowed group are specified
    # ABRT will process crashes of all users.
    #
    #AllowedUsers =
    #AllowedGroups =


Example:
    >>> type(abrt_conf)
    <class 'insights.parsers.abrt_ccpp.AbrtCCppConf'>
    >>> abrt_conf.get('CreateCoreBacktrace')
    'yes'

"""


from insights.specs import Specs
from insights import Parser, parser
from insights.parsers import split_kv_pairs
from insights.parsers import SkipException


@parser(Specs.abrt_ccpp_conf)
class AbrtCCppConf(Parser, dict):
    """
    Class for parsing ``/etc/abrt/plugins/CCpp.conf``.
    """
    def parse_content(self, content):
        self.update(split_kv_pairs(content, use_partition=False))
        if not self:
            raise SkipException("empty content")
