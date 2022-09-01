from insights.parsers.journalctl import JournalAll, JournalSinceBoot, JournalHeader
from insights.tests import context_wrap
from insights.parsers import journalctl
import doctest

JOURNAL_ALL_MSGINFO = """
-- Logs begin at Wed 2017-02-08 15:18:00 CET, end at Tue 2017-09-19 09:12:59 CEST. --
May 18 15:13:34 lxc-rhel68-sat56 jabberd/sm[11057]: session started: jid=rhn-dispatcher-sat@lxc-rhel6-sat56.redhat.com/superclient
May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: --> Wrapper Started as Daemon
May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM...
May 18 15:24:28 lxc-rhel68-sat56 yum[11597]: Installed: lynx-2.8.6-27.el6.x86_64
May 18 15:36:19 lxc-rhel68-sat56 yum[11954]: Updated: sos-3.2-40.el6.noarch
Apr 22 10:35:01 boy-bona CROND[27921]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
Apr 22 10:37:32 boy-bona crontab[28951]: (root) LIST (root)
Apr 22 10:40:01 boy-bona CROND[30677]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
Apr 22 10:41:13 boy-bona crontab[32515]: (root) LIST (root)
""".strip()

JOURNAL_SINCE_BOOT_MSGINFO = """
-- Logs begin at Wed 2017-02-08 15:18:00 CET, end at Tue 2017-09-19 09:12:59 CEST. --
May 18 15:13:34 lxc-rhel68-sat56 jabberd/sm[11057]: session started: jid=rhn-dispatcher-sat@lxc-rhel6-sat56.redhat.com/superclient
May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: --> Wrapper Started as Daemon
May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM...
May 18 15:24:28 lxc-rhel68-sat56 yum[11597]: Installed: lynx-2.8.6-27.el6.x86_64
May 18 15:36:19 lxc-rhel68-sat56 yum[11954]: Updated: sos-3.2-40.el6.noarch
Apr 22 10:35:01 boy-bona CROND[27921]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
Apr 22 10:37:32 boy-bona crontab[28951]: (root) LIST (root)
Apr 22 10:40:01 boy-bona CROND[30677]: (root) CMD (/usr/lib64/sa/sa1 -S DISK 1 1)
Apr 22 10:41:13 boy-bona crontab[32515]: (root) LIST (root)
""".strip()

