"""
freeipa_healthcheck_log - File ``/var/log/ipa/healthcheck/healthcheck.log``
===========================================================================

This module provides plugins access to file ``/var/log/ipa/healthcheck/healthcheck.log``

This file contains a list of items, each item representing a check made on the local IPA server.
The file can be either single-line or multi-line indented.

Typical content of file ``/var/log/ipa/healthcheck/healthcheck.log`` is::

    [
      {
        "source": "ipahealthcheck.dogtag.ca",
        "check": "DogtagCertsConfigCheck",
        "severity": 0,
        "uuid": "57f7d2c9-f71f-4c2f-b831-9e30250b18b2",
        "when": "20190726213428Z",
        "duration": "0.150333",
        "kw": {
          "key": "subsystemCert cert-pki-ca",
          "configfile": "/var/lib/pki/pki-tomcat/conf/ca/CS.cfg"
        }
      },
      {
        "source": "ipahealthcheck.ipa.certs",
        "check": "IPACertmongerExpirationCheck",
        "severity": 0,
        "uuid": "afd047c2-d78b-4c5c-b3a4-f68578ee1595",
        "when": "20190726213429Z",
        "duration": "0.007105",
        "kw": {
          "key": "20190620165230"
        }
      },
      {
        "source": "ipahealthcheck.ds.replication",
        "check": "ReplicationConflictCheck",
        "severity": 0,
        "uuid": "99c0a513-447c-46f1-95ea-058fc0db6075",
        "when": "20190726213429Z",
        "duration": "0.001409",
        "kw": {}
      },
      {
        "source": "ipahealthcheck.ipa.files",
        "check": "IPAFileNSSDBCheck",
        "severity": 0,
        "uuid": "7e8a7739-c4d6-4b97-b602-9f9e981f793c",
        "when": "20190726213432Z",
        "duration": "0.000765",
        "kw": {
          "key": "_etc_pki_pki-tomcat_alias_cert9.db_owner",
          "type": "owner",
          "path": "/etc/pki/pki-tomcat/alias/cert9.db"
        }
      },
      {
        "source": "ipahealthcheck.ipa.topology",
        "check": "IPATopologyDomainCheck",
        "severity": 0,
        "uuid": "c5ee8ee1-98d1-4696-bbf1-8243677b8918",
        "when": "20190726213432Z",
        "duration": "0.019070",
        "kw": {
          "suffix": "ca"
        }
      },
      {
        "source": "ipahealthcheck.system.filesystemspace",
        "check": "FileSystemSpaceCheck",
        "severity": 2,
        "uuid": "4d1c71c5-cc37-4ebf-b53c-34f4e4534437",
        "when": "20190726213432Z",
        "duration": null,
        "kw": {
          "msg": "/var/lib/dirsrv/: free space percentage under threshold: 1% < 20%",
          "store": "/var/lib/dirsrv/",
          "percent_free": 1,
          "threshold": 20
        }
      }
    ]

The list of errors can be accessed via the errors property.

Examples:

    >>> len(healthcheck.errors)
    1
    >>> healthcheck.errors[0]['check'] == 'FileSystemSpaceCheck'
    True

"""

from insights import parser
from insights import JSONParser
from insights.specs import Specs


@parser(Specs.freeipa_healthcheck_log)
class FreeIPAHealthCheckLog(JSONParser):
    """Parses the content of file ``/var/log/ipa/healthcheck/healthcheck.log``."""

    @property
    def errors(self):
        """ list: errors in healthcheck log."""
        return [entry for entry in self.data if entry['severity'] > 0]
