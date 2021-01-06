import doctest

from insights.parsers import ls_etc
from insights.tests import context_wrap


LS_ETC = """
/etc/:
total 388
drwxr-xr-x. 46 1000 1000  4096 Jun 11 21:01 .
drwx------. 15 1000 1000  4096 Aug  5 13:45 ..
drwxr-xr-x.  3 1000 1000  4096 Nov 12  2015 acpi
drwxr-xr-x.  2 1000 1000  4096 Apr 19  2017 alsa
drwxr-xr-x.  2 1000 1000  4096 Apr 19 07:56 alternatives
-rw-r--r--.  1 1000 1000   148 Jan 12  2016 asound.conf
drwxr-x---.  2 1000 1000  4096 Jun 11 20:31 audit
-rw-r--r--.  1 1000 1000 13641 Mar 13  2019 autofs.conf
-rw-------.  1 1000 1000   232 Mar 13  2019 autofs_ldap_auth.conf
-rw-r--r--.  1 1000 1000   667 Mar 13  2019 auto.master
-rw-r--r--.  1 1000 1000   524 Mar 13  2019 auto.misc
-rwxr-xr-x.  1 1000 1000  1260 Mar 13  2019 auto.net
-rwxr-xr-x.  1 1000 1000   687 Mar 13  2019 auto.smb
drwxr-xr-x.  2 1000 1000  4096 Mar 24  2019 cron.d
drwxr-xr-x.  2 1000 1000  4096 Oct 20  2019 cron.daily
-rw-------.  1 1000 1000     0 Jul 22  2016 cron.deny
drwxr-xr-x.  2 1000 1000  4096 Apr 19  2017 cron.hourly
drwxr-xr-x.  2 1000 1000  4096 Mar  5  2015 cron.monthly
-rw-r--r--.  1 1000 1000   457 Jun  3  2011 crontab
drwxr-xr-x.  2 1000 1000  4096 May 17  2019 cups
drwxr-xr-x.  3 1000 1000  4096 Aug 18  2019 dbus-1
-rw-r--r--.  1 1000 1000 21214 Oct 22  2017 dnsmasq.conf
-rw-r--r--.  1 1000 1000  1331 Jun 11 19:33 fstab
drwxr-xr-x.  6 1000 1000  4096 Jul  8  2018 gdm
lrwxrwxrwx.  1 1000 1000    22 Jun 11 20:56 grub.conf -> ../boot/grub/grub.conf
-rw-r--r--.  1 1000 1000     9 Nov  2  2016 host.conf
-rw-r--r--.  1 1000 1000  1128 Mar  6  2019 hosts
-rw-r--r--.  1 1000 1000   158 Jan 12  2010 hosts.20150304.133833
-rw-r--r--.  1 1000 1000   986 Mar  5  2015 hosts.20180326.154713.ihaider
-rw-r--r--.  1 1000 1000   370 Jan 12  2010 hosts.allow
-rw-------.  1 1000 1000  1073 Mar  6  2019 hosts.backup
-rw-r--r--.  1 1000 1000   460 Jan 12  2010 hosts.deny
-rw-r--r--.  1 1000 1000  4850 Feb  8  2017 idmapd.conf
drwxr-xr-x.  2 1000 1000  4096 Jun 11 19:32 init
-rw-r--r--.  1 1000 1000     0 Feb 12  2018 init.conf
drwxr-xr-x.  2 1000 1000  4096 Apr 19 07:55 init.d
-rw-r--r--.  1 1000 1000   884 Apr 27  2018 inittab
drwxr-xr-x.  2 1000 1000  4096 Jul  8  2018 iproute2
-rw-r--r--.  1 1000 1000  2380 Jan  9  2020 ipsec.conf
drwx------.  3 1000 1000  4096 Mar 20 15:12 ipsec.d
drwxr-xr-x.  2 1000 1000  4096 Jun 27  2018 iscsi
drwxr-xr-x.  2 1000 1000  4096 Mar 24  2019 java
-rw-r--r--.  1 1000 1000  8120 Jul  8  2018 kdump.conf
-rw-r--r--.  1 1000 1000  4752 Jun 11 21:00 krb5.conf
-rw-r--r--.  1 1000 1000    28 Jul 25  2013 ld.so.conf
drwxr-xr-x.  2 1000 1000  4096 Jun 11 20:55 ld.so.conf.d
-rw-r--r--.  1 1000 1000  3519 May  4  2010 localtime
-rw-r--r--.  1 1000 1000   215 Nov 19  2013 logrotate.conf
-rw-r--r--.  1 1000 1000   662 Aug 29  2007 logrotate.conf.20150304.134454
drwxr-xr-x.  2 1000 1000  4096 Apr 19 07:56 logrotate.d
-rw-r--r--.  1 1000 1000   152 Mar  5  2015 lsb-release
drwxr-xr-x.  2 1000 1000  4096 Mar  5  2015 lsb-release.d
drwxr-xr-x.  6 1000 1000  4096 Jan 20  2018 lvm
drwxr-xr-x.  2 1000 1000  4096 Jun 11 19:32 modprobe.d
-rw-r--r--.  1 1000 1000   744 Sep 18  2014 multipath.conf
drwxr-xr-x.  2 1000 1000  4096 Sep 12  2018 NetworkManager
-rw-r--r--.  1 1000 1000    58 Apr 27  2018 networks
-rw-r--r--.  1 1000 1000  3605 Mar  3 00:32 nfsmount.conf
-rw-r--r--.  1 1000 1000  1724 Mar  5  2015 nsswitch.conf
drwxr-xr-x.  2 1000 1000  4096 Jan 27  2019 ntp
-rw-r--r--.  1 1000 1000   261 Mar 23  2016 ntp.conf
drwxr-xr-x.  3 1000 1000  4096 Apr 19  2017 openldap
drwxr-xr-x.  2 1000 1000  4096 Jun 11 21:00 pam.d
drwxr-xr-x.  4 1000 1000  4096 Apr 19  2017 pki
drwxr-xr-x.  2 1000 1000  4096 Apr 19  2017 postfix
drwxr-xr-x.  2 1000 1000  4096 Apr 19 07:56 ppp
drwxr-xr-x. 10 1000 1000  4096 Jul  8  2018 rc.d
-rw-r--r--.  1 1000 1000    56 Nov 22  2019 redhat-release
-rw-r--r--.  1 1000 1000  1484 Jul 22  2014 request-key.conf
drwxr-xr-x.  2 1000 1000  4096 Apr 19 07:55 request-key.d
-rw-r--r--.  1 1000 1000    71 Mar  5  2015 resolv.conf
drwxr-xr-x.  3 1000 1000  4096 Oct 20  2019 rhsm
-rw-r--r--.  1 1000 1000  2951 Apr 19  2017 rsyslog.conf
drwxr-xr-x.  2 1000 1000  4096 Jan 17  2020 samba
drwxr-xr-x.  4 1000 1000  4096 May 29 09:35 security
drwxr-xr-x.  3 1000 1000  4096 Dec  6  2017 selinux
drwxr-xr-x.  2 1000 1000  4096 Jan 17  2020 snmp
-rw-r--r--.  1 1000 1000   256 Oct  9  2019 sos.conf
drwxr-xr-x.  2 1000 1000  4096 Jun 11 21:01 ssh
drwxr-xr-x.  6 1000 1000  4096 Jun 11 20:55 sysconfig
-rw-r--r--.  1 1000 1000  1183 Apr 17 09:32 sysctl.conf
drwxr-xr-x.  3 1000 1000  4096 Jan 17  2020 udev
drwxr-xr-x.  2 1000 1000  4096 Aug  4 16:02 vmware-tools
drwxr-xr-x.  3 1000 1000  4096 Jul  8  2018 X11
-rw-------.  1 1000 1000  1001 Dec 16  2015 xinetd.conf
drwxr-xr-x.  2 1000 1000  4096 Apr 19  2017 xinetd.d
drwxr-xr-x.  3 1000 1000  4096 Apr 16  2017 yum
-rw-r--r--.  1 1000 1000   813 Mar 15  2016 yum.conf
drwxr-xr-x.  2 1000 1000  4096 Apr 19 07:53 yum.repos.d

/etc/rc.d/init.d:
total 460
drwxr-xr-x.  2 1000 1000  4096 Apr 19 07:55 .
drwxr-xr-x. 10 1000 1000  4096 Jul  8  2018 ..
-rwxr-xr-x.  1 1000 1000  1287 Jan 24  2018 abrt-ccpp
-rwxr-xr-x.  1 1000 1000  1628 Jan 24  2018 abrtd
-rwxr-xr-x.  1 1000 1000  1641 Jan 24  2018 abrt-oops
-rwxr-xr-x.  1 1000 1000  1818 Nov 12  2015 acpid
-rwxr-xr-x.  1 1000 1000  2062 Oct 18  2016 atd
-rwxr-xr-x.  1 1000 1000  3580 Dec 22  2016 auditd
-rwxr-xr-x.  1 1000 1000  4040 Mar 13  2019 autofs
-rwxr-xr-x.  1 1000 1000 11695 Aug 16  2019 b9daemon
-rwxr-xr-x.  1 1000 1000  2105 Dec  4  2014 besclient
-r-xr-xr-x.  1 1000 1000  1362 Nov  2  2017 blk-availability
-rwxr--r--.  1 1000 1000  2155 Jan 29  2019 cbdaemon
-rwxr-xr-x.  1 1000 1000  2010 Mar  5  2015 centrifydc
-rwxr-xr-x.  1 1000 1000 11864 Jun 16  2015 cpuspeed
-rwxr-xr-x.  1 1000 1000  2826 Jul 22  2016 crond
-rwxr-xr-x.  1 1000 1000  3034 Feb 27  2019 cups
-rwxr-xr-x.  1 1000 1000  1734 Sep 27  2017 dnsmasq
-rw-r--r--.  1 1000 1000 25592 Apr 27  2018 functions
-rwxr-xr-x.  1 1000 1000  1801 Jun 19  2014 haldaemon
-rwxr-xr-x.  1 1000 1000  5985 Apr 27  2018 halt
-rwxr-xr-x.  1 1000 1000 11244 Apr 16  2018 ip6tables
-rwxr-xr-x.  1 1000 1000  6548 Jan  9  2020 ipsec
-rwxr-xr-x.  1 1000 1000 11123 Apr 16  2018 iptables
-rwxr-xr-x.  1 1000 1000  1938 Feb  2  2018 irqbalance
-rwxr-xr-x.  1 1000 1000  4535 Jun  9  2017 iscsi
-rwxr-xr-x.  1 1000 1000  3990 Jun  9  2017 iscsid
-rwxr-xr-x.  1 1000 1000 21406 Apr 12  2018 kdump
-rwxr-xr-x.  1 1000 1000   652 Apr 27  2018 killall
-r-xr-xr-x.  1 1000 1000  2137 Nov  2  2017 lvm2-lvmetad
-r-xr-xr-x.  1 1000 1000  3045 Nov  2  2017 lvm2-monitor
-rwxr-xr-x.  1 1000 1000  2103 Oct 27  2015 mcelogd
-rwxr-xr-x.  1 1000 1000  2571 Jan 26  2017 mdmonitor
-rwxr-xr-x.  1 1000 1000  2200 Jul  8  2019 messagebus
-rwxr-xr-x.  1 1000 1000  2523 Sep 11  2018 multipathd
-r-x------.  1 1000 1000 22776 Mar  5  2015 netbackup
-rwxr-xr-x.  1 1000 1000  4334 Apr 27  2018 netconsole
-rwxr-xr-x.  1 1000 1000  5309 Apr 27  2018 netfs
-rwxr-xr-x.  1 1000 1000  6742 Apr 27  2018 network
-rwxr-xr-x.  1 1000 1000  2188 Jan 13  2017 NetworkManager
-rwxr-xr-x.  1 1000 1000  6889 Mar  3 00:32 nfs
-rwxr-xr-x.  1 1000 1000  3526 Mar  3 00:32 nfslock
-rwxr-xr-x.  1 1000 1000  3570 Nov 23  2016 nfs-rdma
-rwxr-xr-x.  1 1000 1000  1923 Dec 11  2018 ntpd
-rwxr-xr-x.  1 1000 1000  2043 Dec 11  2018 ntpdate
-rwxr-xr-x.  1 1000 1000  2023 Mar 17  2016 portreserve
-rwxr-xr-x.  1 1000 1000  3912 Oct 31  2016 postfix
-rwxr-xr-x.  1 1000 1000  1738 Mar  1  2016 pppoe-server
-rwxr-xr-x.  1 1000 1000  1556 Nov  2  2016 psacct
-rwxr-xr-x.  1 1000 1000  2034 Jan  7  2015 quota_nld
-rwx------.  1 1000 1000  2092 Feb  1  2018 rc.agent_user
-rwxr-xr-x.  1 1000 1000  1513 Dec  7  2016 rdisc
-rwxr-xr-x.  1 1000 1000 12856 Nov 23  2016 rdma
-rwxr-xr-x.  1 1000 1000  1822 Oct 25  2016 restorecond
-rwxr-xr-x.  1 1000 1000  2898 Mar 19  2010 rhnsd
-rwxr-xr-x.  1 1000 1000  1770 Jun 26  2019 rhsmcertd
-rwxr-xr-x.  1 1000 1000  1808 Sep  3  2015 rngd
-rwxr-xr-x.  1 1000 1000  2073 Feb  8  2018 rpcbind
-rwxr-xr-x.  1 1000 1000  2518 Mar  3 00:32 rpcgssd
-rwxr-xr-x.  1 1000 1000  2305 Mar  3 00:32 rpcidmapd
-rwxr-xr-x.  1 1000 1000  2464 Mar  3 00:32 rpcsvcgssd
-rwxr-xr-x.  1 1000 1000  2011 Dec  1  2017 rsyslog
-rwxr-xr-x.  1 1000 1000  1698 Oct 25  2016 sandbox
-rwxr-xr-x.  1 1000 1000  2056 Feb 27  2015 saslauthd
-rwxr--r--.  1 1000 1000  1642 Apr 10  2017 scx-cimd
-rwxr-xr-x.  1 1000 1000   647 Apr 27  2018 single
-rwxr-xr-x.  1 1000 1000  3002 Oct 21  2016 smartd
-rwxr-xr-x.  1 1000 1000  2162 Sep 26  2019 snmpd
-rwxr-xr-x.  1 1000 1000  1738 Sep 26  2019 snmptrapd
-rwxr-xr-x.  1 1000 1000  2472 Apr  2  2019 spice-vdagentd
-rwx------.  1 1000 1000  1028 Jun 23  2018 splunk
-rwxr-xr-x.  1 1000 1000  4621 Mar 20  2019 sshd
-rwxr-xr-x.  1 1000 1000  1144 Nov 13  2017 sysstat
-rwxr-xr-x.  1 1000 1000  2096 Mar 15  2018 tsys-notify
-rwxr-xr-x.  1 1000 1000  2265 Jun 23  2014 tsys-notify.20190401.214025.
-rwxr-xr-x.  1 1000 1000  2294 Oct  1  2019 udev-post
-rwxr-xr-x.  1 1000 1000  3176 Apr  5  2019 udsagent
lrwxrwxrwx.  1 1000 1000    30 Jun 11 19:32 vmware-tools -> ../../vmware-tools/services.sh
lrwxrwxrwx.  1 1000 1000    40 Mar  5  2015 vxpbx_exchanged -> ../../../opt/VRTSpbx/bin/vxpbx_exchanged
-rwxr-xr-x.  1 1000 1000  1598 Oct  9  2019 winbind
-rwxr-xr-x.  1 1000 1000  1914 Oct 18  2017 wpa_supplicant
-rwxr-xr-x.  1 1000 1000  3555 Dec 16  2015 xinetd

/etc/sysconfig:
total 96
drwxr-xr-x.  7 0 0 4096 Jul  6 23:41 .
drwxr-xr-x. 77 0 0 8192 Jul 13 03:55 ..
drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq
drwxr-xr-x.  2 0 0    6 Sep 16  2015 console
-rw-------.  1 0 0 1390 Mar  4  2014 ebtables-config
-rw-r--r--.  1 0 0   72 Sep 15  2015 firewalld
lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub

/etc/rc.d/rc3.d:
total 4
drwxr-xr-x.  2 0 0   58 Jul  6 23:32 .
drwxr-xr-x. 10 0 0 4096 Sep 16  2015 ..
lrwxrwxrwx.  1 0 0   20 Jul  6 23:32 K50netconsole -> ../init.d/netconsole
lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 S10network -> ../init.d/network
lrwxrwxrwx.  1 0 0   15 Jul  6 23:32 S97rhnsd -> ../init.d/rhnsd
"""