JOURNALCTL_HEADER_VALID = """
File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system.journal
File ID: b1390ea69aa747e9ac5c597835c3c562
Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
Boot ID: 082ada53f8184c4896c73101ad793eb5
Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
State: ONLINE
Compatible Flags:
Incompatible Flags: COMPRESSED-LZ4
Header size: 240
Arena size: 8388368
Data Hash Table Size: 19904
Field Hash Table Size: 333
Rotate Suggested: no
Head Sequential Number: 74388 (12294)
Tail Sequential Number: 81647 (13eef)
Head Realtime Timestamp: Mon 2022-08-15 12:01:10 CST (5e63fae9e6e58)
Tail Realtime Timestamp: Wed 2022-08-17 18:38:48 CST (5e66d7852bb3e)
Tail Monotonic Timestamp: 1month 2w 3d 14h 19min 3.733s (3c647d7ce0f)
Objects: 19073
Entry Objects: 7260
Data Objects: 9297
Data Hash Table Fill: 46.7%
Field Objects: 52
Field Hash Table Fill: 15.6%
Tag Objects: 0
Entry Array Objects: 2462
Disk usage: 8.0M
File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system@435b0e30f47a46d8a2a2f9a42eae0aaf-000000000000f7d9-0005e5c6d743ca16.journal
File ID: 3aa38e09ef8540fdb55715e1739d44ef
Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
Boot ID: 082ada53f8184c4896c73101ad793eb5
Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
State: ARCHIVED
Compatible Flags:
Incompatible Flags: COMPRESSED-LZ4
Header size: 240
Arena size: 11464464
Data Hash Table Size: 19904
Field Hash Table Size: 333
Rotate Suggested: yes
Head Sequential Number: 63449 (f7d9)
Tail Sequential Number: 74387 (12293)
Head Realtime Timestamp: Tue 2022-08-09 11:51:01 CST (5e5c6d743ca16)
Tail Realtime Timestamp: Mon 2022-08-15 12:01:10 CST (5e63fae9e1ebf)
Tail Monotonic Timestamp: 1month 2w 1d 7h 41min 26.148s (3987e2331db)
Objects: 29134
Entry Objects: 10939
Data Objects: 14929
Data Hash Table Fill: 75.0%
Field Objects: 76
Field Hash Table Fill: 22.8%
Tag Objects: 0
Entry Array Objects: 3188
Disk usage: 10.9M
File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system@435b0e30f47a46d8a2a2f9a42eae0aaf-000000000000cd85-0005e53f0e6e2342.journal
File ID: ab8fc76ad15b4c61bdc172533fe2e623
Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
Boot ID: 082ada53f8184c4896c73101ad793eb5
Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
State: ARCHIVED
Compatible Flags:
Incompatible Flags: COMPRESSED-LZ4
Header size: 240
Arena size: 11464464
Data Hash Table Size: 19904
Field Hash Table Size: 333
Rotate Suggested: yes
Head Sequential Number: 52613 (cd85)
Tail Sequential Number: 63448 (f7d8)
Head Realtime Timestamp: Tue 2022-08-02 17:51:11 CST (5e53f0e6e2342)
Tail Realtime Timestamp: Tue 2022-08-09 11:51:01 CST (5e5c6d7438053)
Tail Monotonic Timestamp: 1month 1w 2d 7h 31min 17.032s (31fa6c89323)
Objects: 29052
Entry Objects: 10836
Data Objects: 14929
Data Hash Table Fill: 75.0%
Field Objects: 50
Field Hash Table Fill: 15.0%
Tag Objects: 0
Entry Array Objects: 3235
Disk usage: 10.9M
File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system@435b0e30f47a46d8a2a2f9a42eae0aaf-000000000000a315-0005e4ba61aa5231.journal
File ID: 428429bbac0c4051b0ece56a05ad2444
Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
Boot ID: 082ada53f8184c4896c73101ad793eb5
Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
State: ARCHIVED
Compatible Flags:
Incompatible Flags: COMPRESSED-LZ4
Header size: 240
Arena size: 11464464
Data Hash Table Size: 19904
Field Hash Table Size: 333
Rotate Suggested: yes
Head Sequential Number: 41749 (a315)
Tail Sequential Number: 52612 (cd84)
Head Realtime Timestamp: Wed 2022-07-27 03:33:57 CST (5e4ba61aa5231)
Tail Realtime Timestamp: Tue 2022-08-02 17:51:02 CST (5e53f0de06aa0)
Tail Monotonic Timestamp: 1month 2d 13h 31min 17.733s (297dd657d70)
Objects: 29018
Entry Objects: 10864
Data Objects: 14929
Data Hash Table Fill: 75.0%
Field Objects: 49
Field Hash Table Fill: 14.7%
Tag Objects: 0
Entry Array Objects: 3174
Disk usage: 10.9M
File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system@435b0e30f47a46d8a2a2f9a42eae0aaf-000000000000785e-0005e437ff062b37.journal
File ID: d003176b94844c9bbada85c404d79c32
Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
Boot ID: 082ada53f8184c4896c73101ad793eb5
Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
State: ARCHIVED
Compatible Flags:
Incompatible Flags: COMPRESSED-LZ4
Header size: 240
Arena size: 11464464
Data Hash Table Size: 19904
Field Hash Table Size: 333
Rotate Suggested: yes
Head Sequential Number: 30814 (785e)
Tail Sequential Number: 41748 (a314)
Head Realtime Timestamp: Wed 2022-07-20 16:00:36 CST (5e437ff062b37)
Tail Realtime Timestamp: Wed 2022-07-27 03:33:56 CST (5e4ba61a1cb8a)
Tail Monotonic Timestamp: 3w 5d 9h 44min 12.265s (2133126de5b)
Objects: 29093
Entry Objects: 10935
Data Objects: 14929
Data Hash Table Fill: 75.0%
Field Objects: 49
Field Hash Table Fill: 14.7%
Tag Objects: 0
Entry Array Objects: 3178
Disk usage: 10.9M
File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system@435b0e30f47a46d8a2a2f9a42eae0aaf-0000000000004ebd-0005e3aaad8b8fe3.journal
File ID: 9f5a3dbdf74343d88f78e4eb90864c01
Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
Boot ID: 082ada53f8184c4896c73101ad793eb5
Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
State: ARCHIVED
Compatible Flags:
Incompatible Flags: COMPRESSED-LZ4
Header size: 240
Arena size: 11464464
Data Hash Table Size: 19904
Field Hash Table Size: 333
Rotate Suggested: yes
Head Sequential Number: 20157 (4ebd)
Tail Sequential Number: 30813 (785d)
Head Realtime Timestamp: Wed 2022-07-13 15:24:39 CST (5e3aaad8b8fe3)
Tail Realtime Timestamp: Wed 2022-07-20 16:00:36 CST (5e437ff0629ba)
Tail Monotonic Timestamp: 2w 5d 22h 10min 52.149s (190ce8b3c8b)
Objects: 28782
Entry Objects: 10657
Data Objects: 14929
Data Hash Table Fill: 75.0%
Field Objects: 51
Field Hash Table Fill: 15.3%
Tag Objects: 0
Entry Array Objects: 3143
Disk usage: 10.9M
File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system@435b0e30f47a46d8a2a2f9a42eae0aaf-0000000000002512-0005e333648ba707.journal
File ID: 9e1a381cedfa4a12a980872d6db84533
Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
Boot ID: 082ada53f8184c4896c73101ad793eb5
Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
State: ARCHIVED
Compatible Flags:
Incompatible Flags: COMPRESSED-LZ4
Header size: 240
Arena size: 11464464
Data Hash Table Size: 19904
Field Hash Table Size: 333
Rotate Suggested: yes
Head Sequential Number: 9490 (2512)
Tail Sequential Number: 20156 (4ebc)
Head Realtime Timestamp: Thu 2022-07-07 17:05:53 CST (5e333648ba707)
Tail Realtime Timestamp: Wed 2022-07-13 15:24:39 CST (5e3aaad8b8ea7)
Tail Monotonic Timestamp: 1w 5d 21h 34min 54.771s (1037d10a179)
Objects: 29077
Entry Objects: 10667
Data Objects: 14929
Data Hash Table Fill: 75.0%
Field Objects: 52
Field Hash Table Fill: 15.6%
Tag Objects: 0
Entry Array Objects: 3427
Disk usage: 10.9M
File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system@435b0e30f47a46d8a2a2f9a42eae0aaf-0000000000000001-0005e2a7308e8200.journal
File ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
Boot ID: 082ada53f8184c4896c73101ad793eb5
Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
State: ARCHIVED
Compatible Flags:
Incompatible Flags: COMPRESSED-LZ4
Header size: 240
Arena size: 11464464
Data Hash Table Size: 19904
Field Hash Table Size: 333
Rotate Suggested: yes
Head Sequential Number: 1 (1)
Tail Sequential Number: 9489 (2511)
Head Realtime Timestamp: Thu 2022-06-30 17:49:45 CST (5e2a7308e8200)
Tail Realtime Timestamp: Thu 2022-07-07 16:30:18 CST (5e332e54aafc7)
Tail Monotonic Timestamp: 6d 22h 40min 33.968s (8bb4cfc298)
Objects: 28018
Entry Objects: 9489
Data Objects: 14930
Data Hash Table Fill: 75.0%
Field Objects: 79
Field Hash Table Fill: 23.7%
Tag Objects: 0
Entry Array Objects: 3518
Disk usage: 10.9M
""".strip()

