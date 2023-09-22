import doctest

from insights.parsers import ls_systemd_units
from insights.parsers.ls_systemd_units import LsSystemdUnits
from insights.tests import context_wrap

# deliberately full output
LS_OUTPUT_FULL = """
/etc/systemd:
total 40
drwxr-xr-x.  4 0 0  150 Apr  4  2019 .
drwxr-xr-x. 88 0 0 8192 Jun 28 06:56 ..
-rw-r--r--.  1 0 0  615 Jun 22  2018 coredump.conf
-rw-r--r--.  1 0 0 1027 Jun 22  2018 journald.conf
-rw-r--r--.  1 0 0 1052 Apr  4  2019 logind.conf
-rw-r--r--.  1 0 0  631 Feb 26  2019 resolved.conf
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 system
-rw-r--r--.  1 0 0 1682 Feb 26  2019 system.conf
drwxr-xr-x.  2 0 0    6 Feb 26  2019 user
-rw-r--r--.  1 0 0 1130 Jun 22  2018 user.conf

/etc/systemd/system:
total 28
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 .
drwxr-xr-x.  4 0 0  150 Apr  4  2019 ..
drwxr-xr-x.  2 0 0   31 Apr  4  2019 basic.target.wants
-rw-r--r--.  1 0 0 1341 Feb  8  2019 dbus-org.freedesktop.NetworkManager.service
-rw-r--r--.  1 0 0  353 Feb  8  2019 dbus-org.freedesktop.nm-dispatcher.service
-rw-r--r--.  1 0 0  238 Nov  7  2017 dbus-org.freedesktop.timedate1.service
-rw-r--r--.  1 0 0  532 Jun 22  2018 default.target
drwxr-xr-x.  2 0 0   32 Apr  4  2019 getty.target.wants
drwxr-xr-x.  2 0 0 4096 Apr  4  2019 multi-user.target.wants
drwxr-xr-x.  2 0 0   48 Apr  4  2019 network-online.target.wants
drwxr-xr-x.  2 0 0   33 Apr  4  2019 nfs-blkmap.service.requires
drwxr-xr-x.  2 0 0   33 Apr  4  2019 nfs-idmapd.service.requires
drwxr-xr-x.  2 0 0   33 Apr  4  2019 nfs-mountd.service.requires
drwxr-xr-x.  2 0 0   33 Apr  4  2019 nfs-server.service.requires
drwxr-xr-x.  2 0 0   31 Apr  4  2019 remote-fs.target.wants
drwxr-xr-x.  2 0 0   33 Apr  4  2019 rpc-gssd.service.requires
drwxr-xr-x.  2 0 0   33 Apr  4  2019 rpc-statd-notify.service.requires
drwxr-xr-x.  2 0 0   33 Apr  4  2019 rpc-statd.service.requires
drwxr-xr-x.  2 0 0   51 Apr  4  2019 sockets.target.wants
drwxr-xr-x.  2 0 0  151 Apr  4  2019 sysinit.target.wants
-rw-r--r--.  1 0 0  583 Dec 17  2018 syslog.service
crw-rw-rw-.  1 0 0 1, 3 Jun 28 06:56 systemd-timedated.service
drwxr-xr-x.  2 0 0   34 Apr  4  2019 timers.target.wants

/etc/systemd/system/basic.target.wants:
total 8
drwxr-xr-x.  2 0 0   31 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  284 Nov  6  2018 microcode.service

/etc/systemd/system/getty.target.wants:
total 8
drwxr-xr-x.  2 0 0   32 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0 1975 Feb 26  2019 getty@tty1.service

/etc/systemd/system/multi-user.target.wants:
total 80
drwxr-xr-x.  2 0 0 4096 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0 1516 Jan  9  2019 auditd.service
-rw-r--r--.  1 0 0  495 Aug 13  2018 chronyd.service
-rw-r--r--.  1 0 0  491 Jan 23  2019 cloud-config.service
-rw-r--r--.  1 0 0  514 Jan 23  2019 cloud-final.service
-rw-r--r--.  1 0 0  878 Jan 23  2019 cloud-init-local.service
-rw-r--r--.  1 0 0  648 Jan 23  2019 cloud-init.service
-rw-r--r--.  1 0 0  322 Oct  2  2018 crond.service
-rw-r--r--.  1 0 0  301 Jan  4  2019 dnf-makecache.timer
-rw-r--r--.  1 0 0  224 Nov  6  2018 irqbalance.service
-rw-r--r--.  1 0 0  349 Feb 22  2019 kdump.service
-rw-r--r--.  1 0 0 1341 Feb  8  2019 NetworkManager.service
-rw-r--r--.  1 0 0  413 Feb 15  2019 nfs-client.target
-rw-r--r--.  1 0 0  522 Jun 22  2018 remote-fs.target
-rw-r--r--.  1 0 0  547 Oct 20  2018 rpcbind.service
-rw-r--r--.  1 0 0  583 Dec 17  2018 rsyslog.service
-rw-r--r--.  1 0 0  456 Nov 26  2018 sshd.service
-rw-r--r--.  1 0 0  420 Feb 11  2019 sssd.service
-rw-r--r--.  1 0 0  376 Jul  4  2018 tuned.service

/etc/systemd/system/network-online.target.wants:
total 8
drwxr-xr-x.  2 0 0   48 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  302 Feb  8  2019 NetworkManager-wait-online.service

/etc/systemd/system/nfs-blkmap.service.requires:
total 8
drwxr-xr-x.  2 0 0   33 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  608 Feb 15  2019 nfs-convert.service

/etc/systemd/system/nfs-idmapd.service.requires:
total 8
drwxr-xr-x.  2 0 0   33 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  608 Feb 15  2019 nfs-convert.service

/etc/systemd/system/nfs-mountd.service.requires:
total 8
drwxr-xr-x.  2 0 0   33 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  608 Feb 15  2019 nfs-convert.service

/etc/systemd/system/nfs-server.service.requires:
total 8
drwxr-xr-x.  2 0 0   33 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  608 Feb 15  2019 nfs-convert.service

/etc/systemd/system/remote-fs.target.wants:
total 8
drwxr-xr-x.  2 0 0   31 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  413 Feb 15  2019 nfs-client.target

/etc/systemd/system/rpc-gssd.service.requires:
total 8
drwxr-xr-x.  2 0 0   33 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  608 Feb 15  2019 nfs-convert.service

/etc/systemd/system/rpc-statd-notify.service.requires:
total 8
drwxr-xr-x.  2 0 0   33 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  608 Feb 15  2019 nfs-convert.service

/etc/systemd/system/rpc-statd.service.requires:
total 8
drwxr-xr-x.  2 0 0   33 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  608 Feb 15  2019 nfs-convert.service

/etc/systemd/system/sockets.target.wants:
total 12
drwxr-xr-x.  2 0 0   51 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  368 Oct 20  2018 rpcbind.socket
-rw-r--r--.  1 0 0  187 Feb 11  2019 sssd-kcm.socket

/etc/systemd/system/sysinit.target.wants:
total 24
drwxr-xr-x.  2 0 0  151 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  441 Aug  3  2018 import-state.service
-rw-r--r--.  1 0 0  355 Aug  3  2018 loadmodules.service
-rw-r--r--.  1 0 0  378 Aug 12  2018 nis-domainname.service
-rw-r--r--.  1 0 0  126 Dec 21  2018 rngd.service
-rw-r--r--.  1 0 0  406 Dec 14  2018 selinux-autorelabel-mark.service

/etc/systemd/system/timers.target.wants:
total 8
drwxr-xr-x.  2 0 0   34 Apr  4  2019 .
drwxr-xr-x. 17 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  346 Aug 12  2018 unbound-anchor.timer

/etc/systemd/user:
total 0
drwxr-xr-x. 2 0 0   6 Feb 26  2019 .
drwxr-xr-x. 4 0 0 150 Apr  4  2019 ..

/run/systemd:
total 0
drwxr-xr-x. 16 0 0  420 Jun 28 07:38 .
drwxr-xr-x. 27 0 0  820 Jun 28 06:56 ..
drwxr-xr-x.  2 0 0   40 Jun 28 06:56 ask-password
srwx------.  1 0 0    0 Jun 28 06:56 cgroups-agent
srw-------.  1 0 0    0 Jun 28 06:56 coredump
drwxr-xr-x.  4 0 0  100 Jun 28 06:56 generator
d---------.  3 0 0  160 Jun 28 06:56 inaccessible
drwxr-xr-x.  2 0 0   80 Jun 28 06:56 inhibit
drwxr-xr-x.  3 0 0  160 Jun 28 06:56 journal
drwxr-xr-x.  2 0 0   40 Jun 28 06:56 machines
srwxrwxrwx.  1 0 0    0 Jun 28 06:56 notify
srwxrwxrwx.  1 0 0    0 Jun 28 06:56 private
drwxr-xr-x.  2 0 0   60 Jun 28 06:56 seats
drwxr-xr-x.  2 0 0   80 Jun 28 09:44 sessions
-rw-r--r--.  1 0 0    0 Jun 28 06:56 show-status
drwxr-xr-x.  2 0 0   40 Jun 28 06:56 shutdown
drwxr-xr-x.  2 0 0   40 Jun 28 06:56 system
drwxr-xr-x.  2 0 0   60 Jun 28 09:44 transient
drwx------.  2 0 0   40 Jun 28 06:56 unit-root
drwxr-xr-x.  2 0 0 1100 Jun 28 09:44 units
drwxr-xr-x.  2 0 0   60 Jun 28 09:44 users

/run/systemd/ask-password:
total 0
drwxr-xr-x.  2 0 0  40 Jun 28 06:56 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..

/run/systemd/generator:
total 4
drwxr-xr-x.  4 0 0 100 Jun 28 06:56 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..
drwxr-xr-x.  2 0 0  60 Jun 28 06:56 getty.target.wants
drwxr-xr-x.  2 0 0  60 Jun 28 06:56 local-fs.target.requires
-rw-r--r--.  1 0 0 250 Jun 28 06:56 -.mount

/run/systemd/generator/getty.target.wants:
total 4
drwxr-xr-x. 2 0 0   60 Jun 28 06:56 .
drwxr-xr-x. 4 0 0  100 Jun 28 06:56 ..
-rw-r--r--. 1 0 0 1486 Feb 26  2019 serial-getty@ttyS0.service

/run/systemd/generator/local-fs.target.requires:
total 4
drwxr-xr-x. 2 0 0  60 Jun 28 06:56 .
drwxr-xr-x. 4 0 0 100 Jun 28 06:56 ..
-rw-r--r--. 1 0 0 250 Jun 28 06:56 -.mount

/run/systemd/inhibit:
total 4
drwxr-xr-x.  2 0 0  80 Jun 28 06:56 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..
-rw-r--r--.  1 0 0 171 Jun 28 06:56 1
prw-------.  1 0 0   0 Jun 28 06:56 1.ref

/run/systemd/journal:
total 4
drwxr-xr-x.  3 0 0 160 Jun 28 06:56 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..
srw-rw-rw-.  1 0 0   0 Jun 28 06:56 dev-log
-rw-r--r--.  1 0 0   0 Jun 28 06:56 flushed
-rw-r--r--.  1 0 0   8 Jun 28 06:56 kernel-seqnum
srw-rw-rw-.  1 0 0   0 Jun 28 06:56 socket
srw-rw-rw-.  1 0 0   0 Jun 28 06:56 stdout
drwxr-xr-x.  2 0 0 300 Jun 28 09:44 streams

/run/systemd/journal/streams:
total 52
drwxr-xr-x. 2 0 0 300 Jun 28 09:44 .
drwxr-xr-x. 3 0 0 160 Jun 28 06:56 ..
-rw-------. 1 0 0 206 Jun 28 06:56 9:18798
-rw-------. 1 0 0 218 Jun 28 06:56 9:19287
-rw-------. 1 0 0 207 Jun 28 06:56 9:19451
-rw-------. 1 0 0 200 Jun 28 06:56 9:19575
-rw-------. 1 0 0 212 Jun 28 06:56 9:19630
-rw-------. 1 0 0 200 Jun 28 06:56 9:19632
-rw-------. 1 0 0 208 Jun 28 06:56 9:19698
-rw-------. 1 0 0 220 Jun 28 06:56 9:20300
-rw-------. 1 0 0 220 Jun 28 06:56 9:21974
-rw-------. 1 0 0 202 Jun 28 06:56 9:22048
-rw-------. 1 0 0 202 Jun 28 06:56 9:24955
-rw-------. 1 0 0 200 Jun 28 06:56 9:25790
-rw-------. 1 0 0 185 Jun 28 09:44 9:32559

/run/systemd/machines:
total 0
drwxr-xr-x.  2 0 0  40 Jun 28 06:56 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..

/run/systemd/seats:
total 4
drwxr-xr-x.  2 0 0  60 Jun 28 06:56 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..
-rw-r--r--.  1 0 0  95 Jun 28 06:56 seat0

/run/systemd/sessions:
total 4
drwxr-xr-x.  2 0 0  80 Jun 28 09:44 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..
-rw-r--r--.  1 0 0 287 Jun 28 09:44 5
prw-------.  1 0 0   0 Jun 28 09:44 5.ref

/run/systemd/shutdown:
total 0
drwxr-xr-x.  2 0 0  40 Jun 28 06:56 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..

/run/systemd/system:
total 0
drwxr-xr-x.  2 0 0  40 Jun 28 06:56 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..

/run/systemd/transient:
total 4
drwxr-xr-x.  2 0 0  60 Jun 28 09:44 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..
-rw-r--r--.  1 0 0 278 Jun 28 09:44 session-5.scope

/run/systemd/units:
total 0
drwxr-xr-x.  2 0 0 1100 Jun 28 09:44 .
drwxr-xr-x. 16 0 0  420 Jun 28 07:38 ..
l??????????  ? ? ?    ?            ? invocation:auditd.service
l??????????  ? ? ?    ?            ? invocation:chronyd.service
l??????????  ? ? ?    ?            ? invocation:cloud-config.service
l??????????  ? ? ?    ?            ? invocation:cloud-final.service
l??????????  ? ? ?    ?            ? invocation:cloud-init-local.service
l??????????  ? ? ?    ?            ? invocation:cloud-init.service
l??????????  ? ? ?    ?            ? invocation:crond.service
l??????????  ? ? ?    ?            ? invocation:dbus.service
l??????????  ? ? ?    ?            ? invocation:dev-hugepages.mount
l??????????  ? ? ?    ?            ? invocation:dev-mqueue.mount
l??????????  ? ? ?    ?            ? invocation:dracut-shutdown.service
l??????????  ? ? ?    ?            ? invocation:getty@tty1.service
l??????????  ? ? ?    ?            ? invocation:gssproxy.service
l??????????  ? ? ?    ?            ? invocation:import-state.service
l??????????  ? ? ?    ?            ? invocation:irqbalance.service
l??????????  ? ? ?    ?            ? invocation:kdump.service
l??????????  ? ? ?    ?            ? invocation:kmod-static-nodes.service
l??????????  ? ? ?    ?            ? invocation:ldconfig.service
l??????????  ? ? ?    ?            ? invocation:NetworkManager.service
l??????????  ? ? ?    ?            ? invocation:NetworkManager-wait-online.service
l??????????  ? ? ?    ?            ? invocation:nis-domainname.service
l??????????  ? ? ?    ?            ? invocation:polkit.service
l??????????  ? ? ?    ?            ? invocation:rngd.service
l??????????  ? ? ?    ?            ? invocation:rpcbind.service
l??????????  ? ? ?    ?            ? invocation:rpc-statd-notify.service
l??????????  ? ? ?    ?            ? invocation:rsyslog.service
l??????????  ? ? ?    ?            ? invocation:serial-getty@ttyS0.service
l??????????  ? ? ?    ?            ? invocation:session-5.scope
l??????????  ? ? ?    ?            ? invocation:sshd.service
l??????????  ? ? ?    ?            ? invocation:sssd.service
l??????????  ? ? ?    ?            ? invocation:sys-kernel-config.mount
l??????????  ? ? ?    ?            ? invocation:sys-kernel-debug.mount
l??????????  ? ? ?    ?            ? invocation:systemd-hwdb-update.service
l??????????  ? ? ?    ?            ? invocation:systemd-journal-catalog-update.service
l??????????  ? ? ?    ?            ? invocation:systemd-journald.service
l??????????  ? ? ?    ?            ? invocation:systemd-journal-flush.service
l??????????  ? ? ?    ?            ? invocation:systemd-logind.service
l??????????  ? ? ?    ?            ? invocation:systemd-machine-id-commit.service
l??????????  ? ? ?    ?            ? invocation:systemd-random-seed.service
l??????????  ? ? ?    ?            ? invocation:systemd-remount-fs.service
l??????????  ? ? ?    ?            ? invocation:systemd-sysctl.service
l??????????  ? ? ?    ?            ? invocation:systemd-sysusers.service
l??????????  ? ? ?    ?            ? invocation:systemd-tmpfiles-setup-dev.service
l??????????  ? ? ?    ?            ? invocation:systemd-tmpfiles-setup.service
l??????????  ? ? ?    ?            ? invocation:systemd-udevd.service
l??????????  ? ? ?    ?            ? invocation:systemd-udev-trigger.service
l??????????  ? ? ?    ?            ? invocation:systemd-update-done.service
l??????????  ? ? ?    ?            ? invocation:systemd-update-utmp.service
l??????????  ? ? ?    ?            ? invocation:systemd-user-sessions.service
l??????????  ? ? ?    ?            ? invocation:tuned.service
l??????????  ? ? ?    ?            ? invocation:user@1000.service
l??????????  ? ? ?    ?            ? invocation:user-runtime-dir@1000.service
l??????????  ? ? ?    ?            ? invocation:var-lib-nfs-rpc_pipefs.mount

/run/systemd/users:
total 4
drwxr-xr-x.  2 0 0  60 Jun 28 09:44 .
drwxr-xr-x. 16 0 0 420 Jun 28 07:38 ..
-rw-r--r--.  1 0 0 230 Jun 28 09:44 1000

/usr/lib/systemd:
total 10000
drwxr-xr-x. 16 0 0    4096 Apr  4  2019 .
dr-xr-xr-x. 31 0 0    4096 Apr  4  2019 ..
drwxr-xr-x.  3 0 0      17 Apr  4  2019 boot
drwxr-xr-x.  2 0 0    4096 Apr  4  2019 catalog
-rwxr-xr-x.  1 0 0 4652600 Feb 26  2019 libsystemd-shared-239.so
drwxr-xr-x.  2 0 0      29 Apr  4  2019 network
drwxr-xr-x.  2 0 0      29 Apr  4  2019 ntp-units.d
drwxr-xr-x.  3 0 0      21 Apr  4  2019 portable
-rwxr-xr-x.  1 0 0   46000 Feb 26  2019 portablectl
-rwxr-xr-x.  1 0 0    2351 Feb 26  2019 purge-nobody-user
-rw-r--r--.  1 0 0     678 Jun 22  2018 resolv.conf
drwxr-xr-x. 23 0 0   12288 Apr  4  2019 system
-rwxr-xr-x.  1 0 0 2336312 Feb 26  2019 systemd
-rwxr-xr-x.  1 0 0   13024 Feb 26  2019 systemd-ac-power
-rwxr-xr-x.  1 0 0   23200 Feb 26  2019 systemd-backlight
-rwxr-xr-x.  1 0 0   17952 Feb 26  2019 systemd-binfmt
-rwxr-xr-x.  1 0 0   13264 Feb 26  2019 systemd-cgroups-agent
-rwxr-xr-x.  1 0 0   73640 Feb 26  2019 systemd-coredump
-rwxr-xr-x.  1 0 0   30840 Feb 26  2019 systemd-cryptsetup
-rwxr-xr-x.  1 0 0   17368 Feb 26  2019 systemd-dissect
-rwxr-xr-x.  1 0 0   56624 Feb 26  2019 systemd-export
-rwxr-xr-x.  1 0 0   26728 Feb 26  2019 systemd-fsck
-rwxr-xr-x.  1 0 0   22040 Feb 26  2019 systemd-growfs
-rwxr-xr-x.  1 0 0   13264 Feb 26  2019 systemd-hibernate-resume
-rwxr-xr-x.  1 0 0   36704 Feb 26  2019 systemd-hostnamed
-rwxr-xr-x.  1 0 0   22592 Feb 26  2019 systemd-initctl
-rwxr-xr-x.  1 0 0  211568 Feb 26  2019 systemd-journald
-rwxr-xr-x.  1 0 0   61992 Feb 26  2019 systemd-localed
-rwxr-xr-x.  1 0 0  435880 Feb 26  2019 systemd-logind
-rwxr-xr-x.  1 0 0   13824 Feb 26  2019 systemd-makefs
-rwxr-xr-x.  1 0 0   23808 Feb 26  2019 systemd-modules-load
-rwxr-xr-x.  1 0 0  131592 Feb 26  2019 systemd-portabled
-rwxr-xr-x.  1 0 0   13624 Feb 26  2019 systemd-quotacheck
-rwxr-xr-x.  1 0 0   17360 Feb 26  2019 systemd-random-seed
-rwxr-xr-x.  1 0 0   19176 Feb 26  2019 systemd-remount-fs
-rwxr-xr-x.  1 0 0   13264 Feb 26  2019 systemd-reply-password
-rwxr-xr-x.  1 0 0  782824 Feb 26  2019 systemd-resolved
-rwxr-xr-x.  1 0 0   26736 Feb 26  2019 systemd-rfkill
-rwxr-xr-x.  1 0 0   67632 Feb 26  2019 systemd-shutdown
-rwxr-xr-x.  1 0 0   23208 Feb 26  2019 systemd-sleep
-rwxr-xr-x.  1 0 0   31880 Feb 26  2019 systemd-socket-proxyd
-rwxr-xr-x.  1 0 0   13272 Feb 26  2019 systemd-sulogin-shell
-rwxr-xr-x.  1 0 0   17952 Feb 26  2019 systemd-sysctl
-rwxr-xr-x.  1 0 0   46864 Sep 10  2018 systemd-sysv-install
-rwxr-xr-x.  1 0 0   47064 Feb 26  2019 systemd-timedated
-rwxr-xr-x.  1 0 0  524608 Feb 26  2019 systemd-udevd
-rwxr-xr-x.  1 0 0   13832 Feb 26  2019 systemd-update-done
-rwxr-xr-x.  1 0 0   17368 Feb 26  2019 systemd-update-utmp
-rwxr-xr-x.  1 0 0   74120 Feb 26  2019 systemd-user-runtime-dir
-rwxr-xr-x.  1 0 0   13040 Feb 26  2019 systemd-user-sessions
-rwxr-xr-x.  1 0 0   23192 Feb 26  2019 systemd-vconsole-setup
-rwxr-xr-x.  1 0 0   13256 Feb 26  2019 systemd-veritysetup
-rwxr-xr-x.  1 0 0   13264 Feb 26  2019 systemd-volatile-root
drwxr-xr-x.  2 0 0    4096 Apr  4  2019 system-generators
drwxr-xr-x.  2 0 0     122 Apr  4  2019 system-preset
drwxr-xr-x.  2 0 0       6 Feb 26  2019 system-shutdown
drwxr-xr-x.  2 0 0       6 Feb 26  2019 system-sleep
drwxr-xr-x.  4 0 0    4096 Apr  4  2019 user
drwxr-xr-x.  2 0 0      48 Apr  4  2019 user-environment-generators
drwxr-xr-x.  2 0 0       6 Feb 26  2019 user-generators
drwxr-xr-x.  2 0 0      31 Apr  4  2019 user-preset

/usr/lib/systemd/boot:
total 4
drwxr-xr-x.  3 0 0   17 Apr  4  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..
drwxr-xr-x.  2 0 0   58 Apr  4  2019 efi

/usr/lib/systemd/boot/efi:
total 148
drwxr-xr-x. 2 0 0    58 Apr  4  2019 .
drwxr-xr-x. 3 0 0    17 Apr  4  2019 ..
-rwxr-xr-x. 1 0 0 59770 Feb 26  2019 linuxx64.efi.stub
-rwxr-xr-x. 1 0 0 87426 Feb 26  2019 systemd-bootx64.efi

/usr/lib/systemd/catalog:
total 164
drwxr-xr-x.  2 0 0  4096 Apr  4  2019 .
drwxr-xr-x. 16 0 0  4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0 13109 Feb 26  2019 systemd.be.catalog
-rw-r--r--.  1 0 0 10118 Feb 26  2019 systemd.be@latin.catalog
-rw-r--r--.  1 0 0 14295 Feb 26  2019 systemd.bg.catalog
-rw-r--r--.  1 0 0 12454 Feb 26  2019 systemd.catalog
-rw-r--r--.  1 0 0   475 Feb 26  2019 systemd.de.catalog
-rw-r--r--.  1 0 0 13358 Feb 26  2019 systemd.fr.catalog
-rw-r--r--.  1 0 0 11351 Feb 26  2019 systemd.it.catalog
-rw-r--r--.  1 0 0 13049 Feb 26  2019 systemd.pl.catalog
-rw-r--r--.  1 0 0  8376 Feb 26  2019 systemd.pt_BR.catalog
-rw-r--r--.  1 0 0 20471 Feb 26  2019 systemd.ru.catalog
-rw-r--r--.  1 0 0  7360 Feb 26  2019 systemd.zh_CN.catalog
-rw-r--r--.  1 0 0  7319 Feb 26  2019 systemd.zh_TW.catalog

/usr/lib/systemd/network:
total 8
drwxr-xr-x.  2 0 0   29 Apr  4  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  412 Jun 22  2018 99-default.link

/usr/lib/systemd/ntp-units.d:
total 8
drwxr-xr-x.  2 0 0   29 Apr  4  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0   16 Aug 13  2018 50-chronyd.list

/usr/lib/systemd/portable:
total 4
drwxr-xr-x.  3 0 0   21 Apr  4  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..
drwxr-xr-x.  6 0 0   67 Apr  4  2019 profile

/usr/lib/systemd/portable/profile:
total 0
drwxr-xr-x. 6 0 0 67 Apr  4  2019 .
drwxr-xr-x. 3 0 0 21 Apr  4  2019 ..
drwxr-xr-x. 2 0 0 26 Apr  4  2019 default
drwxr-xr-x. 2 0 0 26 Apr  4  2019 nonetwork
drwxr-xr-x. 2 0 0 26 Apr  4  2019 strict
drwxr-xr-x. 2 0 0 26 Apr  4  2019 trusted

/usr/lib/systemd/portable/profile/default:
total 4
drwxr-xr-x. 2 0 0   26 Apr  4  2019 .
drwxr-xr-x. 6 0 0   67 Apr  4  2019 ..
-rw-r--r--. 1 0 0 1101 Jun 22  2018 service.conf

/usr/lib/systemd/portable/profile/nonetwork:
total 4
drwxr-xr-x. 2 0 0   26 Apr  4  2019 .
drwxr-xr-x. 6 0 0   67 Apr  4  2019 ..
-rw-r--r--. 1 0 0 1038 Jun 22  2018 service.conf

/usr/lib/systemd/portable/profile/strict:
total 4
drwxr-xr-x. 2 0 0  26 Apr  4  2019 .
drwxr-xr-x. 6 0 0  67 Apr  4  2019 ..
-rw-r--r--. 1 0 0 775 Jun 22  2018 service.conf

/usr/lib/systemd/portable/profile/trusted:
total 4
drwxr-xr-x. 2 0 0  26 Apr  4  2019 .
drwxr-xr-x. 6 0 0  67 Apr  4  2019 ..
-rw-r--r--. 1 0 0 182 Jun 22  2018 service.conf

/usr/lib/systemd/system:
total 1044
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 .
drwxr-xr-x. 16 0 0  4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0   275 Sep 26  2018 arp-ethers.service
-rw-r--r--.  1 0 0  1516 Jan  9  2019 auditd.service
-rw-r--r--.  1 0 0   628 Feb 15  2019 auth-rpcgss-module.service
-rw-r--r--.  1 0 0  1975 Feb 26  2019 autovt@.service
-rw-r--r--.  1 0 0   956 Feb 26  2019 basic.target
drwxr-xr-x.  2 0 0     6 Feb 26  2019 basic.target.wants
-rw-r--r--.  1 0 0   419 Jun 22  2018 bluetooth.target
-rw-r--r--.  1 0 0   209 Aug 13  2018 chrony-dnssrv@.service
-rw-r--r--.  1 0 0   138 Aug 13  2018 chrony-dnssrv@.timer
-rw-r--r--.  1 0 0   495 Aug 13  2018 chronyd.service
-rw-r--r--.  1 0 0   472 Apr  4  2018 chrony-wait.service
-rw-r--r--.  1 0 0   491 Jan 23  2019 cloud-config.service
-rw-r--r--.  1 0 0   536 Jan 23  2019 cloud-config.target
-rw-r--r--.  1 0 0   514 Jan 23  2019 cloud-final.service
-rw-r--r--.  1 0 0   878 Jan 23  2019 cloud-init-local.service
-rw-r--r--.  1 0 0   648 Jan 23  2019 cloud-init.service
-rw-r--r--.  1 0 0   222 Feb  8  2019 cockpit-motd.service
-rw-r--r--.  1 0 0   305 Feb  8  2019 cockpit.service
-rw-r--r--.  1 0 0   373 Feb  8  2019 cockpit.socket
-rw-r--r--.  1 0 0  1082 Feb 26  2019 console-getty.service
-rw-r--r--.  1 0 0  1263 Feb 26  2019 container-getty@.service
-rw-r--r--.  1 0 0   294 Mar 13  2019 cpupower.service
-rw-r--r--.  1 0 0   322 Oct  2  2018 crond.service
-rw-r--r--.  1 0 0   465 Jun 22  2018 cryptsetup-pre.target
-rw-r--r--.  1 0 0   412 Jun 22  2018 cryptsetup.target
-rw-r--r--.  1 0 0   583 Jun 22  2018 ctrl-alt-del.target
-rw-r--r--.  1 0 0  1081 Feb 26  2019 dbus-org.freedesktop.hostname1.service
-rw-r--r--.  1 0 0  1050 Feb 26  2019 dbus-org.freedesktop.locale1.service
-rw-r--r--.  1 0 0  1362 Feb 26  2019 dbus-org.freedesktop.login1.service
-rw-r--r--.  1 0 0   987 Feb 26  2019 dbus-org.freedesktop.portable1.service
-rw-r--r--.  1 0 0  1021 Feb 26  2019 dbus-org.freedesktop.timedate1.service
-rw-r--r--.  1 0 0   380 Oct 24  2018 dbus.service
-rw-r--r--.  1 0 0   102 Oct 24  2018 dbus.socket
drwxr-xr-x.  2 0 0     6 Feb 26  2019 dbus.target.wants
-rw-r--r--.  1 0 0  1084 Feb 26  2019 debug-shell.service
-rw-r--r--.  1 0 0   598 Jun 22  2018 default.target
drwxr-xr-x.  2 0 0     6 Feb 26  2019 default.target.wants
-rw-r--r--.  1 0 0   750 Jun 22  2018 dev-hugepages.mount
-rw-r--r--.  1 0 0   665 Jun 22  2018 dev-mqueue.mount
-rw-r--r--.  1 0 0   457 Jan  4  2019 dnf-makecache.service
-rw-r--r--.  1 0 0   301 Jan  4  2019 dnf-makecache.timer
-rw-r--r--.  1 0 0   904 Oct  8  2018 dracut-cmdline.service
-rw-r--r--.  1 0 0   821 Oct  8  2018 dracut-initqueue.service
-rw-r--r--.  1 0 0   793 Oct  8  2018 dracut-mount.service
-rw-r--r--.  1 0 0   822 Oct  8  2018 dracut-pre-mount.service
-rw-r--r--.  1 0 0  1125 Oct  8  2018 dracut-pre-pivot.service
-rw-r--r--.  1 0 0   914 Oct  8  2018 dracut-pre-trigger.service
-rw-r--r--.  1 0 0   993 Oct  8  2018 dracut-pre-udev.service
-rw-r--r--.  1 0 0   459 Oct  8  2018 dracut-shutdown.service
-rw-r--r--.  1 0 0   801 Feb 26  2019 emergency.service
-rw-r--r--.  1 0 0   471 Jun 22  2018 emergency.target
-rw-r--r--.  1 0 0   541 Jun 22  2018 exit.target
-rw-r--r--.  1 0 0   480 Jun 22  2018 final.target
-rw-r--r--.  1 0 0    96 Dec 11  2018 fstrim.service
-rw-r--r--.  1 0 0   170 Dec 11  2018 fstrim.timer
-rw-r--r--.  1 0 0   506 Jun 22  2018 getty-pre.target
-rw-r--r--.  1 0 0  1975 Feb 26  2019 getty@.service
-rw-r--r--.  1 0 0   500 Jun 22  2018 getty.target
-rw-r--r--.  1 0 0   598 Jun 22  2018 graphical.target
drwxr-xr-x.  2 0 0    50 Apr  4  2019 graphical.target.wants
-rw-r--r--.  1 0 0   263 Dec 19  2018 grub-boot-indeterminate.service
-rw-r--r--.  1 0 0   479 Aug 12  2018 gssproxy.service
-rw-r--r--.  1 0 0   605 Feb 26  2019 halt-local.service
-rw-r--r--.  1 0 0   527 Jun 22  2018 halt.target
-rw-r--r--.  1 0 0   509 Jun 22  2018 hibernate.target
-rw-r--r--.  1 0 0   530 Jun 22  2018 hybrid-sleep.target
-rw-r--r--.  1 0 0   441 Aug  3  2018 import-state.service
-rw-r--r--.  1 0 0   674 Feb 26  2019 initrd-cleanup.service
-rw-r--r--.  1 0 0   593 Jun 22  2018 initrd-fs.target
-rw-r--r--.  1 0 0   842 Feb 26  2019 initrd-parse-etc.service
-rw-r--r--.  1 0 0   561 Jun 22  2018 initrd-root-device.target
-rw-r--r--.  1 0 0   566 Jun 22  2018 initrd-root-fs.target
-rw-r--r--.  1 0 0   593 Feb 26  2019 initrd-switch-root.service
-rw-r--r--.  1 0 0   754 Jun 22  2018 initrd-switch-root.target
-rw-r--r--.  1 0 0   763 Jun 22  2018 initrd.target
drwxr-xr-x.  2 0 0   225 Apr  4  2019 initrd.target.wants
-rw-r--r--.  1 0 0   708 Feb 26  2019 initrd-udevadm-cleanup-db.service
-rw-r--r--.  1 0 0   497 Apr 20  2018 insights-client.service
-rw-r--r--.  1 0 0   193 Apr 20  2018 insights-client.timer
-rw-r--r--.  1 0 0   224 Nov  6  2018 irqbalance.service
-rw-r--r--.  1 0 0   349 Feb 22  2019 kdump.service
-rw-r--r--.  1 0 0   541 Jun 22  2018 kexec.target
-rw-r--r--.  1 0 0   721 Feb 26  2019 kmod-static-nodes.service
-rw-r--r--.  1 0 0   687 Jun 22  2018 ldconfig.service
-rw-r--r--.  1 0 0   355 Aug  3  2018 loadmodules.service
-rw-r--r--.  1 0 0   435 Jun 22  2018 local-fs-pre.target
-rw-r--r--.  1 0 0   547 Jun 22  2018 local-fs.target
drwxr-xr-x.  2 0 0    40 Apr  4  2019 local-fs.target.wants
-rw-r--r--.  1 0 0   342 Nov  7  2018 man-db-cache-update.service
-rw-r--r--.  1 0 0   380 Oct 24  2018 messagebus.service
-rw-r--r--.  1 0 0   284 Nov  6  2018 microcode.service
-rw-r--r--.  1 0 0   532 Jun 22  2018 multi-user.target
drwxr-xr-x.  2 0 0   195 Apr  4  2019 multi-user.target.wants
-rw-r--r--.  1 0 0   353 Feb  8  2019 NetworkManager-dispatcher.service
-rw-r--r--.  1 0 0  1341 Feb  8  2019 NetworkManager.service
-rw-r--r--.  1 0 0   302 Feb  8  2019 NetworkManager-wait-online.service
-rw-r--r--.  1 0 0   505 Jun 22  2018 network-online.target
-rw-r--r--.  1 0 0   502 Jun 22  2018 network-pre.target
-rw-r--r--.  1 0 0   521 Jun 22  2018 network.target
-rw-r--r--.  1 0 0   295 Feb 15  2019 nfs-blkmap.service
-rw-r--r--.  1 0 0   413 Feb 15  2019 nfs-client.target
-rw-r--r--.  1 0 0   608 Feb 15  2019 nfs-convert.service
-rw-r--r--.  1 0 0   222 Feb 15  2019 nfs-idmapd.service
-rw-r--r--.  1 0 0   287 Feb 15  2019 nfs-mountd.service
-rw-r--r--.  1 0 0   931 Feb 15  2019 nfs-server.service
-rw-r--r--.  1 0 0   567 Feb 15  2019 nfs-utils.service
-rw-r--r--.  1 0 0   378 Aug 12  2018 nis-domainname.service
-rw-r--r--.  1 0 0   554 Jun 22  2018 nss-lookup.target
-rw-r--r--.  1 0 0   513 Jun 22  2018 nss-user-lookup.target
-rw-r--r--.  1 0 0   394 Jun 22  2018 paths.target
-rw-r--r--.  1 0 0   172 Jan 22  2019 polkit.service
-rw-r--r--.  1 0 0   592 Jun 22  2018 poweroff.target
-rw-r--r--.  1 0 0   417 Jun 22  2018 printer.target
-rw-r--r--.  1 0 0    98 Feb 15  2019 proc-fs-nfsd.mount
-rw-r--r--.  1 0 0   745 Jun 22  2018 proc-sys-fs-binfmt_misc.automount
-rw-r--r--.  1 0 0   655 Jun 22  2018 proc-sys-fs-binfmt_misc.mount
-rw-r--r--.  1 0 0   522 Feb 26  2019 qemu-guest-agent.service
-rw-r--r--.  1 0 0   617 Feb 26  2019 quotaon.service
-rw-r--r--.  1 0 0   736 Feb 26  2019 rc-local.service
-rw-r--r--.  1 0 0   208 Aug 12  2018 rdisc.service
-rw-r--r--.  1 0 0   583 Jun 22  2018 reboot.target
-rw-r--r--.  1 0 0   549 Jun 22  2018 remote-cryptsetup.target
-rw-r--r--.  1 0 0   436 Jun 22  2018 remote-fs-pre.target
-rw-r--r--.  1 0 0   522 Jun 22  2018 remote-fs.target
drwxr-xr-x.  2 0 0     6 Feb 26  2019 remote-fs.target.wants
-rw-r--r--.  1 0 0   792 Feb 26  2019 rescue.service
-rw-r--r--.  1 0 0   492 Jun 22  2018 rescue.target
drwxr-xr-x.  2 0 0    50 Apr  4  2019 rescue.target.wants
-rw-r--r--.  1 0 0   260 Feb  4  2019 rhnsd.service
-rw-r--r--.  1 0 0   184 Mar  6  2019 rhsmcertd.service
-rw-r--r--.  1 0 0   212 Mar  6  2019 rhsm-facts.service
-rw-r--r--.  1 0 0   187 Mar  6  2019 rhsm.service
-rw-r--r--.  1 0 0   126 Dec 21  2018 rngd.service
-rw-r--r--.  1 0 0   547 Oct 20  2018 rpcbind.service
-rw-r--r--.  1 0 0   368 Oct 20  2018 rpcbind.socket
-rw-r--r--.  1 0 0   540 Jun 22  2018 rpcbind.target
-rw-r--r--.  1 0 0   281 Feb 15  2019 rpc-gssd.service
-rw-r--r--.  1 0 0    80 Feb 15  2019 rpc_pipefs.target
-rw-r--r--.  1 0 0   387 Feb 15  2019 rpc-statd-notify.service
-rw-r--r--.  1 0 0   382 Feb 15  2019 rpc-statd.service
-rw-r--r--.  1 0 0   583 Dec 17  2018 rsyslog.service
-rw-r--r--.  1 0 0   592 Jun 22  2018 runlevel0.target
-rw-r--r--.  1 0 0   492 Jun 22  2018 runlevel1.target
drwxr-xr-x.  2 0 0     6 Feb 26  2019 runlevel1.target.wants
-rw-r--r--.  1 0 0   532 Jun 22  2018 runlevel2.target
drwxr-xr-x.  2 0 0     6 Feb 26  2019 runlevel2.target.wants
-rw-r--r--.  1 0 0   532 Jun 22  2018 runlevel3.target
drwxr-xr-x.  2 0 0     6 Feb 26  2019 runlevel3.target.wants
-rw-r--r--.  1 0 0   532 Jun 22  2018 runlevel4.target
drwxr-xr-x.  2 0 0     6 Feb 26  2019 runlevel4.target.wants
-rw-r--r--.  1 0 0   598 Jun 22  2018 runlevel5.target
drwxr-xr-x.  2 0 0     6 Feb 26  2019 runlevel5.target.wants
-rw-r--r--.  1 0 0   583 Jun 22  2018 runlevel6.target
-rw-r--r--.  1 0 0   406 Dec 14  2018 selinux-autorelabel-mark.service
-rw-r--r--.  1 0 0   288 Dec 14  2018 selinux-autorelabel.service
-rw-r--r--.  1 0 0   230 Dec 14  2018 selinux-autorelabel.target
-rw-r--r--.  1 0 0  1486 Feb 26  2019 serial-getty@.service
-rw-r--r--.  1 0 0   442 Jun 22  2018 shutdown.target
-rw-r--r--.  1 0 0   402 Jun 22  2018 sigpwr.target
-rw-r--r--.  1 0 0   460 Jun 22  2018 sleep.target
-rw-r--r--.  1 0 0   449 Jun 22  2018 slices.target
-rw-r--r--.  1 0 0   420 Jun 22  2018 smartcard.target
-rw-r--r--.  1 0 0   396 Jun 22  2018 sockets.target
drwxr-xr-x.  2 0 0   227 Apr  4  2019 sockets.target.wants
-rw-r--r--.  1 0 0   420 Jun 22  2018 sound.target
-rw-r--r--.  1 0 0   247 Nov 26  2018 sshd-keygen@.service
-rw-r--r--.  1 0 0   123 Nov 26  2018 sshd-keygen.target
-rw-r--r--.  1 0 0   456 Nov 26  2018 sshd.service
-rw-r--r--.  1 0 0   342 Nov 26  2018 sshd@.service
-rw-r--r--.  1 0 0   181 Nov 26  2018 sshd.socket
-rw-r--r--.  1 0 0   472 Feb 11  2019 sssd-autofs.service
-rw-r--r--.  1 0 0   371 Feb 11  2019 sssd-autofs.socket
-rw-r--r--.  1 0 0   327 Feb 11  2019 sssd-kcm.service
-rw-r--r--.  1 0 0   187 Feb 11  2019 sssd-kcm.socket
-rw-r--r--.  1 0 0   351 Feb 11  2019 sssd-nss.service
-rw-r--r--.  1 0 0   420 Feb 11  2019 sssd-nss.socket
-rw-r--r--.  1 0 0   460 Feb 11  2019 sssd-pac.service
-rw-r--r--.  1 0 0   362 Feb 11  2019 sssd-pac.socket
-rw-r--r--.  1 0 0   443 Feb 11  2019 sssd-pam-priv.socket
-rw-r--r--.  1 0 0   481 Feb 11  2019 sssd-pam.service
-rw-r--r--.  1 0 0   391 Feb 11  2019 sssd-pam.socket
-rw-r--r--.  1 0 0   420 Feb 11  2019 sssd.service
-rw-r--r--.  1 0 0   460 Feb 11  2019 sssd-ssh.service
-rw-r--r--.  1 0 0   362 Feb 11  2019 sssd-ssh.socket
-rw-r--r--.  1 0 0   465 Feb 11  2019 sssd-sudo.service
-rw-r--r--.  1 0 0   364 Feb 11  2019 sssd-sudo.socket
-rw-r--r--.  1 0 0   503 Jun 22  2018 suspend.target
-rw-r--r--.  1 0 0   577 Jun 22  2018 suspend-then-hibernate.target
-rw-r--r--.  1 0 0   393 Jun 22  2018 swap.target
-rw-r--r--.  1 0 0   795 Jun 22  2018 sys-fs-fuse-connections.mount
-rw-r--r--.  1 0 0   558 Jun 22  2018 sysinit.target
drwxr-xr-x.  2 0 0  4096 Apr  4  2019 sysinit.target.wants
-rw-r--r--.  1 0 0   767 Jun 22  2018 sys-kernel-config.mount
-rw-r--r--.  1 0 0   710 Jun 22  2018 sys-kernel-debug.mount
-rw-r--r--.  1 0 0  1407 Jun 22  2018 syslog.socket
drwxr-xr-x.  2 0 0     6 Feb 26  2019 syslog.target.wants
-rw-r--r--.  1 0 0   704 Jun 22  2018 systemd-ask-password-console.path
-rw-r--r--.  1 0 0   728 Feb 26  2019 systemd-ask-password-console.service
-rw-r--r--.  1 0 0   632 Jun 22  2018 systemd-ask-password-wall.path
-rw-r--r--.  1 0 0   760 Feb 26  2019 systemd-ask-password-wall.service
-rw-r--r--.  1 0 0   760 Feb 26  2019 systemd-backlight@.service
-rw-r--r--.  1 0 0  1093 Feb 26  2019 systemd-binfmt.service
-rw-r--r--.  1 0 0  1083 Feb 26  2019 systemd-coredump@.service
-rw-r--r--.  1 0 0   537 Jun 22  2018 systemd-coredump.socket
-rw-r--r--.  1 0 0   541 Feb 26  2019 systemd-exit.service
-rw-r--r--.  1 0 0   799 Feb 26  2019 systemd-firstboot.service
-rw-r--r--.  1 0 0   618 Feb 26  2019 systemd-fsck-root.service
-rw-r--r--.  1 0 0   671 Feb 26  2019 systemd-fsck@.service
-rw-r--r--.  1 0 0   588 Feb 26  2019 systemd-halt.service
-rw-r--r--.  1 0 0   675 Feb 26  2019 systemd-hibernate-resume@.service
-rw-r--r--.  1 0 0   545 Feb 26  2019 systemd-hibernate.service
-rw-r--r--.  1 0 0  1081 Feb 26  2019 systemd-hostnamed.service
-rw-r--r--.  1 0 0   826 Feb 26  2019 systemd-hwdb-update.service
-rw-r--r--.  1 0 0   563 Feb 26  2019 systemd-hybrid-sleep.service
-rw-r--r--.  1 0 0   550 Feb 26  2019 systemd-initctl.service
-rw-r--r--.  1 0 0   546 Jun 22  2018 systemd-initctl.socket
-rw-r--r--.  1 0 0   711 Feb 26  2019 systemd-journal-catalog-update.service
-rw-r--r--.  1 0 0  1130 Jun 22  2018 systemd-journald-dev-log.socket
-rw-r--r--.  1 0 0  1486 Feb 26  2019 systemd-journald.service
-rw-r--r--.  1 0 0   882 Jun 22  2018 systemd-journald.socket
-rw-r--r--.  1 0 0   775 Feb 26  2019 systemd-journal-flush.service
-rw-r--r--.  1 0 0   601 Feb 26  2019 systemd-kexec.service
-rw-r--r--.  1 0 0  1050 Feb 26  2019 systemd-localed.service
-rw-r--r--.  1 0 0  1362 Feb 26  2019 systemd-logind.service
-rw-r--r--.  1 0 0   737 Feb 26  2019 systemd-machine-id-commit.service
-rw-r--r--.  1 0 0  1011 Feb 26  2019 systemd-modules-load.service
-rw-r--r--.  1 0 0   987 Feb 26  2019 systemd-portabled.service
-rw-r--r--.  1 0 0   597 Feb 26  2019 systemd-poweroff.service
-rw-r--r--.  1 0 0   663 Feb 26  2019 systemd-quotacheck.service
-rw-r--r--.  1 0 0   800 Feb 26  2019 systemd-random-seed.service
-rw-r--r--.  1 0 0   592 Feb 26  2019 systemd-reboot.service
-rw-r--r--.  1 0 0   802 Feb 26  2019 systemd-remount-fs.service
-rw-r--r--.  1 0 0  1611 Feb 26  2019 systemd-resolved.service
-rw-r--r--.  1 0 0   728 Feb 26  2019 systemd-rfkill.service
-rw-r--r--.  1 0 0   657 Jun 22  2018 systemd-rfkill.socket
-rw-r--r--.  1 0 0   541 Feb 26  2019 systemd-suspend.service
-rw-r--r--.  1 0 0   600 Feb 26  2019 systemd-suspend-then-hibernate.service
-rw-r--r--.  1 0 0   697 Feb 26  2019 systemd-sysctl.service
-rw-r--r--.  1 0 0   704 Feb 26  2019 systemd-sysusers.service
-rw-r--r--.  1 0 0  1021 Feb 26  2019 systemd-timedated.service
-rw-r--r--.  1 0 0   663 Feb 26  2019 systemd-tmpfiles-clean.service
-rw-r--r--.  1 0 0   490 Jun 22  2018 systemd-tmpfiles-clean.timer
-rw-r--r--.  1 0 0   771 Feb 26  2019 systemd-tmpfiles-setup-dev.service
-rw-r--r--.  1 0 0   751 Feb 26  2019 systemd-tmpfiles-setup.service
-rw-r--r--.  1 0 0   635 Jun 22  2018 systemd-udevd-control.socket
-rw-r--r--.  1 0 0   610 Jun 22  2018 systemd-udevd-kernel.socket
-rw-r--r--.  1 0 0  1049 Feb 26  2019 systemd-udevd.service
-rw-r--r--.  1 0 0   867 Feb 26  2019 systemd-udev-settle.service
-rw-r--r--.  1 0 0   771 Feb 26  2019 systemd-udev-trigger.service
drwxr-xr-x.  2 0 0    49 Apr  4  2019 systemd-udev-trigger.service.d
-rw-r--r--.  1 0 0   674 Feb 26  2019 systemd-update-done.service
-rw-r--r--.  1 0 0   801 Feb 26  2019 systemd-update-utmp-runlevel.service
-rw-r--r--.  1 0 0   802 Feb 26  2019 systemd-update-utmp.service
-rw-r--r--.  1 0 0   636 Feb 26  2019 systemd-user-sessions.service
-rw-r--r--.  1 0 0   622 Feb 26  2019 systemd-vconsole-setup.service
-rw-r--r--.  1 0 0   694 Feb 26  2019 systemd-volatile-root.service
-rw-r--r--.  1 0 0  1415 Jun 22  2018 system-update-cleanup.service
-rw-r--r--.  1 0 0   543 Jun 22  2018 system-update-pre.target
-rw-r--r--.  1 0 0   617 Jun 22  2018 system-update.target
drwxr-xr-x.  2 0 0    45 Apr  4  2019 system-update.target.wants
-rw-r--r--.  1 0 0   128 Aug 12  2018 tcsd.service
-rw-r--r--.  1 0 0   244 Mar 17  2017 teamd@.service
-rw-r--r--.  1 0 0   238 Nov  7  2017 timedatex.service
-rw-r--r--.  1 0 0   445 Jun 22  2018 timers.target
drwxr-xr-x.  2 0 0    42 Apr  4  2019 timers.target.wants
-rw-r--r--.  1 0 0   435 Jun 22  2018 time-sync.target
-rw-r--r--.  1 0 0   704 Jun 22  2018 tmp.mount
-rw-r--r--.  1 0 0   376 Jul  4  2018 tuned.service
-rw-r--r--.  1 0 0   457 Jun 22  2018 umount.target
-rw-r--r--.  1 0 0   296 Aug 12  2018 unbound-anchor.service
-rw-r--r--.  1 0 0   346 Aug 12  2018 unbound-anchor.timer
-rw-r--r--.  1 0 0   551 Feb 26  2019 user-runtime-dir@.service
-rw-r--r--.  1 0 0   671 Feb 26  2019 user@.service
-rw-r--r--.  1 0 0   432 Jun 22  2018 user.slice
drwxr-xr-x.  2 0 0    30 Apr  4  2019 user-.slice.d
-rw-r--r--.  1 0 0   191 Feb 15  2019 var-lib-nfs-rpc_pipefs.mount

/usr/lib/systemd/system/basic.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/dbus.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/default.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/graphical.target.wants:
total 20
drwxr-xr-x.  2 0 0    50 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   801 Feb 26  2019 systemd-update-utmp-runlevel.service

/usr/lib/systemd/system/initrd.target.wants:
total 44
drwxr-xr-x.  2 0 0   225 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   904 Oct  8  2018 dracut-cmdline.service
-rw-r--r--.  1 0 0   821 Oct  8  2018 dracut-initqueue.service
-rw-r--r--.  1 0 0   793 Oct  8  2018 dracut-mount.service
-rw-r--r--.  1 0 0   822 Oct  8  2018 dracut-pre-mount.service
-rw-r--r--.  1 0 0  1125 Oct  8  2018 dracut-pre-pivot.service
-rw-r--r--.  1 0 0   914 Oct  8  2018 dracut-pre-trigger.service
-rw-r--r--.  1 0 0   993 Oct  8  2018 dracut-pre-udev.service

/usr/lib/systemd/system/local-fs.target.wants:
total 20
drwxr-xr-x.  2 0 0    40 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   802 Feb 26  2019 systemd-remount-fs.service

/usr/lib/systemd/system/multi-user.target.wants:
total 40
drwxr-xr-x.  2 0 0   195 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   380 Oct 24  2018 dbus.service
-rw-r--r--.  1 0 0   500 Jun 22  2018 getty.target
-rw-r--r--.  1 0 0   632 Jun 22  2018 systemd-ask-password-wall.path
-rw-r--r--.  1 0 0  1362 Feb 26  2019 systemd-logind.service
-rw-r--r--.  1 0 0   801 Feb 26  2019 systemd-update-utmp-runlevel.service
-rw-r--r--.  1 0 0   636 Feb 26  2019 systemd-user-sessions.service

/usr/lib/systemd/system/remote-fs.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/rescue.target.wants:
total 20
drwxr-xr-x.  2 0 0    50 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   801 Feb 26  2019 systemd-update-utmp-runlevel.service

/usr/lib/systemd/system/runlevel1.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/runlevel2.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/runlevel3.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/runlevel4.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/runlevel5.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/sockets.target.wants:
total 44
drwxr-xr-x.  2 0 0   227 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   102 Oct 24  2018 dbus.socket
-rw-r--r--.  1 0 0   537 Jun 22  2018 systemd-coredump.socket
-rw-r--r--.  1 0 0   546 Jun 22  2018 systemd-initctl.socket
-rw-r--r--.  1 0 0  1130 Jun 22  2018 systemd-journald-dev-log.socket
-rw-r--r--.  1 0 0   882 Jun 22  2018 systemd-journald.socket
-rw-r--r--.  1 0 0   635 Jun 22  2018 systemd-udevd-control.socket
-rw-r--r--.  1 0 0   610 Jun 22  2018 systemd-udevd-kernel.socket

/usr/lib/systemd/system/sysinit.target.wants:
total 132
drwxr-xr-x.  2 0 0  4096 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   412 Jun 22  2018 cryptsetup.target
-rw-r--r--.  1 0 0   750 Jun 22  2018 dev-hugepages.mount
-rw-r--r--.  1 0 0   665 Jun 22  2018 dev-mqueue.mount
-rw-r--r--.  1 0 0   459 Oct  8  2018 dracut-shutdown.service
-rw-r--r--.  1 0 0   721 Feb 26  2019 kmod-static-nodes.service
-rw-r--r--.  1 0 0   687 Jun 22  2018 ldconfig.service
-rw-r--r--.  1 0 0   745 Jun 22  2018 proc-sys-fs-binfmt_misc.automount
-rw-r--r--.  1 0 0   795 Jun 22  2018 sys-fs-fuse-connections.mount
-rw-r--r--.  1 0 0   767 Jun 22  2018 sys-kernel-config.mount
-rw-r--r--.  1 0 0   710 Jun 22  2018 sys-kernel-debug.mount
-rw-r--r--.  1 0 0   704 Jun 22  2018 systemd-ask-password-console.path
-rw-r--r--.  1 0 0  1093 Feb 26  2019 systemd-binfmt.service
-rw-r--r--.  1 0 0   799 Feb 26  2019 systemd-firstboot.service
-rw-r--r--.  1 0 0   826 Feb 26  2019 systemd-hwdb-update.service
-rw-r--r--.  1 0 0   711 Feb 26  2019 systemd-journal-catalog-update.service
-rw-r--r--.  1 0 0  1486 Feb 26  2019 systemd-journald.service
-rw-r--r--.  1 0 0   775 Feb 26  2019 systemd-journal-flush.service
-rw-r--r--.  1 0 0   737 Feb 26  2019 systemd-machine-id-commit.service
-rw-r--r--.  1 0 0  1011 Feb 26  2019 systemd-modules-load.service
-rw-r--r--.  1 0 0   800 Feb 26  2019 systemd-random-seed.service
-rw-r--r--.  1 0 0   697 Feb 26  2019 systemd-sysctl.service
-rw-r--r--.  1 0 0   704 Feb 26  2019 systemd-sysusers.service
-rw-r--r--.  1 0 0   771 Feb 26  2019 systemd-tmpfiles-setup-dev.service
-rw-r--r--.  1 0 0   751 Feb 26  2019 systemd-tmpfiles-setup.service
-rw-r--r--.  1 0 0  1049 Feb 26  2019 systemd-udevd.service
-rw-r--r--.  1 0 0   771 Feb 26  2019 systemd-udev-trigger.service
-rw-r--r--.  1 0 0   674 Feb 26  2019 systemd-update-done.service
-rw-r--r--.  1 0 0   802 Feb 26  2019 systemd-update-utmp.service

/usr/lib/systemd/system/syslog.target.wants:
total 16
drwxr-xr-x.  2 0 0     6 Feb 26  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..

/usr/lib/systemd/system/systemd-udev-trigger.service.d:
total 20
drwxr-xr-x.  2 0 0    49 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0    87 Feb 26  2019 systemd-udev-trigger-no-reload.conf

/usr/lib/systemd/system/system-update.target.wants:
total 20
drwxr-xr-x.  2 0 0    45 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   263 Dec 19  2018 grub-boot-indeterminate.service

/usr/lib/systemd/system/timers.target.wants:
total 20
drwxr-xr-x.  2 0 0    42 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   490 Jun 22  2018 systemd-tmpfiles-clean.timer

/usr/lib/systemd/system/user-.slice.d:
total 20
drwxr-xr-x.  2 0 0    30 Apr  4  2019 .
drwxr-xr-x. 23 0 0 12288 Apr  4  2019 ..
-rw-r--r--.  1 0 0   430 Feb 26  2019 10-defaults.conf

/usr/lib/systemd/system-generators:
total 396
drwxr-xr-x.  2 0 0  4096 Apr  4  2019 .
drwxr-xr-x. 16 0 0  4096 Apr  4  2019 ..
-rwxr-xr-x.  1 0 0   504 Feb 22  2019 kdump-dep-generator.sh
-rwxr-xr-x.  1 0 0 72424 Feb 15  2019 nfs-server-generator
-rwxr-xr-x.  1 0 0 39920 Feb 15  2019 rpc-pipefs-generator
-rwxr-xr-x.  1 0 0   743 Dec 14  2018 selinux-autorelabel-generator.sh
-rwxr-xr-x.  1 0 0 32008 Feb 26  2019 systemd-cryptsetup-generator
-rwxr-xr-x.  1 0 0 17944 Feb 26  2019 systemd-debug-generator
-rwxr-xr-x.  1 0 0 51216 Feb 26  2019 systemd-fstab-generator
-rwxr-xr-x.  1 0 0 19104 Feb 26  2019 systemd-getty-generator
-rwxr-xr-x.  1 0 0 33168 Feb 26  2019 systemd-gpt-auto-generator
-rwxr-xr-x.  1 0 0 13864 Feb 26  2019 systemd-hibernate-resume-generator
-rwxr-xr-x.  1 0 0 13712 Feb 26  2019 systemd-rc-local-generator
-rwxr-xr-x.  1 0 0 14304 Feb 26  2019 systemd-system-update-generator
-rwxr-xr-x.  1 0 0 38408 Feb 26  2019 systemd-sysv-generator
-rwxr-xr-x.  1 0 0 18560 Feb 26  2019 systemd-veritysetup-generator

/usr/lib/systemd/system-preset:
total 20
drwxr-xr-x.  2 0 0  122 Apr  4  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  264 Mar  5  2019 85-display-manager.preset
-rw-r--r--.  1 0 0 3982 Mar  5  2019 90-default.preset
-rw-r--r--.  1 0 0  951 Jun 22  2018 90-systemd.preset
-rw-r--r--.  1 0 0   10 Mar  5  2019 99-default-disable.preset

/usr/lib/systemd/system-shutdown:
total 4
drwxr-xr-x.  2 0 0    6 Feb 26  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..

/usr/lib/systemd/system-sleep:
total 4
drwxr-xr-x.  2 0 0    6 Feb 26  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..

/usr/lib/systemd/user:
total 96
drwxr-xr-x.  4 0 0 4096 Apr  4  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  497 Jun 22  2018 basic.target
-rw-r--r--.  1 0 0  419 Jun 22  2018 bluetooth.target
-rw-r--r--.  1 0 0  360 Oct 24  2018 dbus.service
-rw-r--r--.  1 0 0  178 Oct 24  2018 dbus.socket
-rw-r--r--.  1 0 0  454 Jun 22  2018 default.target
-rw-r--r--.  1 0 0  502 Jun 22  2018 exit.target
-rw-r--r--.  1 0 0  147 Dec  3  2018 glib-pacrunner.service
-rw-r--r--.  1 0 0  568 Jun 22  2018 graphical-session-pre.target
-rw-r--r--.  1 0 0  484 Jun 22  2018 graphical-session.target
-rw-r--r--.  1 0 0  119 Dec 19  2018 grub-boot-success.service
-rw-r--r--.  1 0 0  133 Dec 19  2018 grub-boot-success.timer
-rw-r--r--.  1 0 0  394 Jun 22  2018 paths.target
-rw-r--r--.  1 0 0  417 Jun 22  2018 printer.target
-rw-r--r--.  1 0 0  442 Jun 22  2018 shutdown.target
-rw-r--r--.  1 0 0  420 Jun 22  2018 smartcard.target
-rw-r--r--.  1 0 0  396 Jun 22  2018 sockets.target
drwxr-xr-x.  2 0 0   25 Apr  4  2019 sockets.target.wants
-rw-r--r--.  1 0 0  420 Jun 22  2018 sound.target
-rw-r--r--.  1 0 0  548 Feb 26  2019 systemd-exit.service
-rw-r--r--.  1 0 0  661 Feb 26  2019 systemd-tmpfiles-clean.service
-rw-r--r--.  1 0 0  533 Jun 22  2018 systemd-tmpfiles-clean.timer
-rw-r--r--.  1 0 0  724 Feb 26  2019 systemd-tmpfiles-setup.service
-rw-r--r--.  1 0 0  445 Jun 22  2018 timers.target
drwxr-xr-x.  2 0 0   37 Apr  4  2019 timers.target.wants

/usr/lib/systemd/user/sockets.target.wants:
total 8
drwxr-xr-x. 2 0 0   25 Apr  4  2019 .
drwxr-xr-x. 4 0 0 4096 Apr  4  2019 ..
-rw-r--r--. 1 0 0  178 Oct 24  2018 dbus.socket

/usr/lib/systemd/user/timers.target.wants:
total 8
drwxr-xr-x. 2 0 0   37 Apr  4  2019 .
drwxr-xr-x. 4 0 0 4096 Apr  4  2019 ..
-rw-r--r--. 1 0 0  133 Dec 19  2018 grub-boot-success.timer

/usr/lib/systemd/user-environment-generators:
total 20
drwxr-xr-x.  2 0 0    48 Apr  4  2019 .
drwxr-xr-x. 16 0 0  4096 Apr  4  2019 ..
-rwxr-xr-x.  1 0 0 13280 Feb 26  2019 30-systemd-environment-d-generator

/usr/lib/systemd/user-generators:
total 4
drwxr-xr-x.  2 0 0    6 Feb 26  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..

/usr/lib/systemd/user-preset:
total 8
drwxr-xr-x.  2 0 0   31 Apr  4  2019 .
drwxr-xr-x. 16 0 0 4096 Apr  4  2019 ..
-rw-r--r--.  1 0 0  513 Jun 22  2018 90-systemd.preset
""".strip()


