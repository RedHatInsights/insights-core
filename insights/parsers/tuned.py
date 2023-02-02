"""
Tuned - command ``/usr/sbin/tuned-adm list``
============================================

This parser reads the output of the ``/usr/sbin/tuned-adm list`` command and
reads it into a simple dictionary in the ``data`` property with two of three
keys:

* ``available`` - the list of available profiles
* ``active`` - the active profile name
* ``preset`` - the profile name that's preset to be used when tuned is active

The ``active`` key is available when ``tuned`` is running, because the active
profile is only listed when the daemon is active.  If ``tuned`` is not
running, the tuned-adm command will list the profile that will be used when
the daemon is running, and this is given in the ``preset`` key.

Sample data::

    Available profiles:
    - balanced
    - desktop
    - latency-performance
    - network-latency
    - network-throughput
    - powersave
    - throughput-performance
    - virtual-guest
    - virtual-host
    Current active profile: virtual-guest

Examples:

    >>> type(tuned)
    <class 'insights.parsers.tuned.Tuned'>
    >>> 'active' in tuned
    True
    >>> tuned['active']
    'virtual-guest'
    >>> len(tuned['available'])
    9
    >>> 'balanced' in tuned['available']
    True
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.tuned_adm)
class Tuned(CommandParser, dict):
    """
    Parse output from the ``/usr/sbin/tuned-adm list`` command.

    Raises:
        SkipComponent: When noting needs to parse
    """

    def parse_content(self, content):
        data = {}
        for line in content:
            if line.startswith('-'):
                data.update(available=[]) if 'available' not in data else None
                data['available'].append(line.split('- ')[1].strip())
            elif line.startswith('Current'):
                data['active'] = line.split(': ')[1].strip()
            elif line.startswith('Preset'):
                data['preset'] = line.split(': ')[1].strip()
            # Ignore everything else for now
        if not data:
            raise SkipComponent
        self.update(data)

    @property
    def data(self):
        '''
        For backward compatibility.
        '''
        return self
