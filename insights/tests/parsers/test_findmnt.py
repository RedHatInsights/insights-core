import doctest
import pytest
from insights.parsers import findmnt, SkipException
from insights.tests import context_wrap

FINDMNT_NETNS_SHARED_1 = """
TARGET                                                          SOURCE                                FSTYPE          OPTIONS                                                                       PROPAGATION
/sys                                                            sysfs                                 sysfs           rw,nosuid,nodev,noexec,relatime,seclabel                                      shared
/proc                                                           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared
/dev                                                            devtmpfs                              devtmpfs        rw,nosuid,seclabel,size=8035516k,nr_inodes=2008879,mode=755                   shared
/sys/kernel/security                                            securityfs                            securityfs      rw,nosuid,nodev,noexec,relatime                                               shared
/dev/shm                                                        tmpfs                                 tmpfs           rw,nosuid,nodev,seclabel                                                      shared
/run/netns                                                      tmpfs[/netns]                         tmpfs           rw,nosuid,nodev,seclabel,mode=755                                             shared
/netns                                                          tmpfs[/netns]                         tmpfs           rw,nosuid,nodev,seclabel,mode=755                                             shared
/run/netns/qdhcp-08f32dab-927e-4a61-933d-57d425827b57           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared
/run/netns/qdhcp-fd138c0a-5ec7-44f8-88df-0501c4c7a968           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared
""".strip()

FINDMNT_NETNS_SHARED_2 = """
TARGET                                                          SOURCE                                FSTYPE          OPTIONS                                                                       PROPAGATION
/sys                                                            sysfs                                 sysfs           rw,nosuid,nodev,noexec,relatime,seclabel                                      shared
/proc                                                           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared
/dev                                                            devtmpfs                              devtmpfs        rw,nosuid,seclabel,size=8035516k,nr_inodes=2008879,mode=755                   shared
/sys/kernel/security                                            securityfs                            securityfs      rw,nosuid,nodev,noexec,relatime                                               shared
/dev/shm                                                        tmpfs                                 tmpfs           rw,nosuid,nodev,seclabel                                                      shared
/netns                                                          tmpfs[/netns]                         tmpfs           rw,nosuid,nodev,seclabel,mode=755                                             shared
/run/netns/qdhcp-08f32dab-927e-4a61-933d-57d425827b57           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared
/run/netns/qdhcp-fd138c0a-5ec7-44f8-88df-0501c4c7a968           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared
""".strip()

FINDMNT_NETNS_PRIVATE = """
TARGET                                                          SOURCE                                FSTYPE          OPTIONS                                                                       PROPAGATION
/sys                                                            sysfs                                 sysfs           rw,nosuid,nodev,noexec,relatime,seclabel                                      shared
/proc                                                           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared
/dev                                                            devtmpfs                              devtmpfs        rw,nosuid,seclabel,size=8035516k,nr_inodes=2008879,mode=755                   shared
/sys/kernel/security                                            securityfs                            securityfs      rw,nosuid,nodev,noexec,relatime                                               shared
/dev/shm                                                        tmpfs                                 tmpfs           rw,nosuid,nodev,seclabel                                                      shared
/run/netns                                                      tmpfs[/netns]                         tmpfs           rw,nosuid,nodev,seclabel,mode=755                                             private
/netns                                                          tmpfs[/netns]                         tmpfs           rw,nosuid,nodev,seclabel,mode=755                                             private
/run/netns/qdhcp-08f32dab-927e-4a61-933d-57d425827b57           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               private
/run/netns/qdhcp-fd138c0a-5ec7-44f8-88df-0501c4c7a968           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               private
""".strip()

