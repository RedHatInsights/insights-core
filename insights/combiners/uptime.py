"""
Uptime
======

Combiner for uptime information. It uses the results of the ``Uptime``
parser to get the uptime information.  ``Uptime`` is
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
from insights import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.uptime import Uptime as upt
from insights.util import deprecated

Uptime = namedtuple("Uptime",
                    field_names=[
                        "currtime", "updays", "uphhmm",
                        "users", "loadavg", "uptime"])
"""namedtuple: Type for storing the uptime information."""


@combiner(upt)
def uptime(ut):
    """
    .. warning::
       This combiner method is deprecated, please use
       :py:class:`insights.parsers.uptime.Uptime` instead.

    Check uptime to get the uptime information.

    Returns:
        insights.combiners.uptime.Uptime: A named tuple with `currtime`,
        `updays`, `uphhmm`, `users`, `loadavg` and `uptime` components.

    Raises:
        SkipComponent: If no data is available or if ``loadavg`` is not available.
    """
    deprecated(uptime, "Use the `Uptime` parser instead.")

    if ut.loadavg:
        return Uptime(ut.currtime, ut.updays, ut.uphhmm,
                      ut.users, ut.loadavg, ut.uptime)

    raise SkipComponent("Unable to get uptime information.")
