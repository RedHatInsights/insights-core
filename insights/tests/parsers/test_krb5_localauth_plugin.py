import doctest

from insights.parsers import krb5_localauth_plugin
from insights.tests import context_wrap

conf_content = """
[plugins]
 localauth = {
  module = sssd:/usr/lib64/sssd/modules/sssd_krb5_localauth_plugin.so
 }
""".strip()


def test_krb5_localauth_plugin_conf():
    result = krb5_localauth_plugin.Krb5LocalauthPlugin(context_wrap(conf_content))
    assert result['plugins']['localauth']['module'] == 'sssd:/usr/lib64/sssd/modules/sssd_krb5_localauth_plugin.so'


def test_doc_examples():
    env = {
        'conf': krb5_localauth_plugin.Krb5LocalauthPlugin(context_wrap(conf_content))
    }
    failed, total = doctest.testmod(krb5_localauth_plugin, globs=env)
    assert failed == 0