FINDMNT_NO_NETNS = """
TARGET                                                                                           SOURCE     FSTYPE     OPTIONS                                                                                                                                PROPAGATION
/sys                                                                                             sysfs      sysfs      rw,nosuid,nodev,noexec,relatime,seclabel                                                                                               shared
/proc                                                                                            proc       proc       rw,nosuid,nodev,noexec,relatime                                                                                                        shared
/dev                                                                                             devtmpfs   devtmpfs   rw,nosuid,seclabel,size=5912356k,nr_inodes=1478089,mode=755                                                                            shared
/sys/kernel/security                                                                             securityfs securityfs rw,nosuid,nodev,noexec,relatime                                                                                                        shared
/dev/shm                                                                                         tmpfs      tmpfs      rw,nosuid,nodev,seclabel                                                                                                               shared
/dev/pts                                                                                         devpts     devpts     rw,nosuid,noexec,relatime,seclabel,gid=5,mode=620,ptmxmode=000                                                                         shared
/run                                                                                             tmpfs      tmpfs      rw,nosuid,nodev,seclabel,mode=755                                                                                                      shared
/sys/fs/cgroup                                                                                   tmpfs      tmpfs      ro,nosuid,nodev,noexec,seclabel,mode=755                                                                                               shared
/sys/fs/cgroup/systemd                                                                           cgroup     cgroup     rw,nosuid,nodev,noexec,relatime,seclabel,xattr,release_agent=/usr/lib/systemd/systemd-cgroups-agent,name=systemd                       shared
/sys/fs/pstore                                                                                   pstore     pstore     rw,nosuid,nodev,noexec,relatime                                                                                                        shared
/sys/fs/cgroup/perf_event                                                                        cgroup     cgroup     rw,nosuid,nodev,noexec,relatime,seclabel,perf_event                                                                                    shared
/sys/fs/cgroup/cpu,cpuacct                                                                       cgroup     cgroup     rw,nosuid,nodev,noexec,relatime,seclabel,cpuacct,cpu                                                                                   shared
/sys/fs/cgroup/hugetlb                                                                           cgroup     cgroup     rw,nosuid,nodev,noexec,relatime,seclabel,hugetlb                                                                                       shared
/sys/fs/cgroup/freezer                                                                           cgroup     cgroup     rw,nosuid,nodev,noexec,relatime,seclabel,freezer                                                                                       shared
/sys/fs/cgroup/net_cls,net_prio                                                                  cgroup     cgroup     rw,nosuid,nodev,noexec,relatime,seclabel,net_prio,net_cls                                                                              shared
/sys/fs/cgroup/devices                                                                           cgroup     cgroup     rw,nosuid,nodev,noexec,relatime,seclabel,devices                                                                                       shared
/sys/fs/cgroup/blkio                                                                             cgroup     cgroup     rw,nosuid,nodev,noexec,relatime,seclabel,blkio                                                                                         shared
/var/lib/docker/containers/eb7baaab48d9757e6b6250303c078862792d2a8d4cebd7438170057044a90c3e/shm  shm        tmpfs      rw,nosuid,nodev,noexec,relatime,seclabel,size=65536k                                                                                   private
/var/lib/docker/containers/8af84c3469728812b2959c4a1c95336159efd17407a51c4461b5e20f09a5bb6f/shm  shm        tmpfs      rw,nosuid,nodev,noexec,relatime,seclabel,size=65536k                                                                                   private
/var/lib/docker/containers/54f2fdc2885805159d9fc2c656a3fa073b99bcfa430d9b42683afcc5f5b7dc4d/shm  shm        tmpfs      rw,nosuid,nodev,noexec,relatime,seclabel,size=65536k                                                                                   private
/var/lib/docker/containers/752bbb082c2b7f3d411aa244b77e2d57f64ca9ec25cb954a3e4e97d48baaa542/shm  shm        tmpfs      rw,nosuid,nodev,noexec,relatime,seclabel,size=65536k                                                                                   private
/var/lib/docker/containers/867c62f7157e8c7fff23b81a19c2e4368a2bf5703383ab2372fabb9cb38e8a4a/shm  shm        tmpfs      rw,nosuid,nodev,noexec,relatime,seclabel,size=65536k                                                                                   private
/var/lib/docker/containers/3e1814279bf5f42a74288d8e3a197f7b1388f59582590045755e8e4ca8ee5a19/shm  shm        tmpfs      rw,nosuid,nodev,noexec,relatime,seclabel,size=65536k                                                                                   private
/var/lib/docker/containers/64136ecd23d34617ddb5e18eb337b1467a8f5fa29e804420f4c61688ae2e6531/shm  shm        tmpfs      rw,nosuid,nodev,noexec,relatime,seclabel,size=65536k                                                                                   private
/var/lib/docker/containers/fe2b38088424c5102fdab3f13f93c9341c9311dca176eb175a58bb8bdf545927/shm  shm        tmpfs      rw,nosuid,nodev,noexec,relatime,seclabel,size=65536k                                                                                   private
""".strip()


def test_findmnt_output():
    output = findmnt.FindmntPropagation(context_wrap(FINDMNT_NETNS_SHARED_1))
    assert output.search_target('shm') == [{'target': '/dev/shm', 'source': 'tmpfs', 'fstype': 'tmpfs', 'options': 'rw,nosuid,nodev,seclabel', 'propagation': 'shared'}]
    assert len(output.target_startswith('/run/netns')) == 3
    assert output.target_startswith('/run/netns')[0].get('propagation') == 'shared'

    output = findmnt.FindmntPropagation(context_wrap(FINDMNT_NETNS_SHARED_2))
    assert output.target_startswith('/run/netns')[0].get('propagation') == 'shared'

    output = findmnt.FindmntPropagation(context_wrap(FINDMNT_NETNS_PRIVATE))
    assert output.target_startswith('/run/netns')[0].get('propagation') != 'shared'
    assert output.target_startswith('/run/netns')[0].get('propagation') == 'private'

    output = findmnt.FindmntPropagation(context_wrap(FINDMNT_NO_NETNS))
    assert output.search_target('netns') == []
    assert output.target_startswith('/run/netns') == []


def test_blank_output():
    with pytest.raises(SkipException) as e:
        findmnt.FindmntPropagation(context_wrap(""))
    assert "No data." in str(e)


def test_documentation():
    failed_count, tests = doctest.testmod(
        findmnt,
        globs={'output': findmnt.FindmntPropagation(context_wrap(FINDMNT_NETNS_SHARED_1))}
    )
    assert failed_count == 0
