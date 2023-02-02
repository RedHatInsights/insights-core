"""
Sealert - command ``/usr/bin/sealert -l "*"``
=============================================
"""
from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs


class Report(object):

    def __init__(self):
        self.lines = []

    def __str__(self):
        return "\n".join(self.lines).strip()

    def append_line(self, x):
        self.lines.append(x)

    def lines_stripped(self):
        """
        Returns the lines without trailing empty lines

        Returns:
            list: The lines without empty lines at the end of the list.
        """
        lines = self.lines[:]
        for index in range(len(self.lines) - 1, -1, -1):
            if lines[index] == '':
                del (lines[index])
            else:
                break
        return lines


@parser(Specs.sealert)
class Sealert(CommandParser):
    """
    Reads the output of ``/usr/bin/sealert -l "*"``.

    Sample output:

    .. code-block:: none

        SELinux is preventing sh from entrypoint access on the file /usr/bin/podman.

        *****  Plugin catchall (100. confidence) suggests **************************

        If you believe that sh should be allowed entrypoint access on the podman file by default.
        Then you should report this as a bug.
        You can generate a local policy module to allow this access.
        Do
        allow this access for now by executing:
        # ausearch -c 'sh' --raw | audit2allow -M my-sh
        # semodule -X 300 -i my-sh.pp

        Additional Information:
        Source Context unconfined_u:system_r:rpm_script_t:s0-s0:c0.c1023
        Target Context system_u:object_r:container_runtime_exec_t:s0
        Target Objects                /usr/bin/podman [ file ]
        Source                        sh
        Source Path                   sh
        Port                          <Unknown>
        Host                          localhost.localdomain
        Source RPM Packages
        Target RPM Packages           podman-1.1.2-1.git0ad9b6b.fc28.x86_64
        Policy RPM                    selinux-policy-3.14.1-54.fc28.noarch
        Selinux Enabled               True
        Policy Type                   targeted
        Enforcing Mode                Enforcing
        Host Name                     localhost.localdomain
        Platform                      Linux localhost.localdomain 4.20.7-100.fc28.x86_64
                                      #1 SMP Wed Feb 6 19:17:09 UTC 2019 x86_64 x86_64
        Alert Count                   1
        First Seen                    2019-07-30 11:15:04 CEST
        Last Seen                     2019-07-30 11:15:04 CEST
        Local ID                      39a7094b-e402-4d87-9af9-e97eda41219a

        Raw Audit Messages
        type=AVC msg=audit(1564478104.911:4631): avc:  denied  { entrypoint } for  pid=29402 comm="sh" path="/usr/bin/podman" dev="dm-1" ino=955465 scontext=unconfined_u:system_r:rpm_script_t:s0-s0:c0.c1023 tcontext=system_u:object_r:container_runtime_exec_t:s0 tclass=file permissive=0

        Hash: sh,rpm_script_t,container_runtime_exec_t,file,entrypoint

    Examples:
        >>> type(sealert)
        <class 'insights.parsers.sealert.Sealert'>
        >>> sealert.raw_lines[0]
        'SELinux is preventing rngd from using the dac_override capability.'
        >>> sealert.reports[1].lines_stripped()[0]
        'SELinux is preventing sh from entrypoint access on the file /usr/bin/podman.'
        >>> str(sealert.reports[1]).split('\\n')[0]
        'SELinux is preventing sh from entrypoint access on the file /usr/bin/podman.'

    Attributes:
        raw_lines (list[str]): Unparsed output as list of lines
        reports (list[Report]): Sealert reports

    Raises:
        SkipComponent: When output is empty
    """
    SELINUX_DISABLED_MESSAGE = "unable to establish connection to setroubleshoot daemon!"

    def __init__(self, context):
        super(Sealert, self).__init__(context, extra_bad_lines=[self.SELINUX_DISABLED_MESSAGE])

    def parse_content(self, content):
        self.raw_lines = content
        self.reports = []

        for line in content:
            if line.startswith("SELinux is preventing "):
                self.reports.append(Report())
            if self.reports:  # skips the first report if it contains only partial data
                self.reports[-1].append_line(line)
