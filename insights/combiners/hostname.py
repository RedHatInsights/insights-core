"""
Hostname
========

Combiner for ``hostname`` information. It uses the results of the
``Hostname`` parser, ``Facter`` and the ``SystemID`` parser to get the fqdn,
hostname and domain information.

Examples:
    >>> hn = shared[Hostname]
    >>> hn.fqdn
    rhel7.redhat.com
    >>> hn.hostname
    rhel7
    >>> hn.domain
    redhat.com
    >>> hn
    Hostname(fqdn='rhel7.redhat.com', hostname='rhel7', domain='redhat.com')

"""

from collections import namedtuple
from insights.core.plugins import combiner
from insights.parsers.hostname import Hostname as hname
from insights.parsers.facter import Facter as facter
from insights.parsers.systemid import SystemID as systemid

Hostname = namedtuple("Hostname", field_names=["fqdn", "hostname", "domain"])
"""namedtuple: Type for storing the hostname information."""


@combiner(requires=[[hname, facter, systemid]])
def hostname(shared):
    """Check hostname, facter and systemid to get the fqdn, hostname and domain.

    Prefer hostname to facter and systemid.

    Returns:
        insights.combiners.hostname.Hostname: A named tuple with `fqdn`,
        `hostname` and `domain` components.

    Raises:
        Exception: If no hostname can be found in any of the three parsers.
    """

    hn = shared.get(hname)

    if not hn or not hn.fqdn:
        hn = shared.get(facter)

    if hn and hn.fqdn:
        fqdn = hn.fqdn
        hostname = hn.hostname if hn.hostname else fqdn.split(".")[0]
        domain = hn.domain if hn.domain else ".".join(fqdn.split(".")[1:])
        return Hostname(fqdn, hostname, domain)
    else:
        si = shared.get(systemid)
        fqdn = si.get("profile_name") if si else None
        if fqdn:
            hostname = fqdn.split(".")[0]
            domain = ".".join(fqdn.split(".")[1:])
            return Hostname(fqdn, hostname, domain)

    raise Exception("Unable to get hostname.")
