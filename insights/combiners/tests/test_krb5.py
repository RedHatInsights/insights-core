from insights.combiners.krb5 import AllKrb5Conf
from insights.parsers.krb5 import Krb5Configuration
from insights.tests import context_wrap


KRB5CONFIG = """
# Configuration snippets may be placed in this directory as well
includedir /etc/krb5.conf.d/
include /etc/krb5test.conf
module /etc/krb5test.conf:residual

[libdefaults]
 donotoverwrite1 = true

[logging]
 default = FILE:/var/log/krb5libs.log
 kdc = FILE:/var/log/krb5kdc.log

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
# renew_lifetime = 7d
# forwardable = true
# rdns = false
""".strip()


KRB5CONFIG2 = """
# Configuration snippets may be placed in this directory as well

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
 default = FILE:/var/log/krb5libs2.log
 kdc = FILE:/var/log/krb5kdc2.log
 admin_server = FILE:/var/log/kadmind2.log

[libdefaults]
 donotoverwrite2 = true
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
""".strip()


KRB5CONFIG3 = """

[libdefaults]
 donotoverwrite3 = true

""".strip()


def test_active_krb5_nest():
    krb51 = Krb5Configuration(context_wrap(KRB5CONFIG, path='/etc/krb5.conf'))
    krb52 = Krb5Configuration(context_wrap(KRB5CONFIG2, path='/etc/krb5.conf.d/test.conf'))
    krb53 = Krb5Configuration(context_wrap(KRB5CONFIG3, path='/etc/krb5.conf.d/test2.conf'))
    result = AllKrb5Conf([krb51, krb52, krb53])
    assert result.has_option("libdefaults", "donotoverwrite1")
    assert result.has_option("libdefaults", "donotoverwrite2")
    assert result.has_option("libdefaults", "donotoverwrite3")
    assert result["logging"]["kdc"] == "FILE:/var/log/krb5kdc.log"
    assert result.has_option("logging", "admin_server")
    assert result["libdefaults"]["EXAMPLE2.COM"]["kdc"] == "kerberos.example2.com"
    assert result["libdefaults"]["default_ccache_name"] == "KEYRING:%{uid}:persistent"
    assert "realms" in result.sections()
    assert "realmstest" not in result.sections()
    assert result.has_section("realms")
    assert not result.has_option("realms", "nosuchoption")
    assert not result.has_option("nosucsection", "nosuchoption")
    assert not result.options("realmsno")
    assert sorted(result.options("logging")) == sorted(['default', 'admin_server', 'kdc'])
    assert result.include == ["/etc/krb5test.conf"]
    assert result.includedir == ["/etc/krb5.conf.d/"]
    assert result.module == ["/etc/krb5test.conf:residual"]
