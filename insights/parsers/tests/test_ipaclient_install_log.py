from datetime import datetime
from insights.parsers.ipaclient_install_log import IpaclientInstallLog
from insights.tests import context_wrap


IPACLIENT_INSTALL_LOG_SHORT = """
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
"""

IPACLIENT_INSTALL_LOG_LONG = """
2019-11-20T11:31:27Z DEBUG Logging to /var/log/ipaclient-install.log
2019-11-20T11:31:27Z DEBUG ipa-client-install was invoked with arguments [] and options: {'unattended': True, 'principal': None, 'prompt_password': False, 'on_master': True, 'ca_cert_files': None, 'force': False, 'configure_firefox': False, 'firefox_dir': None, 'keytab': None, 'mkhomedir': True, 'force_join': False, 'ntp_servers': None, 'ntp_pool': None, 'no_ntp': True, 'force_ntpd': False, 'nisdomain': None, 'no_nisdomain': False, 'ssh_trust_dns': False, 'no_ssh': False, 'no_sshd': False, 'no_sudo': False, 'no_dns_sshfp': False, 'kinit_attempts': None, 'request_cert': False, 'ip_addresses': None, 'all_ip_addresses': False, 'fixed_primary': False, 'permit': False, 'enable_dns_updates': False, 'no_krb5_offline_passwords': False, 'preserve_sssd': False, 'automount_location': None, 'domain_name': 'laptop.example.org', 'servers': ['ipa0.laptop.example.org'], 'realm_name': 'LAPTOP.EXAMPLE.ORG', 'host_name': 'ipa0.laptop.example.org', 'verbose': False, 'quiet': False, 'log_file': None, 'uninstall': False}
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
2019-11-20T11:31:27Z INFO Client hostname: ipa0.laptop.example.org
2019-11-20T11:31:27Z DEBUG Hostname source: Provided as option
2019-11-20T11:31:27Z INFO Realm: LAPTOP.EXAMPLE.ORG
2019-11-20T11:31:27Z DEBUG Realm source: Discovered from LDAP DNS records in ipa0.laptop.example.org
2019-11-20T11:31:27Z INFO DNS Domain: laptop.example.org
2019-11-20T11:31:27Z DEBUG DNS Domain source: Forced
2019-11-20T11:31:27Z INFO IPA Server: ipa0.laptop.example.org
2019-11-20T11:31:27Z DEBUG IPA Server source: Provided as option
2019-11-20T11:31:27Z INFO BaseDN: dc=laptop,dc=example,dc=org
2019-11-20T11:31:27Z DEBUG BaseDN source: From IPA server ldap://ipa0.laptop.example.org:389
2019-11-20T11:31:27Z DEBUG Loading Index file from '/var/lib/ipa-client/sysrestore/sysrestore.index'
2019-11-20T11:31:27Z DEBUG Loading StateFile from '/var/lib/ipa-client/sysrestore/sysrestore.state'
2019-11-20T11:31:27Z DEBUG Skipping attempt to configure and synchronize time with chrony server as it has been already done on master.
2019-11-20T11:31:28Z DEBUG Backing up system configuration file '/etc/sssd/sssd.conf'
2019-11-20T11:31:28Z DEBUG   -> Not backing up - '/etc/sssd/sssd.conf' doesn't exist
2019-11-20T11:31:28Z DEBUG New SSSD config will be created
2019-11-20T11:31:28Z DEBUG Backing up system configuration file '/etc/authselect/user-nsswitch.conf'
2019-11-20T11:31:28Z DEBUG Saving Index File to '/var/lib/ipa-client/sysrestore/sysrestore.index'
2019-11-20T11:31:28Z DEBUG Updating configuration file /etc/authselect/user-nsswitch.conf
2019-11-20T11:31:28Z INFO Configured /etc/sssd/sssd.conf
2019-11-20T11:31:28Z DEBUG Initializing principal host/ipa0.laptop.example.org@LAPTOP.EXAMPLE.ORG using keytab /etc/krb5.keytab
2019-11-20T11:31:28Z DEBUG using ccache /etc/ipa/.dns_ccache
2019-11-20T11:31:28Z DEBUG Attempt 1/5: success
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/usr/bin/certutil', '-d', '/tmp/tmpetgxv872', '-N', '-f', '/tmp/tmpetgxv872/pwdfile.txt', '-@', '/tmp/tmpetgxv872/pwdfile.txt']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=
2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=
2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/sbin/restorecon', '-F', '/tmp/tmpetgxv872']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=Warning no default label for /tmp/tmpetgxv872

2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=
2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/sbin/restorecon', '-F', '/tmp/tmpetgxv872/cert9.db']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=Warning no default label for /tmp/tmpetgxv872/cert9.db

2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=
2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/sbin/restorecon', '-F', '/tmp/tmpetgxv872/key4.db']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=Warning no default label for /tmp/tmpetgxv872/key4.db

2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=
2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/sbin/restorecon', '-F', '/tmp/tmpetgxv872/pkcs11.txt']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=Warning no default label for /tmp/tmpetgxv872/pkcs11.txt

2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=
2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/sbin/restorecon', '-F', '/tmp/tmpetgxv872/pwdfile.txt']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=Warning no default label for /tmp/tmpetgxv872/pwdfile.txt

2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG Starting external process
2019-11-20T11:31:28Z DEBUG args=['/usr/bin/certutil', '-d', 'sql:/tmp/tmpetgxv872', '-A', '-n', 'CA certificate 1', '-t', 'C,,', '-a', '-f', '/tmp/tmpetgxv872/pwdfile.txt']
2019-11-20T11:31:28Z DEBUG Process finished, return code=0
2019-11-20T11:31:28Z DEBUG stdout=
2019-11-20T11:31:28Z DEBUG stderr=
2019-11-20T11:31:28Z DEBUG failed to find session_cookie in persistent storage for principal 'host/ipa0.laptop.example.org@LAPTOP.EXAMPLE.ORG'
2019-11-20T11:31:28Z DEBUG trying https://ipa0.laptop.example.org/ipa/json
2019-11-20T11:31:28Z DEBUG Created connection context.rpcclient_140474925875984
2019-11-20T11:31:28Z DEBUG [try 1]: Forwarding 'schema' to json server 'https://ipa0.laptop.example.org/ipa/json'
2019-11-20T11:31:28Z DEBUG New HTTP connection (ipa0.laptop.example.org)
2019-11-20T11:31:41Z DEBUG received Set-Cookie (<class 'list'>)'['ipa_session=MagBearerToken=hEmo9mPQen5aO%2fMQKMo%2fSzw0vg9r1BY77nXksHkyMHXVnKQcLLKwAs7D%2fKzbZTDC0rPreLlNBzzY%2bUHGyxtBJHdAPON%2fdPXbGeHBpvUxdzezcgrdd9HOqpOtwc0bhWemXh%2b34KEcB%2fWa9FCiMyFf%2ftmQziyj4zmpRC8tVxK8olvOn9XIEfgXVmBK41bRvWNR4nZ1%2bUYSbCYG3YMShzefGGKFhGqfoVHobX0wcMoLeDKXb2K5Xj0tpYw54%2bHavmDbwbAA%2bzMUUubxhld6TQi6q0Ek4y8Tkv%2ft6Rp5McajJR%2fPUJ6avPHEiWkZqle9JUWY;path=/ipa;httponly;secure;']'
2019-11-20T11:31:41Z DEBUG storing cookie 'ipa_session=MagBearerToken=hEmo9mPQen5aO%2fMQKMo%2fSzw0vg9r1BY77nXksHkyMHXVnKQcLLKwAs7D%2fKzbZTDC0rPreLlNBzzY%2bUHGyxtBJHdAPON%2fdPXbGeHBpvUxdzezcgrdd9HOqpOtwc0bhWemXh%2b34KEcB%2fWa9FCiMyFf%2ftmQziyj4zmpRC8tVxK8olvOn9XIEfgXVmBK41bRvWNR4nZ1%2bUYSbCYG3YMShzefGGKFhGqfoVHobX0wcMoLeDKXb2K5Xj0tpYw54%2bHavmDbwbAA%2bzMUUubxhld6TQi6q0Ek4y8Tkv%2ft6Rp5McajJR%2fPUJ6avPHEiWkZqle9JUWY;' for principal host/ipa0.laptop.example.org@LAPTOP.EXAMPLE.ORG
2019-11-20T11:31:41Z DEBUG Destroyed connection context.rpcclient_140474925875984
2019-11-20T11:31:41Z DEBUG importing all plugin modules in ipaclient.remote_plugins.schema$7e1a2479...
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.remote_plugins.schema$7e1a2479.plugins
2019-11-20T11:31:41Z DEBUG importing all plugin modules in ipaclient.plugins...
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.automember
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.automount
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.ca
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.cert
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.certmap
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.certprofile
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.csrgen
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.dns
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.hbacrule
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.hbactest
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.host
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.idrange
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.internal
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.location
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.migration
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.misc
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.otptoken
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.otptoken_yubikey
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.passwd
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.permission
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.rpcclient
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.server
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.service
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.sudorule
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.topology
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.trust
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.user
2019-11-20T11:31:41Z DEBUG importing plugin module ipaclient.plugins.vault
2019-11-20T11:31:42Z DEBUG found session_cookie in persistent storage for principal 'host/ipa0.laptop.example.org@LAPTOP.EXAMPLE.ORG', cookie: 'ipa_session=MagBearerToken=hEmo9mPQen5aO%2fMQKMo%2fSzw0vg9r1BY77nXksHkyMHXVnKQcLLKwAs7D%2fKzbZTDC0rPreLlNBzzY%2bUHGyxtBJHdAPON%2fdPXbGeHBpvUxdzezcgrdd9HOqpOtwc0bhWemXh%2b34KEcB%2fWa9FCiMyFf%2ftmQziyj4zmpRC8tVxK8olvOn9XIEfgXVmBK41bRvWNR4nZ1%2bUYSbCYG3YMShzefGGKFhGqfoVHobX0wcMoLeDKXb2K5Xj0tpYw54%2bHavmDbwbAA%2bzMUUubxhld6TQi6q0Ek4y8Tkv%2ft6Rp5McajJR%2fPUJ6avPHEiWkZqle9JUWY'
2019-11-20T11:31:42Z DEBUG setting session_cookie into context 'ipa_session=MagBearerToken=hEmo9mPQen5aO%2fMQKMo%2fSzw0vg9r1BY77nXksHkyMHXVnKQcLLKwAs7D%2fKzbZTDC0rPreLlNBzzY%2bUHGyxtBJHdAPON%2fdPXbGeHBpvUxdzezcgrdd9HOqpOtwc0bhWemXh%2b34KEcB%2fWa9FCiMyFf%2ftmQziyj4zmpRC8tVxK8olvOn9XIEfgXVmBK41bRvWNR4nZ1%2bUYSbCYG3YMShzefGGKFhGqfoVHobX0wcMoLeDKXb2K5Xj0tpYw54%2bHavmDbwbAA%2bzMUUubxhld6TQi6q0Ek4y8Tkv%2ft6Rp5McajJR%2fPUJ6avPHEiWkZqle9JUWY;'
2019-11-20T11:31:42Z DEBUG trying https://ipa0.laptop.example.org/ipa/session/json
2019-11-20T11:31:42Z DEBUG Created connection context.rpcclient_140474906916496
2019-11-20T11:31:42Z DEBUG Try RPC connection
2019-11-20T11:31:42Z DEBUG [try 1]: Forwarding 'ping' to json server 'https://ipa0.laptop.example.org/ipa/session/json'
2019-11-20T11:31:42Z DEBUG New HTTP connection (ipa0.laptop.example.org)
2019-11-20T11:31:42Z DEBUG [try 1]: Forwarding 'ca_is_enabled' to json server 'https://ipa0.laptop.example.org/ipa/session/json'
2019-11-20T11:31:42Z DEBUG HTTP connection keep-alive (ipa0.laptop.example.org)
2019-11-20T11:31:42Z DEBUG [try 1]: Forwarding 'config_show' to json server 'https://ipa0.laptop.example.org/ipa/session/json'
2019-11-20T11:31:42Z DEBUG HTTP connection keep-alive (ipa0.laptop.example.org)
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/usr/bin/certutil', '-d', '/etc/ipa/nssdb', '-N', '-f', '/etc/ipa/nssdb/pwdfile.txt', '-@', '/etc/ipa/nssdb/pwdfile.txt']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/sbin/restorecon', '-F', '/etc/ipa/nssdb']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/sbin/restorecon', '-F', '/etc/ipa/nssdb/cert9.db']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/sbin/restorecon', '-F', '/etc/ipa/nssdb/key4.db']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/sbin/restorecon', '-F', '/etc/ipa/nssdb/pkcs11.txt']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/usr/sbin/selinuxenabled']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/sbin/restorecon', '-F', '/etc/ipa/nssdb/pwdfile.txt']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG retrieving schema for SchemaCache url=ldap://ipa0.laptop.example.org:389 conn=<ldap.ldapobject.SimpleLDAPObject object at 0x7fc2dcb0e050>
2019-11-20T11:31:43Z DEBUG Adding CA certificates to the IPA NSS database.
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/usr/bin/certutil', '-d', 'sql:/etc/ipa/nssdb', '-A', '-n', 'LAPTOP.EXAMPLE.ORG IPA CA', '-t', 'CT,C,C', '-a', '-f', '/etc/ipa/nssdb/pwdfile.txt']
2019-11-20T11:31:43Z DEBUG Process finished, return code=0
2019-11-20T11:31:43Z DEBUG stdout=
2019-11-20T11:31:43Z DEBUG stderr=
2019-11-20T11:31:43Z DEBUG Starting external process
2019-11-20T11:31:43Z DEBUG args=['/usr/bin/update-ca-trust']
2019-11-20T11:31:44Z DEBUG Process finished, return code=0
2019-11-20T11:31:44Z DEBUG stdout=
2019-11-20T11:31:44Z DEBUG stderr=
2019-11-20T11:31:44Z INFO Systemwide CA database updated.
2019-11-20T11:31:44Z INFO Adding SSH public key from /etc/ssh/ssh_host_ecdsa_key.pub
2019-11-20T11:31:44Z INFO Adding SSH public key from /etc/ssh/ssh_host_ed25519_key.pub
2019-11-20T11:31:44Z INFO Adding SSH public key from /etc/ssh/ssh_host_rsa_key.pub
2019-11-20T11:31:44Z DEBUG [try 1]: Forwarding 'host_mod' to json server 'https://ipa0.laptop.example.org/ipa/session/json'
2019-11-20T11:31:44Z DEBUG HTTP connection keep-alive (ipa0.laptop.example.org)
2019-11-20T11:31:44Z DEBUG Writing nsupdate commands to /etc/ipa/.dns_update.txt:
2019-11-20T11:31:44Z DEBUG debug
update delete ipa0.laptop.example.org. IN SSHFP
show
send
update add ipa0.laptop.example.org. 1200 IN SSHFP 3 1 E52AA1BAF90AA5FCC5DD75C395623FE4F9BB933D
update add ipa0.laptop.example.org. 1200 IN SSHFP 3 2 CC4014C1809C488F333B40D319652CB3A81D2757F8FF6C490E4BDD8657785C59
update add ipa0.laptop.example.org. 1200 IN SSHFP 4 1 E2E0818E6FBEB71355D8CD61C6EA0BB05C2F9F7A
update add ipa0.laptop.example.org. 1200 IN SSHFP 4 2 96D2BDDFA1C240A5316E03CAB04E2485CAFE28F93E6B130AD05841BCEEAE531D
update add ipa0.laptop.example.org. 1200 IN SSHFP 1 1 8FCA5A129DE22C8CD1BE07CDDE384D2FC34FEC5E
update add ipa0.laptop.example.org. 1200 IN SSHFP 1 2 E7F6C4AF4E73AEFDE206792E1B00E3686F4344155EB8E51093CF503A144601B5
show
send

2019-11-20T11:31:44Z DEBUG Starting external process
2019-11-20T11:31:44Z DEBUG args=['/usr/bin/nsupdate', '-g', '/etc/ipa/.dns_update.txt']
2019-11-20T11:31:44Z DEBUG Process finished, return code=0
2019-11-20T11:31:44Z DEBUG stdout=Outgoing update query:
;; ->>HEADER<<- opcode: UPDATE, status: NOERROR, id:      0
;; flags:; ZONE: 0, PREREQ: 0, UPDATE: 0, ADDITIONAL: 0
;; UPDATE SECTION:
ipa0.laptop.example.org. 0      ANY     SSHFP

Outgoing update query:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id:  48292
;; flags:; QUESTION: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1
;; QUESTION SECTION:
;2510202844.sig-ipa0.laptop.example.org.        ANY TKEY

;; ADDITIONAL SECTION:
2510202844.sig-ipa0.laptop.example.org. 0 ANY TKEY gss-tsig. 1574249504 1574249504 3 NOERROR 797 YIIDGQYJKoZIhvcSAQICAQBuggMIMIIDBKADAgEFoQMCAQ6iBwMFACAA AACjggH9YYIB+TCCAfWgAwIBBaEUGxJMQVBUT1AuRVhBTVBMRS5PUkei KTAnoAMCAQGhIDAeGwNETlMbF2lwYTAubGFwdG9wLmV4YW1wbGUub3Jn o4IBqzCCAaegAwIBEqEDAgECooIBmQSCAZVTNSEUJroxnDoI+S3+sWIn ORmLZJ2A5yfzbah5lynOr8BWkzqArKMIecpUzxjZvRlTiG3l/p/mHA8W Wp1QGr3CYApopYQ24JtA/QSbWyYtIbzE7FGPuF0o5y/rjm0zQnvxLHpD bFyQuTzk4YTwU0pmigXQuxEiiSdiXd+RZDMLdpH+I9T9fXYgsR8iND/L b5IhsPCRQDqPT4lCjkBjVrkFXl6xLhQFBJ4kodhS2wtbAkwBCGRDwiZU cbCrCVnYQRtHMnqvyPscuU3DkUP092lVarIuLOBGYM0xPPHjAvwZ5ZPa uJDlsfABQCQgGWHq4CrJCWreOfVGik3HyqxoyqPEpr8BvgcR7LluEbvP K1ca63rXN+RyavPNbVKm3H0OSI11xbvuoMqrZugJZWoJTVyTM8ATwhmG mR5+tvEaSzmQvDAv6BsmFrAu8liI7daa2qwZIO45slkRMnLnFhKytzJW ifcK6b9FOzHzu6Km/a0JnNlTuF6DCOnrplV+/TlGbmyD25zD2+vcHZ06 Ed+eF5b8QD9fZ56kge0wgeqgAwIBEqKB4gSB37VLp2Pu5xHN2zup3Y6N JvKHxJTYTbLfDAUFIhYBO/EY6ze9gFkbMTCS5ud2uMQv6bhMbDrDHtoC fHdTmrz5rCyxwksUNdDnmB3Fuw90o0LmqEeOJ3gfUEZbK1QD4soJlKn6 pSLCXEuhc/HCng0fWyjJdcSy9cVdJaHD6RpsJJTqhJDKlpdrdHlaxDJI 8e3WRK0Q0Yr7jjNl9D0aj/7WIjkYPhMkPHRtvAyQG9LJQLk5YrbYaW6h aeL9bwjOlqqdm5Zsf02aqkPOxS7OWm9VK9+sgSjq2gc/WxuTR9DLpHE= 0

Outgoing update query:
;; ->>HEADER<<- opcode: UPDATE, status: NOERROR, id:  48357
;; flags:; ZONE: 1, PREREQ: 0, UPDATE: 1, ADDITIONAL: 1
;; UPDATE SECTION:
ipa0.laptop.example.org. 0      ANY     SSHFP

;; TSIG PSEUDOSECTION:
2510202844.sig-ipa0.laptop.example.org. 0 ANY TSIG gss-tsig. 1574249504 300 28 BAQE//////8AAAAAFbrK15Pb3jZExZWmmSgELQ== 48357 NOERROR 0

Outgoing update query:
;; ->>HEADER<<- opcode: UPDATE, status: NOERROR, id:      0
;; flags:; ZONE: 0, PREREQ: 0, UPDATE: 0, ADDITIONAL: 0
;; UPDATE SECTION:
ipa0.laptop.example.org. 1200   IN      SSHFP   3 1 E52AA1BAF90AA5FCC5DD75C395623FE4F9BB933D
ipa0.laptop.example.org. 1200   IN      SSHFP   3 2 CC4014C1809C488F333B40D319652CB3A81D2757F8FF6C490E4BDD86 57785C59
ipa0.laptop.example.org. 1200   IN      SSHFP   4 1 E2E0818E6FBEB71355D8CD61C6EA0BB05C2F9F7A
ipa0.laptop.example.org. 1200   IN      SSHFP   4 2 96D2BDDFA1C240A5316E03CAB04E2485CAFE28F93E6B130AD05841BC EEAE531D
ipa0.laptop.example.org. 1200   IN      SSHFP   1 1 8FCA5A129DE22C8CD1BE07CDDE384D2FC34FEC5E
ipa0.laptop.example.org. 1200   IN      SSHFP   1 2 E7F6C4AF4E73AEFDE206792E1B00E3686F4344155EB8E51093CF503A 144601B5

Outgoing update query:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id:  47563
;; flags:; QUESTION: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1
;; QUESTION SECTION:
;1561867132.sig-ipa0.laptop.example.org.        ANY TKEY

;; ADDITIONAL SECTION:
1561867132.sig-ipa0.laptop.example.org. 0 ANY TKEY gss-tsig. 1574249504 1574249504 3 NOERROR 797 YIIDGQYJKoZIhvcSAQICAQBuggMIMIIDBKADAgEFoQMCAQ6iBwMFACAA AACjggH9YYIB+TCCAfWgAwIBBaEUGxJMQVBUT1AuRVhBTVBMRS5PUkei KTAnoAMCAQGhIDAeGwNETlMbF2lwYTAubGFwdG9wLmV4YW1wbGUub3Jn o4IBqzCCAaegAwIBEqEDAgECooIBmQSCAZVTNSEUJroxnDoI+S3+sWIn ORmLZJ2A5yfzbah5lynOr8BWkzqArKMIecpUzxjZvRlTiG3l/p/mHA8W Wp1QGr3CYApopYQ24JtA/QSbWyYtIbzE7FGPuF0o5y/rjm0zQnvxLHpD bFyQuTzk4YTwU0pmigXQuxEiiSdiXd+RZDMLdpH+I9T9fXYgsR8iND/L b5IhsPCRQDqPT4lCjkBjVrkFXl6xLhQFBJ4kodhS2wtbAkwBCGRDwiZU cbCrCVnYQRtHMnqvyPscuU3DkUP092lVarIuLOBGYM0xPPHjAvwZ5ZPa uJDlsfABQCQgGWHq4CrJCWreOfVGik3HyqxoyqPEpr8BvgcR7LluEbvP K1ca63rXN+RyavPNbVKm3H0OSI11xbvuoMqrZugJZWoJTVyTM8ATwhmG mR5+tvEaSzmQvDAv6BsmFrAu8liI7daa2qwZIO45slkRMnLnFhKytzJW ifcK6b9FOzHzu6Km/a0JnNlTuF6DCOnrplV+/TlGbmyD25zD2+vcHZ06 Ed+eF5b8QD9fZ56kge0wgeqgAwIBEqKB4gSB37lwcxljU3BwA/1/G1Jh u2ffLkYMnVQtrqBmjpgTp8WSSbkUtW3ahYU6jbqlpAhtKscvidnsGJem lua1ngjD+ZZsKvkNXPsXCUEU6qs2nQ1tfPGgy38ZJiLhZTSHJ2v81+vB Kg1NgqBwtGZPHs9wmieJWhnh+326YD0vydJeZX/dWxcbsT8knCaW9cfS 7U0bvIMqAjLAkUlji2kXJwHyyemlH1JKV9kaavh0X4DaWXY6uaU2yj/a zXwfPXu0iBv4WZuPni+yW505CFzmljg0hiBR5Z37OiYN0UEwssRVMJQ= 0

Outgoing update query:
;; ->>HEADER<<- opcode: UPDATE, status: NOERROR, id:  19687
;; flags:; ZONE: 1, PREREQ: 0, UPDATE: 6, ADDITIONAL: 1
;; UPDATE SECTION:
ipa0.laptop.example.org. 1200   IN      SSHFP   3 1 E52AA1BAF90AA5FCC5DD75C395623FE4F9BB933D
ipa0.laptop.example.org. 1200   IN      SSHFP   3 2 CC4014C1809C488F333B40D319652CB3A81D2757F8FF6C490E4BDD86 57785C59
ipa0.laptop.example.org. 1200   IN      SSHFP   4 1 E2E0818E6FBEB71355D8CD61C6EA0BB05C2F9F7A
ipa0.laptop.example.org. 1200   IN      SSHFP   4 2 96D2BDDFA1C240A5316E03CAB04E2485CAFE28F93E6B130AD05841BC EEAE531D
ipa0.laptop.example.org. 1200   IN      SSHFP   1 1 8FCA5A129DE22C8CD1BE07CDDE384D2FC34FEC5E
ipa0.laptop.example.org. 1200   IN      SSHFP   1 2 E7F6C4AF4E73AEFDE206792E1B00E3686F4344155EB8E51093CF503A 144601B5

;; TSIG PSEUDOSECTION:
1561867132.sig-ipa0.laptop.example.org. 0 ANY TSIG gss-tsig. 1574249504 300 28 BAQE//////8AAAAAINJZvR7Fpql+Hwew/d4qkA== 19687 NOERROR 0
"""


def test_ipaclientinstall_log():
    log = IpaclientInstallLog(context_wrap(IPACLIENT_INSTALL_LOG_SHORT))
    assert len(log.get('DEBUG')) == 27
    assert len(list(log.get_after(datetime(2017, 8, 7, 7, 37, 30)))) == 28
    log = IpaclientInstallLog(context_wrap(IPACLIENT_INSTALL_LOG_LONG))
    assert len(log.get('DEBUG')) == 231
    assert len(list(log.get_after(datetime(2017, 8, 7, 7, 37, 30)))) == 315
