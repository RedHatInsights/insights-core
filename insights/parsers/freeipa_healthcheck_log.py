"""
freeipa_healthcheck_log - File ``/var/log/ipa/healthcheck/healthcheck.log``
===========================================================================

This module provides plugins access to file ``/var/log/ipa/healthcheck/healthcheck.log``

This file contains a list of items, each item representing a check made on the local IPA server.
The file can be either single-line or multi-line indented.

Typical content of file ``/var/log/ipa/healthcheck/healthcheck.log`` is::

    [
      {
        "source": "ipahealthcheck.ipa.roles",
        "check": "IPACRLManagerCheck",
        "result": "SUCCESS",
        "uuid": "1f4177a4-0ddb-4e4d-8258-a5cd5f4638fc",
        "when": "20191203122317Z",
        "duration": "0.002254",
        "kw": {
          "key": "crl_manager",
          "crlgen_enabled": true
        }
      },
      {
        "source": "ipahealthcheck.ipa.roles",
        "check": "IPARenewalMasterCheck",
        "result": "SUCCESS",
        "uuid": "1feb7f99-2e98-4e37-bb52-686896972022",
        "when": "20191203122317Z",
        "duration": "0.018330",
        "kw": {
          "key": "renewal_master",
          "master": true
        }
      },
      {
        "source": "ipahealthcheck.system.filesystemspace",
        "check": "FileSystemSpaceCheck",
        "result": "ERROR",
        "uuid": "90ed8765-6ad7-425c-abbd-b07a652649cb",
        "when": "20191203122221Z",
        "duration": "0.000474",
        "kw": {
          "msg": "/var/log/audit/: free space under threshold: 14 MiB < 512 MiB",
          "store": "/var/log/audit/",
          "free_space": 14,
          "threshold": 512
        }
      }
    ]

The list of errors can be accessed via the issues property.

Examples:

    >>> len(healthcheck.issues)
    1
    >>> healthcheck.issues[0]['check'] == 'FileSystemSpaceCheck'
    True

"""

from insights import parser
from insights import JSONParser
from insights.specs import Specs


@parser(Specs.freeipa_healthcheck_log)
class FreeIPAHealthCheckLog(JSONParser):
    """Parses the content of file ``/var/log/ipa/healthcheck/healthcheck.log``."""

    @property
    def issues(self):
        """ list: non-success results in healthcheck log."""
        return [entry for entry in self.data if entry["result"] != "SUCCESS"]

    def get_results(self, source, check):
        """Given a source and check find and return the result"""
        results = []
        for entry in self.data:
            if (entry.get('source') == source and entry.get('check') == check and entry.get('result') in ['ERROR', 'CRITICAL']):
                results.append(entry)

        return results
