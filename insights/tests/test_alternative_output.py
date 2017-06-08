# -*- coding: UTF-8 -*-
from insights.core import AlternativesOutput
from insights.tests import context_wrap
from insights.parsers import ParseException

import unittest

ALT_JAVA_160 = """
java - status is auto.
 link currently points to /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java
/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java - priority 16091
 slave ControlPanel: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/ControlPanel
 slave keytool: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/keytool
 slave policytool: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/policytool
 slave rmid: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/rmid
 slave rmiregistry: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/rmiregistry
 slave tnameserv: /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/tnameserv
 slave jre_exports: /usr/lib/jvm-exports/jre-1.6.0-ibm.x86_64
 slave jre: /usr/lib/jvm/jre-1.6.0-ibm.x86_64
/usr/lib/jvm/jre-1.4.2-gcj/bin/java - priority 1420
 slave ControlPanel: (null)
 slave keytool: /usr/lib/jvm/jre-1.4.2-gcj/bin/keytool
 slave policytool: (null)
 slave rmid: (null)
 slave rmiregistry: /usr/lib/jvm/jre-1.4.2-gcj/bin/rmiregistry
 slave tnameserv: (null)
 slave jre_exports: /usr/lib/jvm-exports/jre-1.4.2-gcj
 slave jre: /usr/lib/jvm/jre-1.4.2-gcj
Current `best' version is /usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java.
"""

ALT_MTA = """
mta - status is auto.
 link currently points to /usr/sbin/sendmail.postfix
/usr/sbin/sendmail.postfix - priority 30
 slave mta-mailq: /usr/bin/mailq.postfix
 slave mta-newaliases: /usr/bin/newaliases.postfix
Current `best' version is /usr/sbin/sendmail.postfix.
"""

DUPLICATED_STATUS_LINE = """
mta - status is auto.
mta - status is auto.
"""

MISSING_STATUS_LINE = """
 link currently points to /usr/sbin/sendmail.postfix
/usr/sbin/sendmail.postfix - priority 30
 slave mta-mailq: /usr/bin/mailq.postfix
 slave mta-newaliases: /usr/bin/newaliases.postfix
Current `best' version is /usr/sbin/sendmail.postfix.
"""


class TestAlternatives(unittest.TestCase):
    def test_basic_alternatives(self):
        java = AlternativesOutput(context_wrap(ALT_JAVA_160, path='/etc/alternatives/java'))
        self.assertTrue(hasattr(java, 'program'))
        self.assertEqual(java.program, 'java')
        self.assertTrue(hasattr(java, 'status'))
        self.assertEqual(java.status, 'auto')
        self.assertTrue(hasattr(java, 'link'))
        self.assertEqual(java.link, '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java')
        self.assertTrue(hasattr(java, 'best'))
        self.assertEqual(java.best, '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java')

        self.assertTrue(hasattr(java, 'paths'))
        self.assertIsInstance(java.paths, list)
        self.assertEqual(len(java.paths), 2)

        self.assertIn('path', java.paths[0])
        self.assertIn('priority', java.paths[0])
        self.assertIn('slave', java.paths[0])
        self.assertEqual(java.paths[0]['path'], '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/java')
        self.assertEqual(java.paths[0]['priority'], 16091)
        self.assertIsInstance(java.paths[0]['slave'], dict)
        self.assertEqual(sorted(java.paths[0]['slave'].keys()), sorted([
            'ControlPanel', 'keytool', 'policytool', 'rmid', 'rmiregistry',
            'tnameserv', 'jre_exports', 'jre'
        ]))
        self.assertEqual(java.paths[0]['slave']['ControlPanel'], '/usr/lib/jvm/jre-1.6.0-ibm.x86_64/bin/ControlPanel')

        self.assertIn('path', java.paths[1])
        self.assertIn('priority', java.paths[1])
        self.assertIn('slave', java.paths[1])
        self.assertEqual(java.paths[1]['path'], '/usr/lib/jvm/jre-1.4.2-gcj/bin/java')
        self.assertEqual(java.paths[1]['priority'], 1420)
        self.assertIsInstance(java.paths[1]['slave'], dict)
        self.assertEqual(sorted(java.paths[1]['slave'].keys()), sorted([
            'ControlPanel', 'keytool', 'policytool', 'rmid', 'rmiregistry',
            'tnameserv', 'jre_exports', 'jre'
        ]))
        self.assertEqual(java.paths[1]['slave']['ControlPanel'], '(null)')

    def test_mta_alternatives(self):
        mtas = AlternativesOutput(context_wrap(ALT_MTA))

        self.assertTrue(hasattr(mtas, 'program'))
        self.assertEqual(mtas.program, 'mta')
        self.assertTrue(hasattr(mtas, 'status'))
        self.assertEqual(mtas.status, 'auto')
        self.assertTrue(hasattr(mtas, 'link'))
        self.assertEqual(mtas.link, '/usr/sbin/sendmail.postfix')
        self.assertTrue(hasattr(mtas, 'best'))
        self.assertEqual(mtas.best, '/usr/sbin/sendmail.postfix')

        self.assertTrue(hasattr(mtas, 'paths'))
        self.assertIsInstance(mtas.paths, list)
        self.assertEqual(len(mtas.paths), 1)

        self.assertIn('path', mtas.paths[0])
        self.assertIn('priority', mtas.paths[0])
        self.assertIn('slave', mtas.paths[0])

    def test_failure_modes(self):
        # Duplicate status line raises ParseException
        with self.assertRaisesRegexp(ParseException, 'Program line for mta'):
            alts = AlternativesOutput(context_wrap(DUPLICATED_STATUS_LINE))
            self.assertIsNone(alts.program)

        # Missing status line results in no data
        alts = AlternativesOutput(context_wrap(MISSING_STATUS_LINE))
        self.assertIsNone(alts.program)
        self.assertIsNone(alts.status)
        self.assertIsNone(alts.link)
        self.assertIsNone(alts.best)
        self.assertEqual(alts.paths, [])
