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
 targetattr=*)(version 3.0;acl "permission:Add Automember Rebuild Membership T
 ask";allow (add) groupdn = "ldap:///cn=Add Automember Rebuild Membership Task
 ,cn=permissions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
aci: (targetattr = "cn || createtimestamp || entryusn || modifytimestamp || ob
 jectclass || passsyncmanagersdns*")(target = "ldap:///cn=ipa_pwd_extop,cn=plu
 gins,cn=config")(version 3.0;acl "permission:Read PassSync Managers Configura
 tion";allow (compare,read,search) groupdn = "ldap:///cn=Read PassSync Manager
 s Configuration,cn=permissions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
aci: (targetattr = "passsyncmanagersdns*")(target = "ldap:///cn=ipa_pwd_extop,
 cn=plugins,cn=config")(version 3.0;acl "permission:Modify PassSync Managers C
 onfiguration";allow (write) groupdn = "ldap:///cn=Modify PassSync Managers Co
 nfiguration,cn=permissions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
aci: (targetattr = "cn || createtimestamp || entryusn || modifytimestamp || ns
 slapd-directory* || objectclass")(target = "ldap:///cn=config,cn=ldbm databas
 e,cn=plugins,cn=config")(version 3.0;acl "permission:Read LDBM Database Confi
 guration";allow (compare,read,search) groupdn = "ldap:///cn=Read LDBM Databas
 e Configuration,cn=permissions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
aci: (version 3.0;acl "permission:Add Configuration Sub-Entries";allow (add) g
 roupdn = "ldap:///cn=Add Configuration Sub-Entries,cn=permissions,cn=pbac,dc=
 idm,dc=nypd,dc=finest";)
cn: config
modifiersName: cn=directory manager
modifyTimestamp: 20210609192548Z
nsslapd-accesslog: /var/log/dirsrv/slapd-IDM-NYPD-FINEST/access
nsslapd-allow-hashed-passwords: on
nsslapd-anonlimitsdn: cn=anonymous-limits,cn=etc,dc=idm,dc=nypd,dc=finest
nsslapd-auditfaillog: /var/log/dirsrv/slapd-IDM-NYPD-FINEST/audit
nsslapd-auditlog: /var/log/dirsrv/slapd-IDM-NYPD-FINEST/audit
nsslapd-bakdir: /var/lib/dirsrv/slapd-IDM-NYPD-FINEST/bak
nsslapd-certdir: /etc/dirsrv/slapd-IDM-NYPD-FINEST
nsslapd-defaultnamingcontext: dc=idm,dc=nypd,dc=finest
nsslapd-entryusn-global: on
nsslapd-entryusn-import-initval: next
nsslapd-errorlog: /var/log/dirsrv/slapd-IDM-NYPD-FINEST/errors
nsslapd-ignore-time-skew: off
nsslapd-instancedir: /var/lib/dirsrv/scripts-IDM-NYPD-FINEST
nsslapd-ioblocktimeout: 10000
nsslapd-ldapiautobind: on
nsslapd-ldapifilepath: /var/run/slapd-IDM-NYPD-FINEST.socket
nsslapd-ldapigidnumbertype: gidNumber
nsslapd-ldapilisten: on
nsslapd-ldapimaprootdn: cn=Directory Manager
nsslapd-ldapimaptoentries: on
nsslapd-ldapiuidnumbertype: uidNumber
nsslapd-ldifdir: /var/lib/dirsrv/slapd-IDM-NYPD-FINEST/ldif
nsslapd-localhost: smdc-rhidm01p.idm.nypd.finest
nsslapd-localuser: dirsrv
nsslapd-lockdir: /var/lock/dirsrv/slapd-IDM-NYPD-FINEST
nsslapd-maxbersize: 209715200
nsslapd-minssf-exclude-rootdse: on
nsslapd-ndn-cache-enabled: on
nsslapd-port: 389
nsslapd-rootdn: cn=Directory Manager
nsslapd-rundir: /var/run/dirsrv
nsslapd-sasl-mapping-fallback: on
nsslapd-schemadir: /etc/dirsrv/slapd-IDM-NYPD-FINEST/schema
nsslapd-security: on
nsslapd-tmpdir: /tmp
nsslapd-unhashed-pw-switch: nolog
objectClass: top
objectClass: extensibleObject
objectClass: nsslapdConfig
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

dn: cn=plugin default config,cn=config
cn: plugin default config
createTimestamp: 20201026161220Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20201026161220Z
nsDS5ReplicatedAttributeList: (objectclass=*) $ EXCLUDE entryusn
objectClass: top
objectClass: extensibleObject

dn: cn=plugins,cn=config
cn: plugins
objectClass: top
objectClass: nsContainer
numSubordinates: 87

dn: cn=replication,cn=config
cn: replication
objectClass: top
objectClass: nsContainer

dn: cn=replSchema,cn=config
cn: replSchema
createTimestamp: 20201026161205Z
creatorsName: cn=Multimaster Replication Plugin,cn=plugins,cn=config
modifiersName: cn=Multimaster Replication Plugin,cn=plugins,cn=config
modifyTimestamp: 20201026161205Z
objectClass: top
objectClass: nsSchemaPolicy
numSubordinates: 2

dn: cn=root-autobind,cn=config
cn: root-autobind
createTimestamp: 20201026161205Z
creatorsName: cn=directory manager
gidNumber: 0
modifiersName: cn=directory manager
modifyTimestamp: 20201026161205Z
objectClass: extensibleObject
objectClass: top
uidNumber: 0

dn: cn=sasl,cn=config
cn: sasl
objectClass: top
objectClass: nsContainer
numSubordinates: 1

dn: cn=SNMP,cn=config
cn: SNMP
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20201026161200Z
nsSNMPEnabled: on
objectClass: top
objectClass: nsSNMP

dn: cn=tasks,cn=config
aci: (targetattr=*)(version 3.0; acl "Run tasks after replica re-initializatio
 n"; allow (add) groupdn = "ldap:///cn=Modify Replication Agreements,cn=permis
 sions,cn=pbac,dc=idm,dc=nypd,dc=finest";)
aci: (targetattr=*)(version 3.0; acl "cert manager: Run tasks after replica re
 -initialization"; allow (add) userdn = "ldap:///uid=pkidbuser,ou=people,o=ipa
 ca";)
aci: (targetattr="*")(version 3.0; acl "Admin can read all tasks"; allow (read
 , compare, search) groupdn = "ldap:///cn=admins,cn=groups,cn=accounts,dc=idm,
 dc=nypd,dc=finest";)
cn: tasks
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161600Z
objectClass: top
objectClass: extensibleObject
numSubordinates: 40

dn: cn=uniqueid generator,cn=config
cn: uniqueid generator
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20210609174655Z
nsState:: gFEQrkrJ6wHFFhjQIQjhigAAAAAAAAAA
objectClass: top
objectClass: extensibleObject

dn: ou=csusers,cn=config
aci: (targetattr != aci)(version 3.0; aci "cert manager manage replication use
 rs"; allow (all) userdn = "ldap:///uid=pkidbuser,ou=people,o=ipaca";)
createTimestamp: 20201026161439Z
creatorsName: cn=directory manager
modifiersName: cn=directory manager
modifyTimestamp: 20201026161439Z
objectClass: top
objectClass: organizationalUnit
ou: csusers

dn: cn=counters,cn=monitor
cn: counters
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20201026161200Z
objectClass: top
objectClass: extensibleObject

dn: cn=snmp,cn=monitor
cn: snmp
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20201026161200Z
objectClass: top
objectClass: extensibleObject

dn: cn=RSA,cn=encryption,cn=config
cn: RSA
createTimestamp: 20201026161249Z
creatorsName: cn=directory manager
modifiersName: cn=directory manager
modifyTimestamp: 20201026161249Z
nsSSLActivation: on
nsSSLPersonalitySSL: Server-Cert
nsSSLToken: internal (software)
objectClass: top
objectClass: nsEncryptionModule

dn: cn=options,cn=features,cn=config
cn: options
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20201026161200Z
objectClass: top
objectClass: nsContainer

dn: oid=1.3.6.1.4.1.42.2.27.9.5.8,cn=features,cn=config
cn: Account Usable Request Control
objectClass: top
objectClass: directoryServerFeature
oid: 1.3.6.1.4.1.42.2.27.9.5.8

dn: oid=1.3.6.1.4.1.4203.1.9.1.1,cn=features,cn=config
aci: (targetattr != "aci")(version 3.0; acl "Sync Request Control"; allow( rea
 d, search ) userdn = "ldap:///all";)
cn: Sync Request Control
objectClass: top
objectClass: directoryServerFeature
oid: 1.3.6.1.4.1.4203.1.9.1.1

dn: oid=2.16.840.1.113730.3.4.9,cn=features,cn=config
aci: (targetattr !="aci")(version 3.0; acl "VLV Request Control"; allow (read,
  search, compare, proxy) userdn = "ldap:///anyone"; )
cn: VLV Request Control
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161615Z
objectClass: top
objectClass: directoryServerFeature
oid: 2.16.840.1.113730.3.4.9

dn: oid=2.16.840.1.113730.3.5.7,cn=features,cn=config
cn: Bulk Import
createTimestamp: 20201026161200Z
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20201026161200Z
objectClass: top
objectClass: directoryServerFeature
oid: 2.16.840.1.113730.3.5.7

dn: cn=cn\3Dchangelog,cn=mapping tree,cn=config
cn: cn=changelog
createTimestamp: 20201026161625Z
creatorsName: cn=Retro Changelog Plugin,cn=plugins,cn=config
modifiersName: cn=Retro Changelog Plugin,cn=plugins,cn=config
modifyTimestamp: 20201026161625Z
nsslapd-backend: changelog
nsslapd-state: backend
objectClass: top
objectClass: extensibleObject
objectClass: nsMappingTree

dn: cn=dc\3Didm\2Cdc\3Dnypd\2Cdc\3Dfinest,cn=mapping tree,cn=config
cn: dc=idm,dc=nypd,dc=finest
cn: "dc=idm,dc=nypd,dc=finest"
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20210608144744Z
nsslapd-backend: userRoot
nsslapd-referral: ldap://s1pp-rhidm01p.idm.nypd.finest:389/dc%3Didm%2Cdc%3Dnyp
 d%2Cdc%3Dfinest
nsslapd-referral: ldap://smdc-rhidm02p.idm.nypd.finest:389/dc%3Didm%2Cdc%3Dnyp
 d%2Cdc%3Dfinest
nsslapd-referral: ldap://s1pp-rhidm02p.idm.nypd.finest:389/dc%3Didm%2Cdc%3Dnyp
 d%2Cdc%3Dfinest
nsslapd-referral: ldap://sps2-rhidm01p.idm.nypd.finest:389/dc%3Didm%2Cdc%3Dnyp
 d%2Cdc%3Dfinest
nsslapd-referral: ldap://sps2-rhidm02p.idm.nypd.finest:389/dc%3Didm%2Cdc%3Dnyp
 d%2Cdc%3Dfinest
nsslapd-state: backend
objectClass: top
objectClass: extensibleObject
objectClass: nsMappingTree
numSubordinates: 1

dn: cn=o\3Dipaca,cn=mapping tree,cn=config
aci: (targetattr=*)(version 3.0;acl "cert manager: Add Replication Agreements"
 ;allow (add) userdn = "ldap:///uid=pkidbuser,ou=people,o=ipaca";)
aci: (targetattr=*)(targetfilter="(|(objectclass=nsds5Replica)(objectclass=nsd
 s5replicationagreement)(objectclass=nsDSWindowsReplicationAgreement)(objectCl
 ass=nsMappingTree))")(version 3.0; acl "cert manager: Modify Replication Agre
 ements"; allow (read, write, search) userdn = "ldap:///uid=pkidbuser,ou=peopl
 e,o=ipaca";)
aci: (targetattr=*)(targetfilter="(|(objectclass=nsds5replicationagreement)(ob
 jectclass=nsDSWindowsReplicationAgreement))")(version 3.0;acl "cert manager:
 Remove Replication Agreements";allow (delete) userdn = "ldap:///uid=pkidbuser
 ,ou=people,o=ipaca";)
cn: o=ipaca
createTimestamp: 20201026161323Z
creatorsName: cn=Directory Manager
modifiersName: cn=server,cn=plugins,cn=config
modifyTimestamp: 20210608144744Z
nsslapd-backend: ipaca
nsslapd-referral: ldap://s1pp-rhidm01p.idm.nypd.finest:389/o%3Dipaca
nsslapd-referral: ldap://smdc-rhidm02p.idm.nypd.finest:389/o%3Dipaca
nsslapd-referral: ldap://s1pp-rhidm02p.idm.nypd.finest:389/o%3Dipaca
nsslapd-referral: ldap://sps2-rhidm01p.idm.nypd.finest:389/o%3Dipaca
nsslapd-referral: ldap://sps2-rhidm02p.idm.nypd.finest:389/o%3Dipaca
nsslapd-state: backend
objectClass: top
objectClass: extensibleObject
objectClass: nsMappingTree
numSubordinates: 1

dn: cn=7-bit check,cn=plugins,cn=config
cn: 7-bit check
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce  7-bit clean attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NS7bitAttr
nsslapd-pluginInitfunc: NS7bitAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: betxnpreoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
nsslapd-pluginarg0: uid
nsslapd-pluginarg1: mail
nsslapd-pluginarg2: ,
nsslapd-pluginarg3: dc=idm,dc=nypd,dc=finest
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Account Policy Plugin,cn=plugins,cn=config
cn: Account Policy Plugin
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: off
nsslapd-pluginId: none
nsslapd-pluginInitfunc: acct_policy_init
nsslapd-pluginPath: libacctpolicy-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
numSubordinates: 1

dn: cn=Account Usability Plugin,cn=plugins,cn=config
cn: Account Usability Plugin
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Account Usability Control plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: Account Usability Control
nsslapd-pluginInitfunc: auc_init
nsslapd-pluginPath: libacctusability-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ACL Plugin,cn=plugins,cn=config
cn: ACL Plugin
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: acl access check plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: acl
nsslapd-pluginInitfunc: acl_init
nsslapd-pluginPath: libacl-plugin
nsslapd-pluginType: accesscontrol
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ACL preoperation,cn=plugins,cn=config
cn: ACL preoperation
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: acl access check plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: acl
nsslapd-pluginInitfunc: acl_preopInit
nsslapd-pluginPath: libacl-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=attribute uniqueness,cn=plugins,cn=config
cn: attribute uniqueness
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: off
nsslapd-pluginId: none
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: betxnpreoperation
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-across-all-subtrees: off
uniqueness-attribute-name: uid
uniqueness-subtrees: dc=idm,dc=nypd,dc=finest

dn: cn=Auto Membership Plugin,cn=plugins,cn=config
automemberprocessmodifyops: on
cn: Auto Membership Plugin
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161233Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginConfigArea: cn=automember,cn=etc,dc=idm,dc=nypd,dc=finest
nsslapd-pluginDescription: Auto Membership plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: Auto Membership
nsslapd-pluginInitfunc: automember_init
nsslapd-pluginPath: libautomember-plugin
nsslapd-pluginType: betxnpreoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Binary Syntax,cn=plugins,cn=config
cn: Binary Syntax
nsslapd-pluginDescription: binary attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: bin-syntax
nsslapd-pluginInitfunc: bin_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Bit String Syntax,cn=plugins,cn=config
cn: Bit String
nsslapd-pluginDescription: Bit String attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: bitstring-syntax
nsslapd-pluginInitfunc: bitstring_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Bitwise Plugin,cn=plugins,cn=config
cn: Bitwise Plugin
nsslapd-pluginDescription: bitwise match plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: bitwise
nsslapd-pluginInitfunc: bitwise_init
nsslapd-pluginPath: libbitwise-plugin
nsslapd-pluginType: matchingRule
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Boolean Syntax,cn=plugins,cn=config
cn: Boolean Syntax
nsslapd-pluginDescription: Boolean attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: boolean-syntax
nsslapd-pluginInitfunc: boolean_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=caacl name uniqueness,cn=plugins,cn=config
cn: caacl name uniqueness
createTimestamp: 20201026161600Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161600Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce unique attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NSUniqueAttr
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-attribute-name: cn
uniqueness-subtrees: cn=caacls,cn=ca,dc=idm,dc=nypd,dc=finest

dn: cn=Case Exact String Syntax,cn=plugins,cn=config
cn: Case Exact String Syntax
nsslapd-pluginDescription: caseExactString attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: ces-syntax
nsslapd-pluginInitfunc: ces_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Case Ignore String Syntax,cn=plugins,cn=config
cn: Case Ignore String Syntax
nsslapd-pluginDescription: DirectoryString attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: directorystring-syntax
nsslapd-pluginInitfunc: cis_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=certificate store issuer/serial uniqueness,cn=plugins,cn=config
cn: certificate store issuer/serial uniqueness
createTimestamp: 20201026161600Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161600Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce unique attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NSUniqueAttr
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-attribute-name: ipaCertIssuerSerial
uniqueness-subtrees: cn=certificates,cn=ipa,cn=etc,dc=idm,dc=nypd,dc=finest

dn: cn=certificate store subject uniqueness,cn=plugins,cn=config
cn: certificate store subject uniqueness
createTimestamp: 20201026161600Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161600Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce unique attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NSUniqueAttr
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-attribute-name: ipaCertSubject
uniqueness-subtrees: cn=certificates,cn=ipa,cn=etc,dc=idm,dc=nypd,dc=finest

dn: cn=chaining database,cn=plugins,cn=config
cn: chaining database
nsslapd-pluginDescription: LDAP chaining backend database plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: chaining database
nsslapd-pluginInitfunc: chaining_back_init
nsslapd-pluginPath: libchainingdb-plugin
nsslapd-pluginType: database
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensi
numSubordinates: 2

dn: cn=Class of Service,cn=plugins,cn=config
cn: Class of Service
nsslapd-plugin-depends-on-named: State Change Plugin
nsslapd-plugin-depends-on-named: Views
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: class of service plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: cos
nsslapd-pluginInitfunc: cos_init
nsslapd-pluginPath: libcos-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Content Synchronization,cn=plugins,cn=config
cn: Content Synchronization
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161614Z
nsslapd-plugin-depends-on-named: Retro Changelog Plugin
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Context Synchronization (RFC4533) plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: content-sync-plugin
nsslapd-pluginInitfunc: sync_init
nsslapd-pluginPath: libcontentsync-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
nsslapd-pluginbetxn: on
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Country String Syntax,cn=plugins,cn=config
cn: Country String Syntax
nsslapd-pluginDescription: Country String attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: countrystring-syntax
nsslapd-pluginInitfunc: country_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Delivery Method Syntax,cn=plugins,cn=config
cn: Delivery Method Syntax
nsslapd-pluginDescription: Delivery Method attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: delivery-syntax
nsslapd-pluginInitfunc: delivery_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=deref,cn=plugins,cn=config
cn: deref
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Dereference plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: Dereference
nsslapd-pluginInitfunc: deref_init
nsslapd-pluginPath: libderef-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
objectClass: nsContainer

dn: cn=Distinguished Name Syntax,cn=plugins,cn=config
cn: Distinguished Name Syntax
nsslapd-pluginDescription: distinguished name attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: dn-syntax
nsslapd-pluginInitfunc: dn_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Distributed Numeric Assignment Plugin,cn=plugins,cn=config
cn: Distributed Numeric Assignment Plugin
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161233Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Distributed Numeric Assignment plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: Distributed Numeric Assignment
nsslapd-pluginInitfunc: dna_init
nsslapd-pluginPath: libdna-plugin
nsslapd-pluginType: bepreoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
objectClass: nsContainer
numSubordinates: 1

dn: cn=Enhanced Guide Syntax,cn=plugins,cn=config
cn: Enhanced Guide Syntax
nsslapd-pluginDescription: Enhanced Guide attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: enhancedguide-syntax
nsslapd-pluginInitfunc: enhancedguide_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Facsimile Telephone Number Syntax,cn=plugins,cn=config
cn: Facsimile Telephone Number Syntax
nsslapd-pluginDescription: Facsimile Telephone Number attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: facsimile-syntax
nsslapd-pluginInitfunc: facsimile_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Fax Syntax,cn=plugins,cn=config
cn: Fax Syntax
nsslapd-pluginDescription: Fax attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: fax-syntax
nsslapd-pluginInitfunc: fax_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Generalized Time Syntax,cn=plugins,cn=config
cn: Generalized Time Syntax
nsslapd-pluginDescription: GeneralizedTime attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: time-syntax
nsslapd-pluginInitfunc: time_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Guide Syntax,cn=plugins,cn=config
cn: Guide Syntax
nsslapd-pluginDescription: Guide attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: guide-syntax
nsslapd-pluginInitfunc: guide_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=HTTP Client,cn=plugins,cn=config
cn: HTTP Client
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: HTTP Client plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: http-client
nsslapd-pluginInitfunc: http_client_init
nsslapd-pluginPath: libhttp-client-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Integer Syntax,cn=plugins,cn=config
cn: Integer Syntax
nsslapd-pluginDescription: integer attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: int-syntax
nsslapd-pluginInitfunc: int_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Internationalization Plugin,cn=plugins,cn=config
cn: Internationalization Plugin
nsslapd-pluginDescription: internationalized ordering rule plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: orderingrule
nsslapd-pluginInitfunc: orderingRule_init
nsslapd-pluginPath: libcollation-plugin
nsslapd-pluginType: matchingRule
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
nsslapd-pluginarg0: /etc/dirsrv/slapd-IDM-NYPD-FINEST/slapd-collations.conf
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=IPA DNS,cn=plugins,cn=config
cn: IPA DNS
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: IPA DNS support plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: ipa_dns
nsslapd-pluginInitfunc: ipadns_init
nsslapd-pluginPath: libipa_dns.so
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: Red Hat, Inc.
nsslapd-pluginVersion: 1.0
objectClass: top
objectClass: nsslapdPlugin
objectClass: extensibleObject

dn: cn=IPA Lockout,cn=plugins,cn=config
cn: IPA Lockout
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: IPA Lockout plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: IPA Lockout
nsslapd-pluginInitfunc: ipalockout_init
nsslapd-pluginPath: libipa_lockout
nsslapd-pluginType: object
nsslapd-pluginVendor: Red Hat, Inc.
nsslapd-pluginVersion: 1.0
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=IPA MODRDN,cn=plugins,cn=config
cn: IPA MODRDN
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: IPA MODRDN plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: IPA MODRDN
nsslapd-pluginInitfunc: ipamodrdn_init
nsslapd-pluginPath: libipa_modrdn
nsslapd-pluginType: betxnpostoperation
nsslapd-pluginVendor: Red Hat, Inc.
nsslapd-pluginVersion: 1.0
nsslapd-pluginprecedence: 60
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
numSubordinates: 2

dn: cn=IPA OTP Counter,cn=plugins,cn=config
cn: IPA OTP Counter
createTimestamp: 20201026161615Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161615Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Ensure proper OTP token counter operation
nsslapd-pluginEnabled: on
nsslapd-pluginId: ipa-otp-counter
nsslapd-pluginInitfunc: ipa_otp_counter_init
nsslapd-pluginPath: libipa_otp_counter
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: FreeIPA
nsslapd-pluginVersion: FreeIPA/1.0
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=IPA OTP Last Token,cn=plugins,cn=config
cn: IPA OTP Last Token
createTimestamp: 20201026161615Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161615Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Protect the user's last active token
nsslapd-pluginEnabled: on
nsslapd-pluginId: ipa-otp-lasttoken
nsslapd-pluginInitfunc: ipa_otp_lasttoken_init
nsslapd-pluginPath: libipa_otp_lasttoken
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: FreeIPA
nsslapd-pluginVersion: FreeIPA/1.0
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=IPA Range-Check,cn=plugins,cn=config
cn: IPA Range-Check
createTimestamp: 20201026161615Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161615Z
nsslapd-basedn: dc=idm,dc=nypd,dc=finest
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Check if newly added or modified ID ranges do not o
 verlap with existing ones
nsslapd-pluginEnabled: on
nsslapd-pluginId: IPA ID range check plugin
nsslapd-pluginInitfunc: ipa_range_check_init
nsslapd-pluginPath: libipa_range_check
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: FreeIPA project
nsslapd-pluginVersion: FreeIPA/1.0
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=IPA SIDGEN,cn=plugins,cn=config
cn: IPA SIDGEN
createTimestamp: 20201026161233Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161233Z
nsslapd-basedn: dc=idm,dc=nypd,dc=finest
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Add a SID to newly added or modified objects with u
 id pr gid numbers
nsslapd-pluginEnabled: on
nsslapd-pluginId: IPA SIDGEN postop plugin
nsslapd-pluginInitfunc: ipa_sidgen_init
nsslapd-pluginPath: libipa_sidgen
nsslapd-pluginType: postoperation
nsslapd-pluginVendor: FreeIPA project
nsslapd-pluginVersion: FreeIPA/1.0
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=IPA Topology Configuration,cn=plugins,cn=config
cn: IPA Topology Configuration
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-named: ldbm database
nsslapd-plugin-depends-on-named: Multimaster Replication Plugin
nsslapd-pluginDescription: ipa-topology-plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: ipa-topology-plugin
nsslapd-pluginInitfunc: ipa_topo_init
nsslapd-pluginPath: libtopology
nsslapd-pluginType: object
nsslapd-pluginVendor: freeipa
nsslapd-pluginVersion: 1.0
nsslapd-topo-plugin-shared-binddngroup: cn=replication managers,cn=sysaccounts
 ,cn=etc,dc=idm,dc=nypd,dc=finest
nsslapd-topo-plugin-shared-config-base: cn=ipa,cn=etc,dc=idm,dc=nypd,dc=finest
nsslapd-topo-plugin-shared-replica-root: dc=idm,dc=nypd,dc=finest
nsslapd-topo-plugin-shared-replica-root: o=ipaca
nsslapd-topo-plugin-startup-delay: 20
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=IPA UUID,cn=plugins,cn=config
cn: IPA UUID
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: IPA UUID plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: IPA UUID
nsslapd-pluginInitfunc: ipauuid_init
nsslapd-pluginPath: libipa_uuid
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: Red Hat, Inc.
nsslapd-pluginVersion: 1.0
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
numSubordinates: 2

dn: cn=IPA Version Replication,cn=plugins,cn=config
cn: IPA Version Replication
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=directory manager
modifyTimestamp: 20201026161220Z
nsslapd-plugin-depends-on-named: Multimaster Replication Plugin
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: IPA Replication version plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: ipa-repl-version-plugin
nsslapd-pluginInitfunc: repl_version_plugin_init
nsslapd-pluginPath: libipa_repl_version
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: Red Hat, Inc.
nsslapd-pluginVersion: 1.0
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ipa-sidgen-task,cn=plugins,cn=config
cn: ipa-sidgen-task
createTimestamp: 20201026163859Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026163859Z
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: on
nsslapd-pluginId: none
nsslapd-pluginInitfunc: sidgen_task_init
nsslapd-pluginPath: libipa_sidgen_task
nsslapd-pluginType: object
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ipa-winsync,cn=plugins,cn=config
cn: ipa-winsync
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
ipawinsyncacctdisable: both
ipawinsyncdefaultgroupattr: ipaDefaultPrimaryGroup
ipawinsyncdefaultgroupfilter: (gidNumber=*)(objectclass=posixGroup)(objectclas
 s=groupOfNames)
ipawinsyncforcesync: true
ipawinsynchomedirattr: ipaHomesRootDir
ipawinsyncloginshellattr: ipaDefaultLoginShell
ipawinsyncnewentryfilter: (cn=ipaConfig)
ipawinsyncnewuserocattr: ipauserobjectclasses
ipawinsyncrealmattr: cn
ipawinsyncrealmfilter: (objectclass=krbRealmContainer)
ipawinsyncuserattr: uidNumber -1
ipawinsyncuserattr: gidNumber -1
ipawinsyncuserflatten: true
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161600Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: ipa winsync plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: ipa-winsync-plugin
nsslapd-pluginInitfunc: ipa_winsync_plugin_init
nsslapd-pluginPath: libipa_winsync
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: FreeIPA project
nsslapd-pluginVersion: FreeIPA/1.0
nsslapd-pluginprecedence: 60
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ipa_cldap,cn=plugins,cn=config
cn: ipa_cldap
createTimestamp: 20201026163859Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026163859Z
nsslapd-basedn: dc=idm,dc=nypd,dc=finest
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: MS/AD introperable CLDAP server
nsslapd-pluginEnabled: on
nsslapd-pluginId: CLDAP Server
nsslapd-pluginInitfunc: ipa_cldap_init
nsslapd-pluginPath: libipa_cldap
nsslapd-pluginType: postoperation
nsslapd-pluginVendor: FreeIPA project
nsslapd-pluginVersion: FreeIPA/3.0
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ipa_enrollment_extop,cn=plugins,cn=config
cn: ipa_enrollment_extop
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: IPA Enrollment Extended Operation plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: ipa-enrollment
nsslapd-pluginInitfunc: ipaenrollment_init
nsslapd-pluginPath: libipa_enrollment_extop
nsslapd-pluginType: extendedop
nsslapd-pluginVendor: IPA Project
nsslapd-pluginVersion: IPA/2.0
nsslapd-realmtree: dc=idm,dc=nypd,dc=finest
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ipa_extdom_extop,cn=plugins,cn=config
cn: ipa_extdom_extop
createTimestamp: 20201026161233Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161233Z
nsslapd-basedn: dc=idm,dc=nypd,dc=finest
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Support resolving IDs in trusted domains to names a
 nd back
nsslapd-pluginEnabled: on
nsslapd-pluginId: IPA trusted domain ID mapper
nsslapd-pluginInitfunc: ipa_extdom_init
nsslapd-pluginPath: libipa_extdom_extop
nsslapd-pluginType: extendedop
nsslapd-pluginVendor: FreeIPA project
nsslapd-pluginVersion: FreeIPA/1.0
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ipa_pwd_extop,cn=plugins,cn=config
cn: ipa_pwd_extop
createTimestamp: 20201026161233Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161600Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: IPA Password Extended Operation plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: IPA Password Manager
nsslapd-pluginInitfunc: ipapwd_init
nsslapd-pluginPath: libipa_pwd_extop
nsslapd-pluginType: extendedop
nsslapd-pluginVendor: FreeIPA project
nsslapd-pluginVersion: FreeIPA/1.0
nsslapd-pluginbetxn: on
nsslapd-pluginprecedence: 49
nsslapd-realmtree: dc=idm,dc=nypd,dc=finest
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ipaUniqueID uniqueness,cn=plugins,cn=config
cn: ipaUniqueID uniqueness
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce unique attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NSUniqueAttr
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-across-all-subtrees: on
uniqueness-attribute-name: ipaUniqueID
uniqueness-exclude-subtrees: cn=staged users,cn=accounts,cn=provisioning,dc=id
 m,dc=nypd,dc=finest
uniqueness-subtrees: dc=idm,dc=nypd,dc=finest

dn: cn=JPEG Syntax,cn=plugins,cn=config
cn: JPEG Syntax
nsslapd-pluginDescription: JPEG attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: jpeg-syntax
nsslapd-pluginInitfunc: jpeg_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=ipaUniqueID uniqueness,cn=plugins,cn=config
cn: ipaUniqueID uniqueness
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce unique attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NSUniqueAttr
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-across-all-subtrees: on
uniqueness-attribute-name: ipaUniqueID
uniqueness-exclude-subtrees: cn=staged users,cn=accounts,cn=provisioning,dc=id
 m,dc=nypd,dc=finest
uniqueness-subtrees: dc=idm,dc=nypd,dc=finest

dn: cn=JPEG Syntax,cn=plugins,cn=config
cn: JPEG Syntax
nsslapd-pluginDescription: JPEG attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: jpeg-syntax
nsslapd-pluginInitfunc: jpeg_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=krbPrincipalName uniqueness,cn=plugins,cn=config
cn: krbPrincipalName uniqueness
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce unique attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NSUniqueAttr
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-across-all-subtrees: on
uniqueness-attribute-name: krbPrincipalName
uniqueness-exclude-subtrees: cn=staged users,cn=accounts,cn=provisioning,dc=id
 m,dc=nypd,dc=finest
uniqueness-subtrees: dc=idm,dc=nypd,dc=finest

dn: cn=ldbm database,cn=plugins,cn=config
aci: (targetattr=*)(version 3.0; acl "Cert Manager access for VLV searches"; a
 llow (read) userdn="ldap:///uid=pkidbuser,ou=people,o=ipaca";)
cn: ldbm database
modifiersName: cn=directory manager
modifyTimestamp: 20201026161439Z
nsslapd-plugin-depends-on-type: Syntax
nsslapd-plugin-depends-on-type: matchingRule
nsslapd-pluginDescription: high-performance LDAP backend database plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: ldbm-backend
nsslapd-pluginInitfunc: ldbm_back_init
nsslapd-pluginPath: libback-ldbm
nsslapd-pluginType: database
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
numSubordinates: 5

dn: cn=Linked Attributes,cn=plugins,cn=config
cn: Linked Attributes
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Linked Attributes plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: Linked Attributes
nsslapd-pluginInitfunc: linked_attrs_init
nsslapd-pluginPath: liblinkedattrs-plugin
nsslapd-pluginType: betxnpreoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
objectClass: nsContainer

dn: cn=Managed Entries,cn=plugins,cn=config
cn: Managed Entries
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161214Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginConfigArea: cn=Definitions,cn=Managed Entries,cn=etc,dc=idm,dc=n
 ypd,dc=finest
nsslapd-pluginDescription: Managed Entries plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: Managed Entries
nsslapd-pluginInitfunc: mep_init
nsslapd-pluginPath: libmanagedentries-plugin
nsslapd-pluginType: betxnpreoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
objectClass: nsContainer

dn: cn=MemberOf Plugin,cn=plugins,cn=config
cn: MemberOf Plugin
memberofattr: memberOf
memberofentryscope: dc=idm,dc=nypd,dc=finest
memberofentryscopeexcludesubtree: cn=compat,dc=idm,dc=nypd,dc=finest
memberofentryscopeexcludesubtree: cn=provisioning,dc=idm,dc=nypd,dc=finest
memberofentryscopeexcludesubtree: cn=topology,cn=ipa,cn=etc,dc=idm,dc=nypd,dc=
 finest
memberofgroupattr: member
memberofgroupattr: memberUser
memberofgroupattr: memberHost
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161614Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: memberof plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: memberof
nsslapd-pluginInitfunc: memberof_postop_init
nsslapd-pluginPath: libmemberof-plugin
nsslapd-pluginType: betxnpostoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Multimaster Replication Plugin,cn=plugins,cn=config
cn: Multimaster Replication Plugin
nsslapd-plugin-depends-on-named: ldbm database
nsslapd-plugin-depends-on-named: AES
nsslapd-plugin-depends-on-named: Class of Service
nsslapd-pluginDescription: Multi-master Replication Plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: replication-multimaster
nsslapd-pluginInitfunc: replication_multimaster_plugin_init
nsslapd-pluginPath: libreplication-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
nsslapd-pluginbetxn: on
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Name And Optional UID Syntax,cn=plugins,cn=config
cn: Name And Optional UID Syntax
nsslapd-pluginDescription: Name And Optional UID attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: nameoptuid-syntax
nsslapd-pluginInitfunc: nameoptuid_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=netgroup uniqueness,cn=plugins,cn=config
cn: netgroup uniqueness
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce unique attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NSUniqueAttr
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-attribute-name: cn
uniqueness-subtrees: cn=ng,cn=alt,dc=idm,dc=nypd,dc=finest

dn: cn=NIS Server,cn=plugins,cn=config
nsslapd-pluginbetxn: on
cn: NIS Server
nis-tcp-wrappers-name: nis-server
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
nsslapd-pluginDescription: NIS Server Plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: nis-plugin
nsslapd-pluginVersion: 0.56.5 (betxn support available and enabled by default)
nsslapd-pluginPath: /usr/lib64/dirsrv/plugins/nisserver-plugin.so
nsslapd-pluginVendor: redhat.com
nsslapd-pluginType: object
nsslapd-pluginInitfunc: nis_plugin_init
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
createTimestamp: 20210608174736Z
modifyTimestamp: 20210608174736Z
numSubordinates: 8

dn: cn=Numeric String Syntax,cn=plugins,cn=config
cn: Numeric String Syntax
nsslapd-pluginDescription: numeric string attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: numstr-syntax
nsslapd-pluginInitfunc: numstr_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Octet String Syntax,cn=plugins,cn=config
cn: Octet String Syntax
nsslapd-pluginDescription: octet string attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: octetstring-syntax
nsslapd-pluginInitfunc: octetstring_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=OID Syntax,cn=plugins,cn=config
cn: OID Syntax
nsslapd-pluginDescription: OID attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: oid-syntax
nsslapd-pluginInitfunc: oid_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=PAM Pass Through Auth,cn=plugins,cn=config
cn: PAM Pass Through Auth
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: off
nsslapd-pluginId: none
nsslapd-pluginInitfunc: pam_passthruauth_init
nsslapd-pluginPath: libpam-passthru-plugin
nsslapd-pluginType: betxnpreoperation
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
nsslapd-pluginloadglobal: true
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
objectClass: pamConfig
pamExcludeSuffix: cn=config
pamFallback: FALSE
pamIDAttr: notUsedWithRDNMethod
pamIDMapMethod: RDN
pamMissingSuffix: ALLOW
pamSecure: TRUE
pamService: ldapserver

dn: cn=Pass Through Authentication,cn=plugins,cn=config
cn: Pass Through Authentication
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: off
nsslapd-pluginId: none
nsslapd-pluginInitfunc: passthruauth_init
nsslapd-pluginPath: libpassthru-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Password Storage Schemes,cn=plugins,cn=config
cn: Password Storage Schemes
objectClass: top
objectClass: nsContainer
numSubordinates: 19

dn: cn=Posix Winsync API,cn=plugins,cn=config
cn: Posix Winsync API
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: off
nsslapd-pluginId: none
nsslapd-pluginInitfunc: posix_winsync_plugin_init
nsslapd-pluginPath: libposix-winsync-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
nsslapd-pluginprecedence: 25
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
posixwinsynccreatememberoftask: false
posixwinsynclowercaseuid: false
posixwinsyncmapmemberuid: true
posixwinsyncmapnestedgrouping: false
posixwinsyncmssfuschema: false

dn: cn=Postal Address Syntax,cn=plugins,cn=config
cn: Postal Address Syntax
nsslapd-pluginDescription: Postal Address attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: postaladdress-syntax
nsslapd-pluginInitfunc: postal_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Printable String Syntax,cn=plugins,cn=config
cn: Printable String Syntax
nsslapd-pluginDescription: Printable String attribtue syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: printablestring-syntax
nsslapd-pluginInitfunc: printable_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=referential integrity postoperation,cn=plugins,cn=config
cn: referential integrity postoperation
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161614Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: referential integrity plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: referint
nsslapd-pluginInitfunc: referint_postop_init
nsslapd-pluginPath: libreferint-plugin
nsslapd-pluginType: betxnpostoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
nsslapd-plugincontainerscope: dc=idm,dc=nypd,dc=finest
nsslapd-pluginentryscope: dc=idm,dc=nypd,dc=finest
nsslapd-pluginexcludeentryscope: cn=provisioning,dc=idm,dc=nypd,dc=finest
nsslapd-pluginprecedence: 40
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
referint-logfile: /var/log/dirsrv/slapd-IDM-NYPD-FINEST/referint
referint-membership-attr: member
referint-membership-attr: uniquemember
referint-membership-attr: owner
referint-membership-attr: seeAlso
referint-membership-attr: manager
referint-membership-attr: secretary
referint-membership-attr: memberuser
referint-membership-attr: memberhost
referint-membership-attr: sourcehost
referint-membership-attr: memberservice
referint-membership-attr: managedby
referint-membership-attr: memberallowcmd
referint-membership-attr: memberdenycmd
referint-membership-attr: ipasudorunas
referint-membership-attr: ipasudorunasgroup
referint-membership-attr: ipatokenradiusconfiglink
referint-membership-attr: ipaassignedidview
referint-membership-attr: ipaallowedtarget
referint-membership-attr: ipamemberca
referint-membership-attr: ipamembercertprofile
referint-membership-attr: ipalocation
referint-update-delay: 0

dn: cn=Retro Changelog Plugin,cn=plugins,cn=config
cn: Retro Changelog Plugin
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161614Z
nsslapd-attribute: nsuniqueid:targetUniqueId
nsslapd-changelogmaxage: 2d
nsslapd-include-suffix: cn=dns,dc=idm,dc=nypd,dc=finest
nsslapd-plugin-depends-on-named: Class of Service
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Retrocl Plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: retrocl
nsslapd-pluginInitfunc: retrocl_plugin_init
nsslapd-pluginPath: libretrocl-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
nsslapd-pluginbetxn: on
nsslapd-pluginprecedence: 25
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Roles Plugin,cn=plugins,cn=config
cn: Roles Plugin
nsslapd-plugin-depends-on-named: State Change Plugin
nsslapd-plugin-depends-on-named: Views
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: roles plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: roles
nsslapd-pluginInitfunc: roles_init
nsslapd-pluginPath: libroles-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
nsslapd-pluginbetxn: on
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=RootDN Access Control,cn=plugins,cn=config
cn: RootDN Access Control
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: off
nsslapd-pluginId: none
nsslapd-pluginInitfunc: rootdn_init
nsslapd-pluginPath: librootdn-access-plugin
nsslapd-pluginType: internalpreoperation
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
objectClass: top
objectClass: nsSlapdPlugin
objectClass: rootDNPluginConfig

dn: cn=Schema Compatibility,cn=plugins,cn=config
cn: Schema Compatibility
createTimestamp: 20201026161615Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161615Z
nsslapd-pluginDescription: Schema Compatibility Plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: schema-compat-plugin
nsslapd-pluginInitfunc: schema_compat_plugin_init
nsslapd-pluginPath: /usr/lib64/dirsrv/plugins/schemacompat-plugin.so
nsslapd-pluginType: object
nsslapd-pluginVendor: redhat.com
nsslapd-pluginVersion: 0.56.5 (betxn support available and enabled by default)
nsslapd-pluginbetxn: on
nsslapd-pluginprecedence: 40
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
numSubordinates: 5

dn: cn=Schema Reload,cn=plugins,cn=config
cn: Schema Reload
nsslapd-pluginDescription: task plugin to reload schema files
nsslapd-pluginEnabled: on
nsslapd-pluginId: schemareload
nsslapd-pluginInitfunc: schemareload_init
nsslapd-pluginPath: libschemareload-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Space Insensitive String Syntax,cn=plugins,cn=config
cn: Space Insensitive String Syntax
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: off
nsslapd-pluginId: none
nsslapd-pluginInitfunc: sicis_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=State Change Plugin,cn=plugins,cn=config
cn: State Change Plugin
nsslapd-pluginDescription: state change notification service plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: statechange
nsslapd-pluginInitfunc: statechange_init
nsslapd-pluginPath: libstatechange-plugin
nsslapd-pluginType: betxnpostoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=sudorule name uniqueness,cn=plugins,cn=config
cn: sudorule name uniqueness
createTimestamp: 20201026161213Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161213Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce unique attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NSUniqueAttr
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-attribute-name: cn
uniqueness-subtrees: cn=sudorules,cn=sudo,dc=idm,dc=nypd,dc=finest

dn: cn=Syntax Validation Task,cn=plugins,cn=config
cn: Syntax Validation Task
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: on
nsslapd-pluginId: none
nsslapd-pluginInitfunc: syntax_validate_task_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Telephone Syntax,cn=plugins,cn=config
cn: Telephone Syntax
nsslapd-pluginDescription: telephoneNumber attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: tele-syntax
nsslapd-pluginInitfunc: tel_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Teletex Terminal Identifier Syntax,cn=plugins,cn=config
cn: Teletex Terminal Identifier Syntax
nsslapd-pluginDescription: Teletex Terminal Identifier attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: teletextermid-syntax
nsslapd-pluginInitfunc: teletex_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Telex Number Syntax,cn=plugins,cn=config
cn: Telex Number Syntax
nsslapd-pluginDescription: Telex Number attribute syntax plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: telex-syntax
nsslapd-pluginInitfunc: telex_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=uid uniqueness,cn=plugins,cn=config
cn: uid uniqueness
createTimestamp: 20201026161600Z
creatorsName: cn=Directory Manager
modifiersName: cn=Directory Manager
modifyTimestamp: 20201026161600Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: Enforce unique attribute values
nsslapd-pluginEnabled: on
nsslapd-pluginId: NSUniqueAttr
nsslapd-pluginInitfunc: NSUniqueAttr_Init
nsslapd-pluginPath: libattr-unique-plugin
nsslapd-pluginType: preoperation
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject
uniqueness-across-all-subtrees: on
uniqueness-attribute-name: uid
uniqueness-exclude-subtrees: cn=compat,dc=idm,dc=nypd,dc=finest
uniqueness-exclude-subtrees: cn=staged users,cn=accounts,cn=provisioning,dc=id
 m,dc=nypd,dc=finest
uniqueness-subtree-entries-oc: posixAccount
uniqueness-subtrees: dc=idm,dc=nypd,dc=finest

dn: cn=URI Syntax,cn=plugins,cn=config
cn: URI Syntax
nsslapd-pluginDescription: none
nsslapd-pluginEnabled: off
nsslapd-pluginId: none
nsslapd-pluginInitfunc: uri_init
nsslapd-pluginPath: libsyntax-plugin
nsslapd-pluginType: syntax
nsslapd-pluginVendor: none
nsslapd-pluginVersion: none
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=USN,cn=plugins,cn=config
cn: USN
modifiersName: cn=directory manager
modifyTimestamp: 20201211193034Z
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: USN (Update Sequence Number) plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: USN
nsslapd-pluginInitfunc: usn_init
nsslapd-pluginPath: libusn-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
nsslapd-pluginbetxn: on
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=Views,cn=plugins,cn=config
cn: Views
nsslapd-plugin-depends-on-named: State Change Plugin
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: virtual directory information tree views plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: views
nsslapd-pluginInitfunc: views_init
nsslapd-pluginPath: libviews-plugin
nsslapd-pluginType: object
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=whoami,cn=plugins,cn=config
cn: whoami
nsslapd-plugin-depends-on-type: database
nsslapd-pluginDescription: whoami extended operation plugin
nsslapd-pluginEnabled: on
nsslapd-pluginId: whoami-plugin
nsslapd-pluginInitfunc: whoami_init
nsslapd-pluginPath: libwhoami-plugin
nsslapd-pluginType: extendedop
nsslapd-pluginVendor: 389 Project
nsslapd-pluginVersion: 1.3.10.2
objectClass: top
objectClass: nsSlapdPlugin
objectClass: extensibleObject

dn: cn=consumerUpdatePolicy,cn=replSchema,cn=config
cn: consumerUpdatePolicy
createTimestamp: 20201026161205Z
creatorsName: cn=Multimaster Replication Plugin,cn=plugins,cn=config
modifiersName: cn=Multimaster Replication Plugin,cn=plugins,cn=config
modifyTimestamp: 20201026161205Z
objectClass: top
objectClass: nsSchemaPolicy
schemaUpdateAttributeAccept: 2.16.840.1.113730.3.1.2110
schemaUpdateObjectclassAccept: printer-uri-oid

dn: cn=supplierUpdatePolicy,cn=replSchema,cn=config
cn: supplierUpdatePolicy
createTimestamp: 20201026161205Z
creatorsName: cn=Multimaster Replication Plugin,cn=plugins,cn=config
modifiersName: cn=Multimaster Replication Plugin,cn=plugins,cn=config
modifyTimestamp: 20201026161205Z
objectClass: top
objectClass: nsSchemaPolicy
schemaUpdateAttributeAccept: 2.16.840.1.113730.3.1.2110
schemaUpdateObjectclassAccept: printer-uri-oid

dn: cn=mapping,cn=sasl,cn=config
cn: mapping
objectClass: top
objectClass: nsContainer
numSubordinates: 3

dn: cn=abort cleanallruv,cn=tasks,cn=config
objectClass: top
objectClass: extensibleObject
cn: abort cleanallruv
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
createTimestamp: 20210609174700Z
modifyTimestamp: 20210609174700Z

dn: cn=automember export updates,cn=tasks,cn=config
objectClass: top
objectClass: extensibleObject
cn: automember export updates
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
createTimestamp: 20210609174700Z
modifyTimestamp: 20210609174700Z

dn: cn=automember map updates,cn=tasks,cn=configzzzzz
objectClass: top
objectClass: extensibleObject
cn: automember map updates
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
createTimestamp: 20210609174700Z
modifyTimestamp: 20210609174700Z
"""

LDIF_CONFIG_EMPTY = ""


def test_ldip_parser():
    ldif_config = LDIFParser(context_wrap(LDIF_CONFIG))
    #import pdb; pdb.set_trace()
    assert ldif_config[1]['dn_name'] == 'dn: cn=config'
    assert ldif_config[1]['cn_name'][7]['modifiersName'] == 'cn=directory manager'
    assert ldif_config[1]['cn_name'][8]['modifyTimestamp'] == '20210609192548Z'


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