def test_ls_etc():
    list_etc = ls_etc.LsEtc(context_wrap(LS_ETC))
    assert "/etc/rc.d/init.d" in list_etc
    assert "/etc/sysconfig" in list_etc
    assert 'vmware-tools' in list_etc.files_of("/etc/rc.d/init.d")
    assert len(list_etc.files_of("/etc/rc.d/init.d")) == 80
    assert len(list_etc.files_of("/etc/sysconfig")) == 3
    assert list_etc.files_of("/etc/sysconfig") == ['ebtables-config', 'firewalld', 'grub']
    assert list_etc.dirs_of("/etc/sysconfig") == ['.', '..', 'cbq', 'console']
    assert list_etc.specials_of("/etc/sysconfig") == []
    assert list_etc.total_of("/etc/sysconfig") == 96
    grub = list_etc.dir_entry("/etc/sysconfig", "grub")
    assert grub is not None
    assert grub == {
        'group': '0',
        'name': 'grub',
        'links': 1,
        'perms': 'rwxrwxrwx.',
        'raw_entry': 'lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub',
        'owner': '0',
        'link': '/etc/default/grub',
        'date': 'Jul  6 23:32',
        'type': 'l',
        'size': 17,
        'dir': '/etc/sysconfig'}
    assert list_etc.files_of("/etc/rc.d/rc3.d") == ['K50netconsole',
                                                  'S10network', 'S97rhnsd']


def test_ls_etc_documentation():
    failed_count, tests = doctest.testmod(
        ls_etc,
        globs={'ls_etc': ls_etc.LsEtc(context_wrap(LS_ETC))}
    )
    assert failed_count == 0
