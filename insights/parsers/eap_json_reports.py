"""
EAP Json Report Files
=====================
EAP runtime will generate JSON report files under /var/tmp/insights-runtimes/uploads/

This module provides processing for the json report files of EAP runtimes.
"""

from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.eap_json_reports)
class EAPJSONReports(JSONParser):
    """
    Class to parse the EAP json report files.

        Sample input data::

         {
           "version": "1.0.0",
           "idHash": "e38277334d0f6b6fdc6f3b831fb102cdd70f04faab5c38b0be36fb1aacb4236e",
           "basic": {
               "app.user.dir": "/opt/t_eap/jboss-eap-7.4",
               "java.specification.version": "1.8",
               "java.runtime.version": "1.8.0_362-b09",
               "java.class.path": "/opt/t_eap/jboss-eap-7.4/jboss-modules.jar",
               "system.os.version": "4.18.0-425.13.1.el8_7.x86_64",
               "jvm.args": [
                   "-D[Standalone]",
                   "-verbose:gc",
                   "-Xloggc:/opt/t_eap/jboss-eap-7.4/standalone/log/gc.log",
                   "-Djboss.modules.system.pkgs=org.jboss.byteman",
                   "-Dorg.jboss.boot.log.file=/opt/t_eap/jboss-eap-7.4/standalone/log/server.log",
                   "-Dlogging.configuration=file:/opt/t_eap/jboss-eap-7.4/standalone/configuration/logging.properties"
                 ]
                }
         }

    Examples:
        >>> type(eap_json_report)
        <class 'insights.parsers.eap_json_reports.EAPJSONReports'>
        >>> str(eap_json_report["version"])
        '1.0.0'
        >>> "idHash" in eap_json_report
        True
    """
    pass
