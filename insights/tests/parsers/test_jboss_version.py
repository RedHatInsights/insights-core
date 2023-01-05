from insights.parsers.jboss_version import JbossVersion, JbossRuntimeVersions
from insights.tests import context_wrap
import doctest
from insights.parsers import jboss_version

JBOSS_6 = """
Red Hat JBoss Enterprise Application Platform - Version 6.4.3.GA
""".strip()

JBOSS_7 = """
Red Hat JBoss Enterprise Application Platform - Version 7.1.0.Beta1
""".strip()


def test_jboss6():
    release6 = JbossVersion(context_wrap(JBOSS_6, path='/home/test/jboss/jboss-eap-6.4/version.txt'))
    assert release6.file_path == '/home/test/jboss/jboss-eap-6.4/version.txt'
    assert release6.raw == JBOSS_6
    assert release6.major == 6
    assert release6.minor == 4
    assert release6.version == "6.4.3"
    assert release6.code_name == "GA"
    assert release6.release == 3


def test_jboss7():
    release7 = JbossVersion(context_wrap(JBOSS_7, path='/home/test/jboss/jboss-eap-7.1/version.txt'))
    assert release7.file_path == '/home/test/jboss/jboss-eap-7.1/version.txt'
    assert release7.raw == JBOSS_7
    assert release7.major == 7
    assert release7.minor == 1
    assert release7.version == "7.1.0"
    assert release7.code_name == "Beta1"
    assert release7.release == 0


SINGLE_JBOSS = """
{"/opt/jboss-datagrid-7.3.0-server": "Red Hat Data Grid - Version 7.3.0"}
"""

MULTI_JBOSS = """
{"/opt/jboss": "Red Hat JBoss Enterprise Application Platform - Version 7.3.0.GA\n", "/opt/jboss-sss": "Red Hat Single Sign-On - Version 7.4.10.GA\n", "/opt/jboss-keycloak": "Keycloak - Version 3.4.3.Final\n"}
"""
WEB_SERVER_RUNTIME = """
{"/opt/jboss-web-server": "Red Hat JBoss Web Server - Version 5.6 GA\n\nJava Components:\nApache Tomcat 9.0.50-3.redhat_00004.1.el7jws\nTomcat Vault 1.1.8-4.Final_redhat_00004.1.el7jws\nJBoss mod_cluster 1.4.3-2.Final_redhat_00002.1.el7jws\n\nNative Components:\nApache Tomcat Native 1.2.30-3.redhat_3.el7jws\\nApache Portable Runtime (APR) 1.6.3-107.jbcs.el7\nOpenSSL 1.1.1g-8.jbcs.el7\n"}
"""


def test_JbossRuntimeVersions():
    jboss_runtimes = JbossRuntimeVersions(context_wrap(SINGLE_JBOSS))
    jboss_v = jboss_runtimes[0]
    assert jboss_v.file_path == "/opt/jboss-datagrid-7.3.0-server"
    assert jboss_v.product == "Red Hat Data Grid"
    assert jboss_v.version == "7.3.0"
    assert jboss_v.major == 7
    assert jboss_v.minor == 3
    assert jboss_v.release == 0
    jboss_runtimes = JbossRuntimeVersions(context_wrap(MULTI_JBOSS))
    for j in jboss_runtimes:
        assert 'Red Hat' in j.product or 'Keycloak' in j.product
    jboss_v = jboss_runtimes[0]
    assert jboss_v.file_path == "/opt/jboss"
    assert jboss_v.version == "7.3.0"
    assert jboss_v.code_name == "GA"
    jboss_v = jboss_runtimes[2]
    assert jboss_v.file_path == "/opt/jboss-keycloak"
    assert jboss_v.version == "3.4.3"
    assert jboss_v.code_name == "Final"
    jboss_runtimes = JbossRuntimeVersions(context_wrap(WEB_SERVER_RUNTIME))
    jboss_v = jboss_runtimes[0]
    assert jboss_v.product == "Red Hat JBoss Web Server"
    assert jboss_v.file_path == "/opt/jboss-web-server"
    assert jboss_v.code_name == "GA"
    assert jboss_v.version == "5.6"
    assert jboss_v.major == 5
    assert jboss_v.minor == 6
    assert jboss_v.release == 0


def test_jboss_version_doc_examples():
    env = {
        'jboss_version': JbossVersion(context_wrap(JBOSS_6,
                                                   path='/home/test/jboss/jboss-eap-6.4/version.txt')),
        'all_jboss_versions': JbossRuntimeVersions(context_wrap(SINGLE_JBOSS,
                                                                path='/home/test/jboss/jboss_versions'))
    }
    failed, total = doctest.testmod(jboss_version, globs=env)
    assert failed == 0
