"""
Uptime
======

Combiner for uptime information. It uses the results of the ``Uptime``
parser and the ``Facter`` parser to get the uptime information.  ``Uptime`` is
the preferred source of data.

Examples:
    >>> ut = shared[uptime]
    >>> ut.updays
    21
    >>> ht.uptime
    03:45

"""
from __future__ import division
from collections import namedtuple
from insights.core.plugins import combiner
from insights.parsers.uptime import Uptime as upt
from insights.parsers.facter import Facter

Uptime = namedtuple("Uptime",
                    field_names=[
                        "currtime", "updays", "uphhmm",
                        "users", "loadavg", "uptime"])
"""namedtuple: Type for storing the uptime information."""


@combiner([upt, Facter])
def uptime(ut, facter):
    """Check uptime and facts to get the uptime information.

    Prefer uptime to facts.

    Returns:
        insights.combiners.uptime.Uptime: A named tuple with `currtime`,
        `updays`, `uphhmm`, `users`, `loadavg` and `uptime` components.

    Raises:
        Exception: If no data is available from both of the parsers.
    """

    ut = ut
    if ut and ut.loadavg:
        return Uptime(ut.currtime, ut.updays, ut.uphhmm,
                      ut.users, ut.loadavg, ut.uptime)
    ft = facter
    if ft and hasattr(ft, 'uptime_seconds'):
        import datetime
        secs = int(ft.uptime_seconds)
        up_dd = secs // (3600 * 24)
        up_hh = (secs % (3600 * 24)) // 3600
        up_mm = (secs % 3600) // 60
        updays = str(up_dd) if up_dd > 0 else ''
        uphhmm = '%02d:%02d' % (up_hh, up_mm)
        up_time = datetime.timedelta(seconds=secs)
        return Uptime(None, updays, uphhmm, None, None, up_time)

    raise Exception("Unable to get uptime information.")
