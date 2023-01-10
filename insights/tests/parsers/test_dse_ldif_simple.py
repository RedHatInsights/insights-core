# -*- coding: utf-8 -*-

import doctest

from insights import add_filter
from insights.parsers import dse_ldif_simple
from insights.parsers.dse_ldif_simple import DseLdifSimple
from insights.specs import Specs
from insights.tests import context_wrap

DSE_LDIF_REAL_EXAMPLE = """

dn: cn=config
cn: config
objectClass: top
objectClass: extensibleObject
objectClass: nsslapdConfig
nsslapd-schemadir: /etc/dirsrv/slapd-dir/schema
nsslapd-lockdir: /var/lock/dirsrv/slapd-dir
nsslapd-tmpdir: /tmp
nsslapd-certdir: /etc/dirsrv/slapd-dir
nsslapd-ldifdir: /var/lib/dirsrv/slapd-dir/ldif
nsslapd-bakdir: /var/lib/dirsrv/slapd-dir/bak
nsslapd-rundir: /var/run/dirsrv
nsslapd-instancedir: /usr/lib64/dirsrv/slapd-dir
nsslapd-accesslog: /var/log/dirsrv/slapd-dir/access
nsslapd-localhost: testinstance.local
nsslapd-port: 389
nsslapd-localuser: dirsrv
nsslapd-errorlog: /var/log/dirsrv/slapd-dir/errors
nsslapd-auditlog: /var/log/dirsrv/slapd-dir/audit
nsslapd-auditfaillog: /var/log/dirsrv/slapd-dir/audit
nsslapd-rootdn: cn=Directory Manager
nsslapd-ldapifilepath: /var/run/slapd-dir.socket
nsslapd-ldapilisten: off
nsslapd-ldapiautobind: off
nsslapd-ldapimaprootdn: cn=Directory Manager
nsslapd-ldapimaptoentries: off
nsslapd-ldapiuidnumbertype: uidNumber
nsslapd-ldapigidnumbertype: gidNumber
nsslapd-ldapientrysearchbase: dc=testinstance,dc=local
nsslapd-defaultnamingcontext: dc=testinstance,dc=local
aci: (targetattr="*")(version 3.0; acl "Configuration Administrators Group"; a
 llow (all) groupdn="ldap:///cn=Configuration Administrators,ou=Groups,ou=Topo
 logyManagement,o=NetscapeRoot";)
aci: (targetattr="*")(version 3.0; acl "Configuration Administrator"; allow (a
 ll) userdn="ldap:///uid=admin,ou=Administrators,ou=TopologyManagement,o=Netsc
 apeRoot";)
aci: (targetattr = "*")(version 3.0; acl "SIE Group"; allow (all) groupdn = "l
 dap:///cn=slapd-dir,cn=Red Hat Directory Server,cn=Server Group,cn=testinstan
 ce.local,ou=testinstance.local,o=NetscapeRoot";)
modifiersName: cn=directory manager
modifyTimestamp: 20211015231914Z
nsslapd-securePort: 636
nsslapd-security: on
nsslapd-rootpw: {SSHA512}la6KbVGTR3XKHN6CoZ/PcYvOrS7qGAVSC9kjvGtyuPzSJGbHXReTs
 FUBF6QnP0jHAONEx4784x6PNPcMzTOdpoJw0gOQkXKM
numSubordinates: 10


dn: cn=monitor
objectClass: top
objectClass: extensibleObject
cn: monitor
aci: (target ="ldap:///cn=monitor*")(targetattr != "aci || connection")(versio
 n 3.0; acl "monitor"; allow( read, search, compare ) userdn = "ldap:///anyone
 ";)
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
createTimestamp: 20211015215626Z
modifyTimestamp: 20211015215626Z
numSubordinates: 3

dn: cn=encryption,cn=config
objectClass: top
objectClass: nsEncryptionConfig
cn: encryption
nsSSLSessionTimeout: 0
nsSSLClientAuth: allowed
sslVersionMin: TLS1.0
sslVersionMax: TLS1.1
nsSSL3: on
nsTLS1: on
allowWeakCipher: on
nsSSL3Ciphers: +all
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
createTimestamp: 20211015215626Z
modifyTimestamp: 20211015231142Z
CACertExtractFile: /etc/dirsrv/slapd-dir/server-cert.pem
numSubordinates: 1

dn: cn=features,cn=config
objectClass: top
objectClass: nsContainer
cn: features
numSubordinates: 5

"""

