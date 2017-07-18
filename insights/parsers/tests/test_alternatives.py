from insights.tests import context_wrap
from insights.parsers.alternatives import JavaAlternatives
from insights.core import ParseException

import pytest

JAVA_ALTERNATIVES = """
java - status is auto.
 link currently points to /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b15.el7_2.x86_64/jre/bin/java
/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.111-2.6.7.2.el7_2.x86_64/jre/bin/java - priority 1700111
/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b15.el7_2.x86_64/jre/bin/java - priority 1800111
/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java - priority 16091
 slave ControlPanel: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/ControlPanel
 slave keytool: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/keytool
 slave policytool: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/policytool
 slave rmid: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/rmid
Current `best' version is /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java.
"""

BAD_ALTERNATIVES_OUTPUT = """
COMMAND> alternatives --display java
java - status is auto.
 link currently points to /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.131-3.b12.el7_3.x86_64/jre/bin/java
/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.141-2.6.10.1.el7_3.x86_64/jre/bin/java - family java-1.7.0-openjdk.x86_64 priority 1700141
 slave jjs: (null)
"""

TWO_ALTERNATIVES_OUTPUT = """
java - status is auto.
 link currently points to /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.131-3.b12.el7_3.x86_64/jre/bin/java
/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.141-2.6.10.1.el7_3.x86_64/jre/bin/java - family java-1.7.0-openjdk.x86_64 priority 1700141
 slave jjs: (null)
 slave keytool: /usr/lib/jvm/java-1.7.0-openjdk-1.7.0.141-2.6.10.1.el7_3.x86_64/jre/bin/keytool
 slave orbd: /usr/lib/jvm/java-1.7.0-openjdk-1.7.0.141-2.6.10.1.el7_3.x86_64/jre/bin/orbd
 slave pack200: /usr/lib/jvm/java-1.7.0-openjdk-1.7.0.141-2.6.10.1.el7_3.x86_64/jre/bin/pack200
 slave policytool: (null)
 slave rmid: /usr/lib/jvm/java-1.7.0-openjdk-1.7.0.141-2.6.10.1.el7_3.x86_64/jre/bin/rmid
 slave rmiregistry: /usr/lib/jvm/java-1.7.0-openjdk-1.7.0.141-2.6.10.1.el7_3.x86_64/jre/bin/rmiregistry
mta - status is auto.
 link currently points to /usr/sbin/sendmail.postfix
/usr/sbin/sendmail.postfix - priority 30
 slave mta-mailq: /usr/bin/mailq.postfix
 slave mta-newaliases: /usr/bin/newaliases.postfix
 slave mta-pam: /etc/pam.d/smtp.postfix
 slave mta-rmail: /usr/bin/rmail.postfix
 slave mta-sendmail: /usr/lib/sendmail.postfix
 slave mta-mailqman: /usr/share/man/man1/mailq.postfix.1.gz
 slave mta-newaliasesman: /usr/share/man/man1/newaliases.postfix.1.gz
 slave mta-sendmailman: /usr/share/man/man1/sendmail.postfix.1.gz
 slave mta-aliasesman: /usr/share/man/man5/aliases.postfix.5.gz
Current `best' version is /usr/sbin/sendmail.postfix.
"""


def test_java_alternatives():
    java = JavaAlternatives(context_wrap(JAVA_ALTERNATIVES))
    assert java.program == 'java'
    assert java.status == 'auto'
    assert java.link == '/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.111-1.b15.el7_2.x86_64/jre/bin/java'
    assert java.best == '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java'
    assert len(java.paths) == 3
    assert java.paths[0]['path'] == '/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.111-2.6.7.2.el7_2.x86_64/jre/bin/java'
    assert java.paths[0]['priority'] == 1700111
    assert java.paths[2]['slave']['ControlPanel'] == '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/ControlPanel'


def test_alternatives_failures():
    with pytest.raises(ParseException) as exc:
        java = JavaAlternatives(context_wrap(TWO_ALTERNATIVES_OUTPUT))
    assert 'Program line for mta found in output for java' in str(exc)

    java = JavaAlternatives(context_wrap(BAD_ALTERNATIVES_OUTPUT))
    assert java.program == 'java'
