"""
CertList - command ``getcert list``
====================================

"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.parsers import keyword_search
from insights.specs import Specs


@parser(Specs.getcert_list)
class CertList(CommandParser):
    """
    Parse the output of ``getcert list``.

    Stores data as a pseudo-dictionary, keyed on request ID.  But it's much
    easier to find requests based on their properties, using the ``search``
    method.  This finds requests based on their keys, e.g.
    ``search(stuck='no')``.  Spaces and dashes are converted to underscores
    in the keys being sought, so one can search for ``key_pair_storage`` or
    ``pre_save_command``.  Multiple keys can be searched in the same call,
    e.. ``search(CA="IPA", stuck='yes')``.  If no keys are given, no requests
    are returned.

    Sample output::

        Number of certificates and requests being tracked: 2.
        Request ID '20130725003533':
                status: MONITORING
                stuck: no
                key pair storage: type=NSSDB,location='/etc/dirsrv/slapd-LDAP-EXAMPLE-COM',nickname='Server-Cert',token='NSS Certificate DB',pinfile='/etc/dirsrv/slapd-LDAP-EXAMPLE-COM/pwdfile.txt'
                certificate: type=NSSDB,location='/etc/dirsrv/slapd-LDAP-EXAMPLE-COM',nickname='Server-Cert',token='NSS Certificate DB'
                CA: IPA
                issuer: CN=Certificate Authority,O=LDAP.EXAMPLE.COM
                subject: CN=master.LDAP.EXAMPLE.COM,O=LDAP.EXAMPLE.COM
                expires: 2017-06-28 12:52:12 UTC
                eku: id-kp-serverAuth,id-kp-clientAuth
                pre-save command:
                post-save command: /usr/lib64/ipa/certmonger/restart_dirsrv LDAP-EXAMPLE-COM
                track: yes
                auto-renew: yes
        Request ID '20130725003602':
                status: MONITORING
                stuck: no
                key pair storage: type=NSSDB,location='/etc/dirsrv/slapd-PKI-IPA',nickname='Server-Cert',token='NSS Certificate DB',pinfile='/etc/dirsrv/slapd-PKI-IPA/pwdfile.txt'
                certificate: type=NSSDB,location='/etc/dirsrv/slapd-PKI-IPA',nickname='Server-Cert',token='NSS Certificate DB'
                CA: IPA
                issuer: CN=Certificate Authority,O=EXAMPLE.COM
                subject: CN=ldap.EXAMPLE.COM,O=EXAMPLE.COM
                expires: 2017-06-28 12:52:13 UTC
                eku: id-kp-serverAuth,id-kp-clientAuth
                pre-save command:
                post-save command: /usr/lib64/ipa/certmonger/restart_dirsrv PKI-IPA
                track: yes
                auto-renew: yes

    Attributes:

        num_tracked (int): The number of 'tracked' certificates and requests,
            as given in the first line of the output.
        requests (list): The list of request IDs as they appear in the output,
            as strings.

    Examples:

        >>> certs = shared[Cert_List]
        >>> certs.num_tracked  # number of certificates tracked from first line
        2
        >>> len(certs)  # number of requests stored - may be smaller than num_tracked
        2
        >>> certs.requests
        ['20130725003533', '20130725003602']
        >>> '20130725003533' in certs
        True
        >>> certs['20130725003533']['issuer']
        'CN=Certificate Authority,O=LDAP.EXAMPLE.COM'
        >>> for request in certs.search(CA='IPA'):
        ...     print request['certificate']
        ...
        type=NSSDB,location='/etc/dirsrv/slapd-LDAP-EXAMPLE-COM',nickname='Server-Cert',token='NSS Certificate DB'
        type=NSSDB,location='/etc/dirsrv/slapd-PKI-IPA',nickname='Server-Cert',token='NSS Certificate DB'

    """

    def parse_content(self, content):
        """
        We're only interested in lines that contain a ':'.  Special lines
        start with 'Request ID' and 'Number of certificates...'; we handle
        those separately.  All other lines are stripped of surrounding white
        space and stored as a key-value pair against the last request ID.
        """
        self._data = {}
        self.num_tracked = 0
        self.requests = []
        self._rq_list = []
        current_request = None

        _TRACK_HEADER = 'Number of certificates and requests being tracked: '
        _RQ_HEADER = 'Request ID '
        for line in content:
            line = line.strip()
            if line.startswith(_TRACK_HEADER):
                num_tracked = line[len(_TRACK_HEADER):-1]
                if not num_tracked.isdigit():
                    raise ParseException("Incorrectly formatted number of certificates and requests")
                self.num_tracked = int(num_tracked)
            elif line.startswith(_RQ_HEADER):
                current_request = line[len(_RQ_HEADER) + 1:-2]
                if current_request in self._data:
                    raise ParseException("Found duplicate request ID '{rq}'".format(rq=current_request))
                self._data[current_request] = {}
                self.requests.append(current_request)
                self._rq_list.append(self._data[current_request])
            elif line.endswith(':'):
                # Key with no value - fake it
                key = line[:-1]
                self._data[current_request][key] = ''
            elif ': ' in line:
                key, val = line.split(': ', 1)
                self._data[current_request][key] = val

    def __contains__(self, rq):
        """
        Does the certificate collection contain the given request ID?
        """
        return rq in self._data

    def __len__(self):
        """
        Return the number of requests found (not the number tracked)
        """
        return len(self._data)

    def __getitem__(self, rq):
        """
        Return the request with the given ID.
        """
        return self._data[rq]

    def search(self, **kwargs):
        """
        Search for one or more key-value pairs in the given data.  See the
        documentation of meth:insights.parsers.keyword_search for more
        details on how to use it.
        """
        return keyword_search(self._rq_list, **kwargs)
