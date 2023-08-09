"""
SystemctlStatusAll command ``systemctl status --all``
=====================================================
"""

from insights.core import LogFileOutput
from insights.core.plugins import parser
from insights.core.filters import add_filter
from insights.specs import Specs


add_filter(Specs.systemctl_status_all, ['State: ', 'Jobs: ', 'Failed: '])


@parser(Specs.systemctl_status_all)
class SystemctlStatusAll(LogFileOutput):
    """
    Class for parsing the output from command ``systemctl status --all``.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Sample output::

        * redhat.test.com
            State: degraded
             Jobs: 0 queued
           Failed: 2 units
            Since: Thu 2021-09-23 12:03:43 UTC; 3h 7min ago
           CGroup: /
                   |-user.slice
                   | `-user-1000.slice
                   |   |-user@1000.service

        Sep 23 15:11:07 redhat.test.com systemd[1]: proc-sys-fs-binfmt_misc.automount: Automount point already active?
        Sep 23 15:11:07 redhat.test.com systemd[1]: proc-sys-fs-binfmt_misc.automount: Got automount request for /proc/sys/fs/binfmt_mis

    Examples:
        >>> type(systemctl_status)
        <class 'insights.parsers.systemctl_status_all.SystemctlStatusAll'>
        >>> "Automount point already active?" in  systemctl_status
        True
        >>> systemctl_status.state == 'degraded'
        True
        >>> systemctl_status.jobs == '0 queued'
        True
        >>> systemctl_status.failed == '2 units'
        True
    """
    _state = _jobs = _failed = False  # Use False to avoid conflicting with None

    def __get_item(self, key):
        ret = self.get(key, num=1)
        if ret:
            return ret[0]['raw_message'].split(':')[1].strip()
        return None

    @property
    def state(self):
        """
        (str): "State" shown in the command output, `None` by default.
        """
        if self._state is False:
            self._state = self.__get_item('State: ')
        return self._state

    @property
    def jobs(self):
        """
        (str): "Jobs" shown in the command output, `None` by default.
        """
        if self._jobs is False:
            self._jobs = self.__get_item('Jobs: ')
        return self._jobs

    @property
    def failed(self):
        """
        (str): "Failed" shown in the command output, `None` by default.
        """
        if self._failed is False:
            self._failed = self.__get_item('Failed: ')
        return self._failed