def test_ls_systemd_units():
    systemd = LsSystemdUnits(context_wrap(LS_OUTPUT_FULL))
    assert systemd
    assert len(systemd.listings) == 78
    assert systemd.dirs_of("/etc/systemd/system") == [
        '.',
        '..',
        'basic.target.wants',
        'getty.target.wants',
        'multi-user.target.wants',
        'network-online.target.wants',
        'nfs-blkmap.service.requires',
        'nfs-idmapd.service.requires',
        'nfs-mountd.service.requires',
        'nfs-server.service.requires',
        'remote-fs.target.wants',
        'rpc-gssd.service.requires',
        'rpc-statd-notify.service.requires',
        'rpc-statd.service.requires',
        'sockets.target.wants',
        'sysinit.target.wants',
        'timers.target.wants'
    ]
    assert systemd.files_of("/etc/systemd/system") == [
        'dbus-org.freedesktop.NetworkManager.service',
        'dbus-org.freedesktop.nm-dispatcher.service',
        'dbus-org.freedesktop.timedate1.service',
        'default.target',
        'syslog.service'
    ]
    assert systemd.specials_of("/etc/systemd/system") == [
        'systemd-timedated.service'
    ]
    assert systemd.listing_of("/etc/systemd/system")["syslog.service"] == {
        'date': 'Dec 17  2018',
        'dir': '/etc/systemd/system',
        'group': '0',
        'links': 1,
        'name': 'syslog.service',
        'owner': '0',
        'perms': 'rw-r--r--.',
        'raw_entry': '-rw-r--r--.  1 0 0  583 Dec 17  2018 syslog.service',
        'size': 583,
        'type': '-'
    }


def test_doc_examples():
    env = {
        "ls_systemd_units": LsSystemdUnits(context_wrap(LS_OUTPUT_FULL))
    }
    failed, total = doctest.testmod(ls_systemd_units, globs=env)
    assert failed == 0
