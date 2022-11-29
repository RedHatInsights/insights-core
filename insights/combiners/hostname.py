"""
Hostname
========

Combiner for ``hostname`` information. It uses the results of all the
``Hostname`` parsers and the ``SystemID`` parser to get the fqdn,
hostname and domain information.


"""
from insights.core.plugins import combiner
from insights.core.serde import deserializer, serializer
from insights.parsers.hostname import Hostname as HnF, HostnameShort as HnS, HostnameDefault as HnD
from insights.parsers.systemid import SystemID


@combiner([HnF, HnD, HnS, SystemID])
class Hostname(object):
    """
    Check hostname and systemid to get the fqdn, hostname and domain.

    Prefer hostname to systemid.

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
    def __init__(self, hf, hd, hs, sid):
        self.fqdn = self.hostname = self.domain = None

        if hf or hs or hd:
            hn = hf or hs or hd
            self.hostname = self.fqdn = hn.hostname
            self.domain = ''
            if hf and hf.fqdn:
                self.fqdn = hf.fqdn
                self.domain = hf.domain
        else:
            self.fqdn = sid.get("profile_name")
            if self.fqdn:
                self.hostname = self.fqdn.split(".")[0]
                self.domain = ".".join(self.fqdn.split(".")[1:])

        if not self.hostname or not self.fqdn:
            raise Exception("Unable to get hostname.")


@serializer(Hostname)
def serialize(obj, root=None):
    return {"fqdn": obj.fqdn, "hostname": obj.hostname, "domain": obj.domain}


@deserializer(Hostname)
def deserialize(_type, data, root=None):
    return Hostname(**data)
