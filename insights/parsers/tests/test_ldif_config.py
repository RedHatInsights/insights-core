import doctest
import pytest
from insights.tests import context_wrap
from insights.parsers import ldif_config, SkipException
from insights.parsers.ldif_config import LDIFParser

LDIF_CONFIG = """
dn:
aci: (targetattr != "aci")(version 3.0; aci "rootdse anon read access"; allow(
 read,search,compare) userdn="ldap:///anyone";)
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=Directory Manager
modifyTimestamp: 20210608144722Z
nsslapd-return-default-opattr: namingContexts
nsslapd-return-default-opattr: supportedControl
nsslapd-return-default-opattr: supportedExtension
nsslapd-return-default-opattr: supportedLDAPVersion
nsslapd-return-default-opattr: supportedSASLMechanisms
nsslapd-return-default-opattr: vendorName
nsslapd-return-default-opattr: vendorVersion
objectClass: top

dn: cn=config
aci: (targetattr != aci)(version 3.0; aci "cert manager read access"; allow (r
 ead, search, compare) userdn = "ldap:///uid=pkidbuser,ou=people,o=ipaca";)
aci: (target = "ldap:///cn=automember rebuild membership,cn=tasks,cn=config")(
 targetattr=*)(version 3.0;acl "permission:Add Automember Rebuil Membership T
 ask";allow (add) groupdn = "ldap:///cn=Add Automember Rebuild Membership Task
 ,cn=permissions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
aci: (targetattr = "cn || createtimestamp || entryusn || modifytimestamp || ob
 jectclass || passsyncmanagersdns*")(target = "ldap:///cn=ipa_pwd_extop,cn=plu
 gins,cn=config")(version 3.0;acl "permission:Read PassSync Managers Configura
 tion";allow (compare,read,search) groupdn = "ldap:///cn=Read PassSync Manager
 s Configuration,cn=permissions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
cn: config1111
cn: config2222
cn1:: IGJlZ2lucyB3aXRoIGEgc3BhY2U=
cn2:< file:///tmp/value
modifiersName: cn=directory manager
modifyTimestamp: 20210609192548Z
objectClass: nsslapdConfig
CACertExtractFile: /etc/dirsrv/slapd-IDM-NYPD-FINEST/IDM.NYPD.FINEST20IPA20CA.
 pem
numSubordinates: 14
nsslapd-errorlog-level: 81920
nsslapd-rootpw: {SSHA512}mdrYu17fr9ukhID6B6/aMHE1KeMhWLwVfP3y2LSNtTFaMkRPf340X
 MGEN/ocUoAyykmDSMxVcF3ajVR3+f5mqmNqxUek9PYT

dn: cn=monitor
aci: (target ="ldap:///cn=monitor*")(targetattr != "aci || connection")(versio
 n 3.0; acl "monitor"; allow( read, search, compare ) userdn = "ldap:///anyone
 ";)
cn: monitor
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20201026161200Z
objectClass: top
objectClass: extensibleObject
numSubordinates: 3

dn: cn=changelog5,cn=config
cn: changelog5
createTimestamp: 20201026161228Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161228Z
nsslapd-changelogdir: /var/lib/dirsrv/slapd-IDM-NYPD-FINEST/cldb
nsslapd-changelogmaxage: 7d
objectClass: top
objectClass: extensibleobject

dn: cn=encryption,cn=config
CACertExtractFile: /etc/dirsrv/slapd-IDM-NYPD-FINEST/IDM.NYPD.FINEST20IPA20CA.
 pem
allowWeakCipher: off
cn: encryption
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20201026161252Z
nsSSL3Ciphers: default
nsSSLClientAuth: allowed
nsSSLSessionTimeout: 0
objectClass: top
objectClass: nsEncryptionConfig
sslVersionMin: TLS1.0
numSubordinates: 1

dn: cn=features,cn=config
cn: features
objectClass: top
objectClass: nsContainer
numSubordinates: 5

dn: cn=mapping tree,cn=config
aci: (targetattr = "cn || createtimestamp || description || entryusn || modify
 timestamp || nsds50ruv || nsds5beginreplicarefresh || nsds5debugreplicatimeou
 t || nsds5flags || nsds5replicaabortcleanruv || nsds5replicaautoreferral || n
 sds5replicabackoffmax || nsds5replicabackoffmin || nsds5replicabinddn || nsds
 5replicabindmethod || nsds5replicabusywaittime || nsds5replicachangecount ||
 nsds5replicachangessentsincestartup || nsds5replicacleanruv || nsds5replicacl
 eanruvnotified || nsds5replicacredentials || nsds5replicaenabled || nsds5repl
 icahost || nsds5replicaid || nsds5replicalastinitend || nsds5replicalastinits
 tart || nsds5replicalastinitstatus || nsds5replicalastupdateend || nsds5repli
 calastupdatestart || nsds5replicalastupdatestatus || nsds5replicalegacyconsum
 er || nsds5replicaname || nsds5replicaport || nsds5replicaprotocoltimeout ||
 nsds5replicapurgedelay || nsds5replicareferral || nsds5replicaroot || nsds5re
 plicasessionpausetime || nsds5replicastripattrs || nsds5replicatedattributeli
 st || nsds5replicatedattributelisttotal || nsds5replicatimeout || nsds5replic
 atombstonepurgeinterval || nsds5replicatransportinfo || nsds5replicatype || n
 sds5replicaupdateinprogress || nsds5replicaupdateschedule || nsds5task || nsd
 s7directoryreplicasubtree || nsds7dirsynccookie || nsds7newwingroupsyncenable
 d || nsds7newwinusersyncenabled || nsds7windowsdomain || nsds7windowsreplicas
 ubtree || nsruvreplicalastmodified || nsstate || objectclass || onewaysync ||
  winsyncdirectoryfilter || winsyncinterval || winsyncmoveaction || winsyncsub
 treepair || winsyncwindowsfilter")(targetfilter = "(|(objectclass=nsds5Replic
 a)(objectclass=nsds5replicationagreement)(objectclass=nsDSWindowsReplicationA
 greement)(objectClass=nsMappingTree))")(version 3.0;acl "permission:Read Repl
 ication Agreements";allow (compare,read,search) groupdn = "ldap:///cn=Read Re
 plication Agreements,cn=permissions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
aci: (targetattr=*)(version 3.0;acl "permission:Add Replication Agreements";al
 low (add) groupdn = "ldap:///cn=Add Replication Agreements,cn=permissions,cn=
 pbac,dc=idm,dc=nypd,dc=finest";)
aci: (targetattr=*)(targetfilter="(|(objectclass=nsds5Replica)(objectclass=nsd
 s5replicationagreement)(objectclass=nsDSWindowsReplicationAgreement)(objectCl
 ass=nsMappingTree))")(version 3.0; acl "permission:Modify Replication Agreeme
 nts"; allow (read, write, search) groupdn = "ldap:///cn=Modify Replication Ag
 reements,cn=permissions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
aci: (targetattr=*)(targetfilter="(|(objectclass=nsds5replicationagreement)(ob
 jectclass=nsDSWindowsReplicationAgreement))")(version 3.0;acl "permission:Rem
 ove Replication Agreements";allow (delete) groupdn = "ldap:///cn=Remove Repli
 cation Agreements,cn=permissions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
aci: (target = "ldap:///cn=meTo($dn),cn=*,cn=mapping tree,cn=config")(targetat
 tr = "objectclass || cn")(version 3.0; acl "Allow hosts to read their replica
 tion agreements"; allow(read, search, compare) userdn = "ldap:///fqdn=($dn),c
 n=computers,cn=accounts,dc=idm,dc=nypd,dc=finest";)
cn: mapping tree
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161600Z
objectClass: top
objectClass: extensibleObject
numSubordinates: 3

dn: cn=sasl,cn=config
cn: sasl
objectClass: top
objectClass: nsContainer
numSubordinates: 1
"""

