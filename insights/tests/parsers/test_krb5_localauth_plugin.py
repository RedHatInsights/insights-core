from insights.parsers import krb5
from insights.tests import context_wrap

CONF_CONTENT = """
[plugins]
localauth = {
   module = sssd:/usr/lib64/sssd/modules/sssd_krb5_localauth_plugin.so
 }
""".strip()


def test_krb5_localauth_plugin_conf():
    result = krb5.Krb5LocalauthPlugin(context_wrap(CONF_CONTENT))
    assert (
        result['plugins']['localauth']['module']
        == 'sssd:/usr/lib64/sssd/modules/sssd_krb5_localauth_plugin.so'
    )
