"""
YumLog - file ``/var/log/yum.log``
==================================

This module provides parsing for the ``/var/log/yum.log`` file.
"""
from collections import defaultdict, namedtuple
from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.parsers.installed_rpms import InstalledRpm
from insights.specs import Specs


Entry = namedtuple('Entry', field_names='idx timestamp state pkg')
"""namedtuple: Represents a package line in ``/var/log/yum.log``."""
VALID_STATES = ["Erased:", "Installed:", "Updated:"]
"""Package states in this file"""
add_filter(Specs.yum_log, VALID_STATES)


@parser(Specs.yum_log)
class YumLog(Parser, list):
    """
    Class for parsing file ``/var/log/yum.log`` into a list of .

    The file looks like::

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

    The information is stored as a ``list`` of :py:data:`Entry` objects, each
    of which contains attributes for the position in the log, timestamp of the
    action, the package's state in the system, and the affected package as an
    :py:class:`insights.parsers.installed_rpms.InstalledRpm`.

    .. note::
        The file will be filtered at least with the keywords defined in the
        :py:data:`STATES`, that means only the lines that contain one of
        these keywords will be collected.

    Examples:
        >>> type(yl)
        <class 'insights.parsers.yumlog.YumLog'>
        >>> e = yl.present_packages.get('nss-softokn')
        >>> e.pkg.release == '19.el6_6'
        True
        >>> e = yl.present_packages.get('openssl-libs')
        >>> e.pkg.name == 'openssl-libs'
        True
        >>> e.pkg.version == '1.0.1e'
        True
        >>> len(yl)
        8
        >>> sorted(e.idx for e in yl) == sorted(range(len(yl)))
        True
    """
    ERASED = 'Erased'
    """
    .. deprecated:: 3.3.0

       Use string "Erased" instead.
    """

    INSTALLED = 'Installed'
    """
    .. deprecated:: 3.3.0

       Use string "Installed" instead.
    """

    UPDATED = 'Updated'
    """
    .. deprecated:: 3.3.0

       Use string "Updated" instead.
    """

    STATES = set(["Erased", "Installed", "Updated"])

    def parse_content(self, content):
        """Parses contents of each line in ``/var/log/yum.log``.

        Each line in the file contains 5 fields that are parsed into the
        attributes of :py:data:`Entry` instances:

            - month
            - day
            - time
            - state
            - package

        The month, day, and time form the ``Entry.timestamp``.
        ``Entry.state`` contains the state of the package, one of ``Erased``,
        ``Installed``, or ``Updated``. ``Entry.pkg`` contains the
        :py:class:`insights.parsers.installed_rpms.InstalledRpm` instance
        corresponding to the parse package.

        ``Entry.idx`` is the zero-based line number (but not the RAW line number)
        of the ``Entry`` in the file.  It can ONLY be used to tell ordering
        of events.

        Parameters:
            content (list): Lines of ``/var/log/yum.log`` to be parsed.

        Raises:
            ParseException: if a line can't be parsed for any reason.
            SkipComponent: if nothing is parsed.
        """
        self._pkgs = defaultdict(list)
        for idx, line in enumerate(content):
            if not any(s in line for s in self.STATES):  # Do not remove
                continue
            try:
                line = line.replace(': 100', '')
                month, day, time, state, pkg = line.split()[:5]
                timestamp = ' '.join([month, day, time])
                state = state.rstrip(':')
                pkg = pkg.split(':')[-1].strip()
                if "." not in pkg:
                    pkg = InstalledRpm({'name': pkg})
                else:
                    pkg = InstalledRpm.from_package(pkg)
                e = Entry(idx, timestamp, state, pkg)
                self.append(e)
                self._pkgs[pkg.name].append(e)
            except:
                raise ParseException('YumLog could not parse', line)

        if len(self) == 0:
            raise SkipComponent

        self.__cur_pkgs = dict((k, v[-1]) for k, v in self._pkgs.items())

    @property
    def pkgs(self):
        """
        .. deprecated:: 3.3.0

           Just keep backward compatibility
        """
        return dict(self._pkgs)

    @property
    def data(self):
        """
        .. deprecated:: 3.3.0

           Just keep backward compatibility
        """
        return self

    @property
    def present_packages(self):
        """`list` of latest ``Entry`` instances for installed packages."""
        return dict((k, v) for k, v in self.__cur_pkgs.items() if v.state in ['Installed', 'Updated'])

    def packages_of(self, state):
        """
        Parameters:
            state: one state or list of states of `Installed`, `Updated`, and `Erased`.

        Returns:
            `list` of latest ``Entry`` instances for packages in `state`.

        Raises:
            KeyError: when getting invalid state.
        """
        state = [state] if isinstance(state, str) else state
        if any(st not in self.STATES for st in state):
            raise KeyError('Invalid State(s): {0}'.format(state))
        return dict((k, v) for k, v in self.__cur_pkgs.items() if v.state in state)