LDIF_CONFIG_EMPTY = ""


def test_ldip_parser():
    ldif_config = LDIFParser(context_wrap(LDIF_CONFIG))
    assert ldif_config[1]['dn: cn=config']['modifiersName'] == 'cn=directory manager'
    assert ldif_config[1]['dn: cn=config']['modifyTimestamp'] == '20210609192548Z'
    assert ldif_config[1]['dn: cn=config']['objectClass'] == 'nsslapdConfig'
    assert ldif_config[3]['dn: cn=changelog5,cn=config']['cn'] == 'changelog5'
    assert ldif_config[3]['dn: cn=changelog5,cn=config']['createTimestamp'] == '20201026161228Z'
    assert ldif_config[3]['dn: cn=changelog5,cn=config']['creatorsName'] == 'cn=Directory Manager'
    assert ldif_config[3]['dn: cn=changelog5,cn=config']['nsslapd-changelogdir'] == '/var/lib/dirsrv/slapd-IDM-NYPD-FINEST/cldb'
    assert ldif_config[3]['dn: cn=changelog5,cn=config']['objectClass'] == 'extensibleobject'


def test_empty():
    with pytest.raises(SkipException) as e:
        LDIFParser(context_wrap(LDIF_CONFIG_EMPTY))
    assert 'The file is empty' in str(e)


def test_ldif_config_doc_examples():
    env = {
        'ldif_config': LDIFParser(context_wrap(LDIF_CONFIG)),
    }
    failed, total = doctest.testmod(ldif_config, globs=env)
    assert failed == 0
