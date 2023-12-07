# -*- coding: utf-8 -*-

import doctest
import pytest

from insights.parsers import dse_ldif
from insights.parsers.dse_ldif import DseLDIF
from insights.tests import context_wrap
from insights.core.exceptions import SkipComponent

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
dn: cn=features,cn=config
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
dn: cn=features,cn=config
nsslapd-security: o
 n
some-line-wo-colon
sslVersionMax:: VExTMS4yIA==
sslVersionMin:< file:///tmp/somefile
nsSSL3: on
userCertificate;binary:< file:BabsCert
"""

DSE_LDIF_DN_TEST = """
dn: cn=somefirst,cn=config
cn: config

dn: cn=somesecond,cn=config

dn:
cn: config

dn: cn=features,cn=config
cn: config
nsslapd-security: on
sslVersionMin: TLS1.0
sslVersionMax: TLS1.1
nsSSL3: on
"""

DSE_LDIF_EMPTY = ""

DSE_LDIF_EMPTY_PARSED = """
#dn: cn=features,cn=config
#cn: config
#nsslapd-security: on
"""

DSE_LDIF_DOCTEST = """
dn: cn=config
nsslapd-return-default-opattr: namingContexts
nsslapd-return-default-opattr: supportedControl
nsslapd-securePort: 636
nsslapd-security: on

dn: cn=encryption,cn=config
sslVersionMin: SSLv3
sslVersionMax: TLS1.1
nsSSL3: on
"""


def test_dse_ldif_filtered():
    dse_ldif = DseLDIF(context_wrap(DSE_LDIF_REAL_EXAMPLE))
    assert len(dse_ldif) == 4

    group = dse_ldif[0]
    assert group["dn"] == ["cn=config"]
    assert group["cn"] == ["config"]
    assert group["nsslapd-security"] == ["on"]
    assert group["objectClass"] == ['top', 'extensibleObject', 'nsslapdConfig']
    assert group["numSubordinates"] == ['10']
    assert group['aci'][-1] == '(targetattr = "*")(version 3.0; acl "SIE Group"; allow (all) groupdn = "l'


def test_dse_ldif_smoke():
    dse_ldif = DseLDIF(context_wrap(DSE_LDIF_SMOKE))
    assert len(dse_ldif) == 1

    group = dse_ldif[0]
    expected = {
        "dn": "cn=features,cn=config",
        "cn": "config",
        "nsslapd-security": "on",
        "sslVersionMin": "TLS1.0",
        "sslVersionMax": "TLS1.1",
        "nsSSL3": "on",
    }
    for k, v in expected.items():
        assert [v] == group[k]


def test_dse_ldif_coverage():
    dse_ldif = DseLDIF(context_wrap(DSE_LDIF_COVERAGE))
    assert len(dse_ldif) == 1

    group = dse_ldif[0]
    expected = {
        "dn": "cn=features,cn=config",
        "nsSSL3": "on",
        "nsslapd-security": "o",
    }
    for k, v in expected.items():
        assert [v] == group[k]


def test_dse_ldif_dn():
    dse_ldif = DseLDIF(context_wrap(DSE_LDIF_DN_TEST))
    assert len(dse_ldif) == 4

    assert dse_ldif[0]["dn"] == ["cn=somefirst,cn=config"]
    assert dse_ldif[0]["cn"] == ["config"]
    assert dse_ldif[1]["dn"] == ["cn=somesecond,cn=config"]
    assert dse_ldif[2]["dn"] == [""]
    assert dse_ldif[2]["cn"] == ["config"]
    assert dse_ldif[3]["dn"] == ["cn=features,cn=config"]
    assert dse_ldif[3]["nsSSL3"] == ["on"]


def test_dse_ldif_empty():
    with pytest.raises(SkipComponent) as e:
        DseLDIF(context_wrap(DSE_LDIF_EMPTY))
    assert 'Empty file content' in str(e)

    with pytest.raises(SkipComponent) as e:
        DseLDIF(context_wrap(DSE_LDIF_EMPTY_PARSED))
    assert 'No valid content' in str(e)


def test_doc_examples():
    env = {
        "dse_ldif": DseLDIF(context_wrap(DSE_LDIF_DOCTEST)),
    }
    failed, total = doctest.testmod(dse_ldif, globs=env)
    assert failed == 0
