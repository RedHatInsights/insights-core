"""
YumLog - file ``/var/log/yum.log``
==================================

This module provides parsing for the ``/var/log/yum.log`` file.
The ``YumLog`` class implements parsing for the file, which looks like::

    May 13 15:54:49 Installed: libevent-2.0.21-4.el7.x86_64
    May 13 15:54:49 Installed: tmux-1.8-4.el7.x86_64
    May 23 18:06:24 Installed: wget-1.14-10.el7_0.1.x86_64
    May 23 18:10:05 Updated: 1:openssl-libs-1.0.1e-51.el7_2.5.x86_64
    May 23 18:10:05 Installed: 1:perl-parent-0.225-244.el7.noarch
    May 23 18:10:05 Installed: perl-HTTP-Tiny-0.033-3.el7.noarch
    May 23 16:09:09 Erased: redhat-access-insights-batch
    May 23 18:10:05 Installed: perl-podlators-2.5.1-3.el7.noarch
    May 23 18:10:05 Installed: perl-Pod-Perldoc-3.20-4.el7.noarch
    May 23 18:10:05 Installed: 1:perl-Pod-Escapes-1.04-286.el7.noarch
    May 23 18:10:06 Installed: perl-Text-ParseWords-3.29-4.el7.noarch

The information is stored as a ``list`` of ``Entry`` objects, each of which
contains attributes for the position in the log, timestamp of the action,
the package's state in the system, and the affected package as an
``InstalledRpm``.

Note:
    The examples in this module may be executed with the following command:

    ``python -m insights.parsers.yumlog``

Examples:
    >>> content = '''
    ... May 23 18:06:24 Installed: wget-1.14-10.el7_0.1.x86_64
    ... Jan 24 00:24:00 Updated: glibc-2.12-1.149.el6_6.4.x86_64
    ... Jan 24 00:24:09 Updated: glibc-devel-2.12-1.149.el6_6.4.x86_64
    ... Jan 24 00:24:10 Updated: nss-softokn-3.14.3-19.el6_6.x86_64
    ... Jan 24 18:10:05 Updated: 1:openssl-libs-1.0.1e-51.el7_2.5.x86_64
    ... Jan 24 00:24:11 Updated: glibc-2.12-1.149.el6_6.4.i686
    ... May 23 16:09:09 Erased: redhat-access-insights-batch
    ... Jan 24 00:24:11 Updated: glibc-devel-2.12-1.149.el6_6.4.i686
    ... '''.strip()
    >>> from insights.tests import context_wrap
    >>> yl = YumLog(context_wrap(content))
    >>> e = yl.present_packages.get('nss-softokn')
    >>> e.pkg.release
    '19.el6_6'
    >>> e = yl.present_packages.get('openssl-libs')
    >>> e.pkg.name
    'openssl-libs'
    >>> e.pkg.version
    '1.0.1e'
    >>> len(yl)
    8
    >>> indices = [e.idx for e in yl]
    >>> indices == range(len(yl))
    True
"""
from collections import defaultdict, namedtuple
from insights.core import Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.parsers.installed_rpms import InstalledRpm
from insights.specs import Specs


Entry = namedtuple('Entry', field_names='idx timestamp state pkg')
"""namedtuple: Represents a line in ``/var/log/yum.log``."""


@parser(Specs.yum_log)
class YumLog(Parser):
    """Class for parsing /var/log/yum.log"""

    ERASED = 'Erased'
    """Package Erased"""

    INSTALLED = 'Installed'
    """Package Installed"""

    UPDATED = 'Updated'
    """Package Updated"""

    STATES = set([ERASED, INSTALLED, UPDATED])

    def parse_content(self, content):
        """Parses contents of each line in ``/var/log/yum.log``.

        Each line in the file contains 5 fields that are parsed into the
        attributes of ``Entry`` instances:

            - month
            - day
            - time
            - state
            - package

        The month, day, and time form the ``Entry.timestamp``.
        ``Entry.state`` contains the state of the package, one of ``ERASED``,
        ``INSTALLED``, or ``UPDATED``. ``Entry.pkg`` contains the ``InstalledRpm``
        instance corresponding to the parse package. ``Entry.idx`` is the
        zero-based line number of the ``Entry`` in the file.  It can be
        used to tell ordering of events.

        Parameters:
            content (list): Lines of ``/var/log/yum.log`` to be parsed.

        Raises:
            ParseException: if a line can't be parsed for any reason.
        """
        self.data = []
        self.pkgs = defaultdict(list)
        for idx, line in enumerate(get_active_lines(content)):
            if not any(s in line for s in self.STATES):
                continue
            try:
                line = line.replace(': 100', '')
                month, day, time, state, pkg = line.split()[:5]
                timestamp = ' '.join([month, day, time])
                state = state.rstrip(':')
                pkg = pkg.split(':')[-1].strip()
                if state == self.ERASED and "." not in pkg:
                    pkg = InstalledRpm({'name': pkg})
                else:
                    pkg = InstalledRpm.from_package(pkg)
                e = Entry(idx, timestamp, state, pkg)
                self.data.append(e)
                self.pkgs[pkg.name].append(e)
            except:
                raise ParseException('YumLog could not parse', line)

        self.pkgs = dict(self.pkgs)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for d in self.data:
            yield d

    def _packages_currently(self, states):
        result = {}
        for k, v in self.pkgs.items():
            e = v[-1]
            if e.state in states:
                result[k] = e

        return result

    @property
    def present_packages(self):
        """``list`` of latest ``Entry`` instances for installed packages."""
        return self._packages_currently([self.INSTALLED, self.UPDATED])
