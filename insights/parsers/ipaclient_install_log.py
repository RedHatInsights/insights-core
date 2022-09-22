"""
IpaclientInstallLog - file ``/var/log/ipaclient-install.log``
================================================

This file records the information of IPA client enrollment while
executing command ``ipa-client-install``
"""

from insights.specs import Specs
from .. import LogFileOutput, parser


@parser(Specs.ipaclient_install_log)
class IpaclientInstallLog(LogFileOutput):
    """
    This parser is used to parse the content of file `/var/log/ipaclient-install.log`.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Typical content of ``ipaclient-install.log`` file is::

    2019-11-20T11:31:27Z DEBUG IPA version 4.9.0.dev201911200836+gitc0b0c6b4b-0.fc31
    2019-11-20T11:31:27Z DEBUG Loading Index file from '/var/lib/ipa-client/sysrestore/sysrestore.index'
    2019-11-20T11:31:27Z DEBUG Starting external process
    2019-11-20T11:31:27Z DEBUG args=['/usr/sbin/selinuxenabled']
    2019-11-20T11:31:27Z DEBUG Process finished, return code=0
    2019-11-20T11:31:27Z DEBUG stdout=
    2019-11-20T11:31:27Z DEBUG stderr=
    2019-11-20T11:31:27Z WARNING Using existing certificate '/etc/ipa/ca.crt'.
    2019-11-20T11:31:27Z DEBUG [IPA Discovery]
    2019-11-20T11:31:27Z DEBUG Starting IPA discovery with domain=laptop.example.org, servers=['ipa0.laptop.example.org'], hostname=ipa0.laptop.example.org
    2019-11-20T11:31:27Z DEBUG Server and domain forced
    2019-11-20T11:31:27Z DEBUG [Kerberos realm search]
    2019-11-20T11:31:27Z DEBUG Kerberos realm forced
    2019-11-20T11:31:27Z DEBUG [LDAP server check]
    2019-11-20T11:31:27Z DEBUG Verifying that ipa0.laptop.example.org (realm LAPTOP.EXAMPLE.ORG) is an IPA server
    2019-11-20T11:31:27Z DEBUG Init LDAP connection to: ldap://ipa0.laptop.example.org:389
    2019-11-20T11:31:27Z DEBUG Search LDAP server for IPA base DN
    2019-11-20T11:31:27Z DEBUG Check if naming context 'dc=laptop,dc=example,dc=org' is for IPA
    2019-11-20T11:31:27Z DEBUG Naming context 'dc=laptop,dc=example,dc=org' is a valid IPA context
    2019-11-20T11:31:27Z DEBUG Search for (objectClass=krbRealmContainer) in dc=laptop,dc=example,dc=org (sub)
    2019-11-20T11:31:27Z DEBUG Found: cn=LAPTOP.EXAMPLE.ORG,cn=kerberos,dc=laptop,dc=example,dc=org
    2019-11-20T11:31:27Z DEBUG Discovery result: Success; server=ipa0.laptop.example.org, domain=laptop.example.org, kdc=ipa0.laptop.example.org, basedn=dc=laptop,dc=example,dc=org
    2019-11-20T11:31:27Z DEBUG Validated servers: ipa0.laptop.example.org
    2019-11-20T11:31:27Z DEBUG will use discovered domain: laptop.example.org
    2019-11-20T11:31:27Z DEBUG Using servers from command line, disabling DNS discovery
    2019-11-20T11:31:27Z DEBUG will use provided server: ipa0.laptop.example.org
    2019-11-20T11:31:27Z DEBUG will use discovered realm: LAPTOP.EXAMPLE.ORG
    2019-11-20T11:31:27Z DEBUG will use discovered basedn: dc=laptop,dc=example,dc=org

    Example:
        >>> ipaclientinstalllog = shared[IpaclientInstallLog]
        >>> len(list(log.get('DEBUG')))
        27
        >>> from datetime import datetime
        >>> len(log.get_after(datetime(2019, 10, 1, 1, 1, 1)))
        28
    """
    time_format = '%Y-%m-%dT%H:%M:%SZ'