DSE_LDIF_SMOKE = """
cn: config
nsslapd-security: on
sslVersionMin: TLS1.0
sslVersionMax: TLS1.1
nsSSL3: on
# a comment : with a colon
"""

# This is purely for coverage testing. Real deployments don't use these features
# for these attributes.
DSE_LDIF_COVERAGE = """
# a comment
nsslapd-security: o
 n
sslVersionMax:: VExTMS4yIA==
sslVersionMin:< file:///tmp/somefile
nsSSL3: on
"""

DSE_LDIF_DOCTEST = """
dn: cn=config
nsslapd-securePort: 636
nsslapd-security: on

dn: cn=encryption,cn=config
sslVersionMin: SSLv3
sslVersionMax: TLS1.1
nsSSL3: on
"""


def test_dse_ldif_smoke():
    dse_ldif_simple = DseLdifSimple(context_wrap(DSE_LDIF_SMOKE))
    assert None is dse_ldif_simple.get("asdf")
    assert len(dse_ldif_simple) == 5
    expected = {
        "cn": "config",  # just a canary to detect spec collection status
        "nsslapd-security": "on",
        "sslVersionMin": "TLS1.0",
        "sslVersionMax": "TLS1.1",
        "nsSSL3": "on",
    }
    assert dict(dse_ldif_simple) == expected
    assert dse_ldif_simple["nsslapd-security"] == "on"
    assert "sslVersionMin" in dse_ldif_simple
    for k in dse_ldif_simple:
        assert expected[k] == dse_ldif_simple[k]
        assert expected[k] == dse_ldif_simple.get(k)


def test_dse_ldif_coverage():
    dse_ldif_simple = DseLdifSimple(context_wrap(DSE_LDIF_COVERAGE))
    assert "sslVersionMin" not in dse_ldif_simple
    assert "sslVersionMax" not in dse_ldif_simple
    assert "nsSSL3" in dse_ldif_simple
    assert len(dse_ldif_simple) == 2
    expected = {
        "nsSSL3": "on",
        # This doesn't happen in real deployments because 389-ds automatically
        # reformats it back to a single line.
        "nsslapd-security": "o",
    }
    assert dict(dse_ldif_simple) == expected


def test_dse_ldif_filtered():
    add_filter(
        Specs.dse_ldif, [
            "nsslapd-security",
            "sslVersionMin",
            "sslVersionMax",
            "nsSSL3",
            "cn: config",  # Note that this can serve as a canary for knowing whether the spec is collected.
        ]
    )

    dse_ldif_simple = DseLdifSimple(context_wrap(DSE_LDIF_REAL_EXAMPLE, filtered_spec=Specs.dse_ldif))
    assert dse_ldif_simple["nsslapd-security"] == "on"
    assert len(dse_ldif_simple) == 6
    expected = {
        "cn": "config",  # just a canary to detect spec collection status
        "nsslapd-security": "on",
        "sslVersionMin": "TLS1.0",
        "sslVersionMax": "TLS1.1",
        "nsSSL3": "on",
        "nsSSL3Ciphers": "+all",
    }
    assert dict(dse_ldif_simple) == expected


def test_doc_examples():
    env = {
        "dse_ldif_simple": DseLdifSimple(context_wrap(DSE_LDIF_DOCTEST)),
    }
    failed, total = doctest.testmod(dse_ldif_simple, globs=env)
    assert failed == 0
