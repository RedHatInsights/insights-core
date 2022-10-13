from insights.parsers import ls_krb5_sssd
from insights.parsers.ls_krb5_sssd import LsKrb5SSSD
from insights.tests import context_wrap
import doctest

LS_KRB5_SSSD = """
/var/lib/sss/pubconf/krb5.include.d:
total 24
drwxr-xr-x@ 6 501  20  192 Jul  1 23:46 .
drwxr-xr-x@ 3 501  20   96 Jul  1 23:48 ..
-rw-r--r--@ 1 501  20  674 Jul  1 23:46 domain_realm_rhidm_gwl_bz
-rw-r--r--@ 1 501  20   35 Jul  1 23:46 krb5_libdefaults
-rw-r--r--@ 1 501  20   98 Jul  1 23:46 localauth_plugin
-rw-------@ 1 501  20    0 Oct  1  2021 localauth_pluginolsIe3
"""


def test_ls_krb5_sssd():
    ls_krb5_sssd = LsKrb5SSSD(context_wrap(LS_KRB5_SSSD))
    assert '/var/lib/sss/pubconf/krb5.include.d' in ls_krb5_sssd
    assert ls_krb5_sssd.files_of('/var/lib/sss/pubconf/krb5.include.d') == ['domain_realm_rhidm_gwl_bz', 'krb5_libdefaults', 'localauth_plugin', 'localauth_pluginolsIe3']


def test_ls_krb5_sssd_doc():
    failed_count, tests = doctest.testmod(
        ls_krb5_sssd,
        globs={'ls_krb5_sssd': ls_krb5_sssd.LsKrb5SSSD(context_wrap(LS_KRB5_SSSD))}
    )
    assert failed_count == 0
