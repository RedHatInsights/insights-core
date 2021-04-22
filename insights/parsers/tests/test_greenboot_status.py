from insights.tests import context_wrap
from insights.parsers.greenboot_status import GreenbootStatus


GREEN = """
Boot Status is GREEN - Health Check SUCCESS
"""


RED = """
Mar 04 15:47:12 example greenboot[768]: Script 'check-dns.sh' SUCCESS
Mar 04 15:47:12 example required-services.sh[999]: active
Mar 04 15:47:12 example required-services.sh[999]: active
Mar 04 15:47:12 example required-services.sh[999]: inactive
Mar 04 15:47:10 example NetworkManager[886]: <info>  [1614872830.0295] manager: NetworkManager state is now CONNECTED_GLOBAL
Mar 04 15:47:12 example check-dns.sh[801]: PING 192.168.81.1 (192.168.81.1) 56(84) bytes of data.
Mar 04 15:47:12 example check-dns.sh[801]: 64 bytes from 192.168.81.1: icmp_seq=1 ttl=64 time=0.253 ms
Mar 04 15:47:12 example check-dns.sh[801]: --- 192.168.81.1 ping statistics ---
Mar 04 15:47:12 example check-dns.sh[801]: 1 packets transmitted, 1 received, 0% packet loss, time 0ms
Mar 04 15:47:12 example check-dns.sh[801]: rtt min/avg/max/mdev = 0.253/0.253/0.253/0.000 ms
Mar 04 15:47:12 example greenboot[768]: Script 'check-dns.sh' SUCCESS
Mar 04 15:47:12 example required-services.sh[999]: active
Mar 04 15:47:12 example required-services.sh[999]: active
Mar 04 15:47:12 example required-services.sh[999]: inactive
Mar 04 15:47:12 example greenboot[768]: Script 'required-services.sh' FAILURE (exit code '3')
Mar 04 15:47:12 example systemd[1]: greenboot-healthcheck.service: Main process exited, code=exited, status=3/NOTIMPLEMENTED
Mar 04 15:47:12 example systemd[1]: greenboot-healthcheck.service: Failed with result 'exit-code'.
Mar 04 15:47:12 example systemd[1]: Failed to start greenboot Health Checks Runner.
Mar 04 15:47:12 example systemd[1]: Dependency failed for Boot Completion Check.
Mar 04 15:47:12 example systemd[1]: Dependency failed for Mark boot as successful in grubenv.
Mar 04 15:47:12 example systemd[1]: Dependency failed for Multi-User System.
Mar 04 15:47:12 example systemd[1]: multi-user.target: Job multi-user.target/start failed with result 'dependency'.
Mar 04 15:47:12 example systemd[1]: greenboot-grub2-set-success.service: Job greenboot-grub2-set-success.service/start failed with result 'dependency'.
Mar 04 15:47:12 example systemd[1]: Dependency failed for greenboot Success Scripts Runner.
Mar 04 15:47:12 example systemd[1]: greenboot-task-runner.service: Job greenboot-task-runner.service/start failed with result 'dependency'.
Mar 04 15:47:12 example systemd[1]: boot-complete.target: Job boot-complete.target/start failed with result 'dependency'.
Mar 04 15:47:12 example systemd[1]: greenboot-healthcheck.service: Triggering OnFailure= dependencies.
Mar 04 15:47:12 example systemd[1]: Starting greenboot Failure Scripts Runner...
Mar 04 15:47:12 example systemd[1]: Starting Update UTMP about System Runlevel Changes...
Mar 04 15:47:12 example greenboot[1004]: Boot Status is RED - Health Check FAILURE!
Mar 04 15:47:12 example greenboot[1004]: Running Red Scripts...
Mar 04 15:47:12 example systemd[1]: Started greenboot Failure Scripts Runner.
Mar 04 15:47:12 example systemd[1]: Starting Reboot on red boot status...
Mar 04 15:47:12 example systemd[1]: Starting greenboot MotD Generator...
Mar 04 15:47:12 example systemd[1]: Reached target Generic red boot target.
Mar 04 15:47:12 example redboot-auto-reboot[1009]: SYSTEM is UNHEALTHY, but boot_counter is unset in grubenv. Manual intervention necessary.
Mar 04 15:47:12 example systemd[1]: systemd-update-utmp-runlevel.service: Succeeded.
Mar 04 15:47:12 example systemd[1]: Started Update UTMP about System Runlevel Changes.
Mar 04 15:47:12 example systemd[1]: redboot-auto-reboot.service: Main process exited, code=exited, status=1/FAILURE
Mar 04 15:47:12 example systemd[1]: redboot-auto-reboot.service: Failed with result 'exit-code'.
Mar 04 15:47:12 example systemd[1]: Failed to start Reboot on red boot status.
Mar 04 15:47:12 example greenboot-status[1010]: Script 'required-services.sh' FAILURE (exit code '3')
Mar 04 15:47:12 example greenboot-status[1010]: Boot Status is RED - Health Check FAILURE!
Mar 04 15:47:12 example greenboot-status[1010]: SYSTEM is UNHEALTHY, but boot_counter is unset in grubenv. Manual intervention necessary.
Mar 04 15:47:12 example systemd[1]: Started greenboot MotD Generator.
"""


def test_greenboot_status_green():
    green = context_wrap(GREEN)
    p = GreenbootStatus(green)
    assert p.green
    assert not p.red


def test_greenboot_status_red():
    red = context_wrap(RED)
    p = GreenbootStatus(red)
    assert p.red
    assert not p.green
