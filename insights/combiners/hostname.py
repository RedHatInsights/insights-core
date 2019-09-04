"""
Hostname
========

Combiner for ``hostname`` information. It uses the results of all the
``Hostname`` parsers, ``Facter`` and the ``SystemID`` parser to get the fqdn,
hostname and domain information.


"""

from insights.core.plugins import combiner
from insights.core.serde import deserializer, serializer
from insights.parsers.hostname import Hostname as HnF, HostnameShort as HnS, HostnameDefault as HnD
from insights.parsers.facter import Facter
from insights.parsers.systemid import SystemID
from insights.util import deprecated


@combiner([HnF, HnD, HnS, Facter, SystemID])
class Hostname(object):
    """
    Check hostname, facter and systemid to get the fqdn, hostname and domain.

    Prefer hostname to facter and systemid.

    Examples:
        >>> type(hostname)
        <class 'insights.combiners.hostname.Hostname'>
        >>> hostname.fqdn
        'rhel7.example.com'
        >>> hostname.hostname
        'rhel7'
        >>> hostname.domain
        'example.com'

    Raises:
        Exception: If no hostname can be found in any of the source parsers.
    """
    def __init__(self, hf, hd, hs, ft, sid):
        self.fqdn = self.hostname = self.domain = None

        if hf or hs or hd or ft:
            hn = hf or hs or hd or ft
            self.hostname = self.fqdn = hn.hostname
            self.domain = ''
            if hf and hf.fqdn:
                self.fqdn = hf.fqdn
                self.domain = hf.domain
            elif ft and ft.fqdn:
                self.fqdn = ft.fqdn
                self.domain = ft.domain if ft.domain else ".".join(self.fqdn.split(".")[1:])
        else:
            self.fqdn = sid.get("profile_name")
            if self.fqdn:
                self.hostname = self.fqdn.split(".")[0]
                self.domain = ".".join(self.fqdn.split(".")[1:])

        if not self.hostname or not self.fqdn:
            raise Exception("Unable to get hostname.")


@combiner([HnF, HnD, HnS, Facter, SystemID])
def hostname(hf, hd, hs, ft, sid):
    """
    .. warning::
        This combiner methode is deprecated, please use
        :py:class:`insights.combiners.hostname.Hostname` instead.

    Check hostname, facter and systemid to get the fqdn, hostname and domain.

    Prefer hostname to facter and systemid.

    Examples:
        >>> hn.fqdn
        'rhel7.example.com'
        >>> hn.hostname
        'rhel7'
        >>> hn.domain
        'example.com'

    Returns:
        insights.combiners.hostname.Hostname: A class with `fqdn`,
        `hostname` and `domain` attributes.

    Raises:
        Exception: If no hostname can be found in any of the source parsers.
    """
    deprecated(hostname, "Use the `Hostname` class instead.")
    return Hostname(hf, hd, hs, ft, sid)


@serializer(Hostname)
def serialize(obj, root=None):
    return {"fqdn": obj.fqdn, "hostname": obj.hostname, "domain": obj.domain}


@deserializer(Hostname)
def deserialize(_type, data, root=None):
    return Hostname(**data)
