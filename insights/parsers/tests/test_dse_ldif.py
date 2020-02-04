import insights.parsers.dse_ldif as dseldifconfig_module
from insights.parsers.dse_ldif import DSELdifConfig
from insights.tests import context_wrap
import doctest


DSE_LDIF_CONFIG_INPUT = """
dn:
objectClass: top
aci: (targetattr != "aci")(version 3.0; aci "rootdse anon read access"; allow(
 read,search,compare) userdn="ldap:///anyone";)
creatorsName: cn=server,cn=plugins,cn=config
modifiersName: cn=server,cn=plugins,cn=config
createTimestamp: 20151021124922Z
modifyTimestamp: 20151021124922Z

dn: cn=encryption,cn=config
objectClass: top
objectClass: nsEncryptionConfig
cn: encryption
nsSSLSessionTimeout: 0
nsSSLClientAuth: allowed
sslVersionMin: TLS1.0
modifiersName: cn=directory manager
createTimestamp: 20151021124922Z
nsTLS1: on
nsSSL3Ciphers: -rsa_null_md5,-rsa_null_sha,+rsa_rc4_128_md5,+rsa_rc4_40_md5,+r
 sa_rc2_40_md5,+rsa_des_sha,+rsa_fips_des_sha,+rsa_3des_sha,+rsa_fips_3des_sha
 ,+fortezza,+fortezza_rc4_128_sha,+fortezza_null,+tls_rsa_export1024_with_rc4_
 56_sha,+tls_rsa_export1024_with_des_cbc_sha,+tls_rsa_aes_128_sha,+tls_rsa_aes
 _256_sha
nsKeyfile: alias/slapd-rhds10-2-key3.db
nsCertfile: alias/slapd-rhds10-2-cert8.db
numSubordinates: 1
""".strip()


def test_dse_ldif_config():
    dse_ldif_config = DSELdifConfig(context_wrap(DSE_LDIF_CONFIG_INPUT))
    assert dse_ldif_config is not None
    assert 'objectClass' in dse_ldif_config
    assert 'aci' in dse_ldif_config
    assert 'nsSSL3Ciphers' in dse_ldif_config
    assert 'sslVersionMin' in dse_ldif_config
    assert 'nsCertfile' in dse_ldif_config


def test_doc_examples():
    env = {
        'dse_ldif': DSELdifConfig(context_wrap(DSE_LDIF_CONFIG_INPUT)),
    }
    failed, total = doctest.testmod(dseldifconfig_module, globs=env)
    assert failed == 0
