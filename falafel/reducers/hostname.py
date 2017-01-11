"""
Hostname
========

Shared reducer for ``hostname`` information. It uses the results of the
``Hostname`` mapper, ``Facter`` and the ``SystemID`` mapper to get the fqdn,
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
from falafel.core.plugins import reducer
from falafel.mappers.hostname import Hostname as hname
from falafel.mappers.facter import Facter as facter
from falafel.mappers.systemid import SystemID as systemid

Hostname = namedtuple("Hostname", field_names=["fqdn", "hostname", "domain"])
"""namedtuple: Type for storing the hostname information."""


@reducer(requires=[[hname, facter, systemid]], shared=True)
def hostname(local, shared):
    """Check hostname, facter and systemid to get the fqdn, hostname and domain.

    Prefer hostname to facter and systemid.

    Returns:
        Hostname: A named tuple with `fqdn`, `hostname` and `domain`
        components.

    Raises:
        Exception: If nothing can be gotten from all the three mappers.
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
