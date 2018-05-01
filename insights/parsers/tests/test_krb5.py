from insights.parsers import krb5
from insights.tests import context_wrap


KRB5CONFIG = """
# Configuration snippets may be placed in this directory as well
includedir /etc/krb5.conf.d/
include /etc/krb5test.conf
module /etc/krb5test.conf:residual

[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log
 admin_server = FILE:/var/log/kadmind.log

[realms]
 dns_lookup_realm = false
 default_ccache_name = KEYRING:persistent:%{uid}
 default_ccache_name2 = KEYRING:%{uid}:persistent
 kdc_default_options = default.example.com
 kdc_default_options = default2.example.com
 EXAMPLE.COM = {
  kdc = kerberos.example.com
  admin_server = kerberos.example.com
  auth_to_local = RULE:[1:$1@$0](.*@.*EXAMPLE.ORG)s/@.*//
 }
 EXAMPLE4.COM = {
  kdc = kerberos.example4.com
  admin_server = kerberos.example4.com
 }
 ticket_lifetime = 24h
[libdefaults]
 dnsdsd = false
 tilnvs = 24h
 default_ccache_name = KEYRING:%{uid}:persistent
 EXAMPLE2.COM = {
  kdc = kerberos.example2.com
  admin_server = kerberos.example2.com
 }
 EXAMPLE3.COM = {
  kdc = kerberos.example3.com
  admin_server = kerberos.example3.com *
 }
# renew_lifetime = 7d
# forwardable = true
# rdns = false
""".strip()

KRB5CONFIG2 = """
# Configuration snippets may be placed in this directory as well
""".strip()

KRB5DCONFIG = """
# Configuration snippets may be placed in this directory as well

[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log

[realms]
 dns_lookup_realm = false
 ticket_lifetime = 24h
# default_ccache_name = KEYRING:persistent:%{uid}
 EXAMPLE.COM = {
  kdc = kerberos.example.com
  kdc = test2.example.com
  kdc = test3.example.com
  admin_server = kerberos.example.com
 }

[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log *
 admin_server = FILE:/var/log/kadmind.log

""".strip()

KRB5_CONF_PATH = "etc/krb5.conf"
KRB5_DCONF_PATH = "etc/krb5.conf.d/test.conf"


def test_krb5configuration():
    common_conf_info = krb5.Krb5Configuration(context_wrap(KRB5CONFIG, path=KRB5_CONF_PATH))
    assert common_conf_info["libdefaults"]["dnsdsd"] == "false"
    assert "renew_lifetime" not in common_conf_info.data.keys()
    assert common_conf_info["realms"]["EXAMPLE.COM"]["kdc"] == "kerberos.example.com"
    assert common_conf_info["realms"]["default_ccache_name"] == "KEYRING:persistent:%{uid}"
    assert common_conf_info["libdefaults"]["default_ccache_name"] == "KEYRING:%{uid}:persistent"
    assert common_conf_info["realms"]["kdc_default_options"] == ["default.example.com", "default2.example.com"]
    assert "realms" in common_conf_info.sections()
    assert "realmstest" not in common_conf_info.sections()
    assert common_conf_info.has_section("realms")
    assert not common_conf_info.has_option("realms", "nosuchoption")
    assert not common_conf_info.has_option("nosucsection", "nosuchoption")
    assert not common_conf_info.options("realmsno")
    assert sorted(common_conf_info.options("logging")) == sorted(['default', 'admin_server', 'kdc'])
    assert common_conf_info.include == ["/etc/krb5test.conf"]
    assert common_conf_info.includedir == ["/etc/krb5.conf.d/"]
    assert common_conf_info.module == ["/etc/krb5test.conf:residual"]


def test2_krb5configuration():
    common_conf_info = krb5.Krb5Configuration(context_wrap(KRB5CONFIG2, path=KRB5_CONF_PATH))
    assert common_conf_info.data == {}


def test_krb5Dconfiguration():
    common_conf_info = krb5.Krb5Configuration(context_wrap(KRB5DCONFIG, path=KRB5_DCONF_PATH))
    assert common_conf_info["realms"]["ticket_lifetime"] == "24h"
    assert "default_ccache_name" not in common_conf_info.data.keys()
    assert common_conf_info["realms"]["EXAMPLE.COM"]["kdc"] == ['kerberos.example.com', 'test2.example.com', 'test3.example.com']
    assert not common_conf_info.has_option("logging", "admin_server")