JOURNALCTL_HEADER_VALID_EXAMPLE = """
File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system.journal
File ID: b1390ea69aa747e9ac5c597835c3c562
Machine ID: 6bdaf92aa0754b53acbb1dbff7127e2b
Boot ID: 082ada53f8184c4896c73101ad793eb5
Sequential Number ID: 435b0e30f47a46d8a2a2f9a42eae0aaf
State: ONLINE
Compatible Flags:
Incompatible Flags: COMPRESSED-LZ4
Header size: 240
Arena size: 8388368
Data Hash Table Size: 19904
Field Hash Table Size: 333
Rotate Suggested: no
Head Sequential Number: 74388 (12294)
Tail Sequential Number: 81647 (13eef)
Head Realtime Timestamp: Mon 2022-08-15 12:01:10 CST (5e63fae9e6e58)
Tail Realtime Timestamp: Wed 2022-08-17 18:38:48 CST (5e66d7852bb3e)
Tail Monotonic Timestamp: 1month 2w 3d 14h 19min 3.733s (3c647d7ce0f)
Objects: 19073
Entry Objects: 7260
Data Objects: 9297
Data Hash Table Fill: 46.7%
Field Objects: 52
Field Hash Table Fill: 15.6%
Tag Objects: 0
Entry Array Objects: 2462
Disk usage: 8.0M
""".strip()


