from insights.parsers import httpd_M
from insights.parsers.httpd_M import HttpdM
from insights.tests import context_wrap
from insights.parsers import ParseException
import pytest
import doctest

HTTPD_M_RHEL6 = """
httpd.event: apr_sockaddr_info_get() failed for liuxc-rhel6-apache
httpd.event: Could not reliably determine the server's fully qualified domain name, using 127.0.0.1 for ServerName
Loaded Modules:
 core_module (static)
 mpm_event_module (static)
 http_module (static)
 so_module (static)
 auth_basic_module (shared)
 auth_digest_module (shared)
 authn_file_module (shared)
 authn_alias_module (shared)
 authn_anon_module (shared)
 authn_dbm_module (shared)
 authn_default_module (shared)
 authz_host_module (shared)
 authz_user_module (shared)
 authz_owner_module (shared)
 authz_groupfile_module (shared)
 authz_dbm_module (shared)
 authz_default_module (shared)
 ldap_module (shared)
 authnz_ldap_module (shared)
 include_module (shared)
 log_config_module (shared)
Syntax OK
""".strip()

HTTPD_M_RHEL7 = """
AH00558: httpd: Could not reliably determine the server's fully qualified domain name, using fe80::a9:89fd:1fc4:f8d. Set the 'ServerName' directive globally to suppress this message
Loaded Modules:
 so_module (static)
 http_module (static)
 access_compat_module (shared)
 actions_module (shared)
 alias_module (shared)
 allowmethods_module (shared)
 auth_basic_module (shared)
 auth_digest_module (shared)
 authn_anon_module (shared)
 authn_core_module (shared)
 authn_dbd_module (shared)
 authn_dbm_module (shared)
 authn_file_module (shared)
""".strip()


HTTPD_M_DOC = """
Loaded Modules:
 core_module (static)
 http_module (static)
 access_compat_module (shared)
 actions_module (shared)
 alias_module (shared)
Syntax OK
""".strip()


def test_httpd_M():
    result = HttpdM(context_wrap(HTTPD_M_RHEL6, path='/usr/test/httpd_-M'))
    assert result.httpd_command == '/usr/test/httpd'
    assert sorted(result.loaded_modules) == sorted(result.shared_modules + result.static_modules)
    assert 'core_module' in result
    assert result['core_module'] == 'static'

    result = HttpdM(context_wrap(HTTPD_M_RHEL7, path='/usr/tst/httpd_-M'))
    assert result.httpd_command == '/usr/tst/httpd'
    assert sorted(result.loaded_modules) == sorted(result.shared_modules + result.static_modules)
    assert 'core_module' not in result


def test_httpd_M_exp():
    with pytest.raises(ParseException) as sc:
        HttpdM(context_wrap(""))
    assert "Input content is empty." in str(sc)

    with pytest.raises(ParseException) as sc:
        HttpdM(context_wrap("HTTPD_M_24"))
    assert "Input content is not empty but there is no useful parsed data." in str(sc)


def test_httpd_M_doc():
    env = {
            'HttpdM': HttpdM,
            'hm': HttpdM(context_wrap(HTTPD_M_DOC, path='/usr/sbin/httpd_-M'))
          }
    failed, total = doctest.testmod(httpd_M, globs=env)
    assert failed == 0
