"""
EngineDBQuery - command ``engine-db-query --statement "<DB_QUERY>" --json``
============================================================================

Parses the output of the command `engine-db-query` returned in JSON format.
"""
from insights.core import CommandParser, JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.engine_db_query_vdsm_version)
class EngineDBQueryVDSMversion(CommandParser, JSONParser):
    """
    Get the hostname & vdsm package version along with host info.

    Class for parsing the output of the command - ``engine-db-query --statement "SELECT vs.vds_name, rpm_version FROM vds_dynamic vd, vds_static vs WHERE vd.vds_id = vs.vds_id;" --json``.

    Attributes:
        data (dict): Host info.

    Sample output of this command is::

        {
          "id_host": "None",
          "when": "2020-06-21 12:45:59",
          "time": "0.00263094902039",
          "name": "None",
          "description": "None",
          "type": "None",
          "kb": "None",
          "bugzilla": "None",
          "file": "",
          "path": "None",
          "id": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "hash": "d41d8cd98f00b204e9800998ecf8427e",
          "result": [{"vds_name": "hosto", "rpm_version": "vdsm-4.30.40-1.el7ev"}]
        }


    Examples:
        >>> output.get('id', None) == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        True
        >>> output.result == [{'vds_name': 'hosto', 'rpm_version': 'vdsm-4.30.40-1.el7ev'}]
        True
    """
    @property
    def result(self):
        """Get the value of 'result'."""
        return self.data.get('result', [])