def test_journal_all_messages():
    msg_info = JournalAll(context_wrap(JOURNAL_ALL_MSGINFO))
    bona_list = msg_info.get('(root) LIST (root)')
    assert 2 == len(bona_list)
    assert bona_list[0].get('timestamp') == "Apr 22 10:37:32"
    assert bona_list[1].get('timestamp') == "Apr 22 10:41:13"
    crond = msg_info.get('CROND')
    assert 2 == len(crond)
    assert crond[0].get('procname') == "CROND[27921]"
    assert msg_info.get('jabberd/sm[11057]')[0].get('hostname') == "lxc-rhel68-sat56"
    assert msg_info.get('Wrapper')[0].get('message') == "--> Wrapper Started as Daemon"
    assert msg_info.get('Launching')[0].get('raw_message') == "May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM..."
    assert 2 == len(msg_info.get('yum'))


def test_journal_since_boot_messages():
    msg_info = JournalSinceBoot(context_wrap(JOURNAL_SINCE_BOOT_MSGINFO))
    bona_list = msg_info.get('(root) LIST (root)')
    assert 2 == len(bona_list)
    assert bona_list[0].get('timestamp') == "Apr 22 10:37:32"
    assert bona_list[1].get('timestamp') == "Apr 22 10:41:13"
    crond = msg_info.get('CROND')
    assert 2 == len(crond)
    assert crond[0].get('procname') == "CROND[27921]"
    assert msg_info.get('jabberd/sm[11057]')[0].get('hostname') == "lxc-rhel68-sat56"
    assert msg_info.get('Wrapper')[0].get('message') == "--> Wrapper Started as Daemon"
    assert msg_info.get('Launching')[0].get('raw_message') == "May 18 15:13:36 lxc-rhel68-sat56 wrapper[11375]: Launching a JVM..."
    assert 2 == len(msg_info.get('yum'))


def test_journalctl_header_valid():
    parser_result = JournalHeader(context_wrap(JOURNALCTL_HEADER_VALID))
    assert parser_result is not None
    result_list = parser_result.get('File Path')
    assert len(result_list) == 8
    assert result_list[0].get('raw_message') == 'File Path: /run/log/journal/6bdaf92aa0754b53acbb1dbff7127e2b/system.journal'


def test_losetup_doc_examples():
    env = {'journal_header': JournalHeader(context_wrap(JOURNALCTL_HEADER_VALID_EXAMPLE)),
           'JournalAll': JournalAll(context_wrap(JOURNAL_ALL_MSGINFO)),
           'JournalSinceBoot': JournalSinceBoot(context_wrap(JOURNAL_SINCE_BOOT_MSGINFO))}
    failed, total = doctest.testmod(journalctl, globs=env)
    assert failed == 0
