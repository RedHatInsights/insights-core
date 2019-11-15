from insights.parsers import SkipException
from insights.tests import context_wrap
from insights.parsers.sealert import Sealert, Report
import pytest

INPUT_1 = """
bla bla
ble ble
""".strip()

REPORT_1 = """
SELinux is preventing rngd from using the dac_override capability.


*****  Plugin dac_override (91.4 confidence) suggests **********************

If you want to help identify if domain needs this access or you have a file with the wrong permissions on your system
Then turn on full auditing to get path information about the offending file and generate the error again.
Do

Turn on full auditing
# auditctl -w /etc/shadow -p w
Try to recreate AVC. Then execute
# ausearch -m avc -ts recent
If you see PATH record check ownership/permissions on file, and fix it,
otherwise report as a bugzilla.

*****  Plugin catchall (9.59 confidence) suggests **************************

If you believe that rngd should have the dac_override capability by default.
Then you should report this as a bug.
You can generate a local policy module to allow this access.
Do
allow this access for now by executing:
# ausearch -c 'rngd' --raw | audit2allow -M my-rngd
# semodule -X 300 -i my-rngd.pp


Additional Information:
Source Context                system_u:system_r:rngd_t:s0
Target Context                system_u:system_r:rngd_t:s0
Target Objects                Unknown [ capability ]
Source                        rngd
Source Path                   rngd
Port                          <Unknown>
Host                          localhost.localdomain
Source RPM Packages
Target RPM Packages
Policy RPM                    selinux-policy-3.14.1-54.fc28.noarch
Selinux Enabled               True
Policy Type                   targeted
Enforcing Mode                Enforcing
Host Name                     localhost.localdomain
Platform                      Linux localhost.localdomain 4.20.7-100.fc28.x86_64
                              #1 SMP Wed Feb 6 19:17:09 UTC 2019 x86_64 x86_64
Alert Count                   10
First Seen                    2019-03-08 13:09:05 CET
Last Seen                     2019-07-01 15:28:18 CEST
Local ID                      a81fca67-2c8d-4cb1-b1c2-a97c0521858d

Raw Audit Messages
type=AVC msg=audit(1561987698.393:103): avc:  denied  { dac_override } for  pid=1084 comm="rngd" capability=1 scontext=system_u:system_r:rngd_t:s0 tcontext=system_u:system_r:rngd_t:s0 tclass=capability permissive=0


Hash: rngd,rngd_t,rngd_t,capability,dac_override

""".strip()

REPORT_2 = """
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
""".strip()

INPUT_2 = """

{0}



{1}

""".format(REPORT_1, REPORT_2)


def test_report():
    r = Report()
    r.append_line("")
    r.append_line("a")
    r.append_line("b")
    r.append_line("")
    r.append_line("")
    assert len(r.lines) == 5
    assert len(r.lines_stripped()) == 3
    assert r.lines_stripped() == ["", "a", "b"]
    assert str(r) == "a\nb"


def test_sealert():
    with pytest.raises(SkipException):
        Sealert(context_wrap(INPUT_1))
    with pytest.raises(SkipException):
        Sealert(context_wrap(""))
    sealert = Sealert(context_wrap(INPUT_2))
    assert len(sealert.reports) == 2
    assert str(sealert.reports[0]) == REPORT_1
    assert str(sealert.reports[1]) == REPORT_2
    assert sealert.reports[0].lines[10] == REPORT_1.split("\n")[10]
    assert sealert.reports[0].lines_stripped() == REPORT_1.split("\n")
