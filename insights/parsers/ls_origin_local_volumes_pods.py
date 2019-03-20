"""
LsOriginLocalVolumePods - command ``ls /var/lib/origin/openshift.local.volumes/pods``
========================================================================================
Shared parsers for parsing output of the command ``ls /var/lib/origin/openshift.local.volumes/pods``.
"""

from insights.specs import Specs
from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
import json


@parser(Specs.ls_origin_local_volumes_pods)
class LsOriginLocalVolumePods(CommandParser):
    """
    Class to parse the output of command ``ls /var/lib/origin/openshift.local.volumes/pods``.

    Sample output of the command::


        0c4c3dd9-29be-11e9-9856-001a4a1602ba  15dad82b-b70f-11e8-a370-001a4a1602ba  18b6e8aa-b70f-11e8-a370-001a4a1602ba  3ca7d1cd-ec9c-11e8-b381-001a4a1602ba  d538a202-3ff3-11e9-9856-001a4a1602ba
        0c623ca7-29be-11e9-9856-001a4a1602ba  168a59bb-e199-11e8-b381-001a4a1602ba  2cd57827-ec9c-11e8-b381-001a4a1602ba  3cc402a6-b70f-11e8-a370-001a4a1602ba  f1f0948c-3a31-11e9-9856-001a4a1602ba
        0c6998b9-29be-11e9-9856-001a4a1602ba  16975616-e199-11e8-b381-001a4a1602ba  2d5b18ea-01a1-11e9-ab6d-001a4a1602ba  b8d8fb89-2de0-11e9-9856-001a4a1602ba

    The content collected by insights-client::


        [
          "15dad82b-b70f-11e8-a370-001a4a1602ba",
          "18b6e8aa-b70f-11e8-a370-001a4a1602ba",
          "3cc402a6-b70f-11e8-a370-001a4a1602ba",
          "168a59bb-e199-11e8-b381-001a4a1602ba",
          "16975616-e199-11e8-b381-001a4a1602ba",
          "2cd57827-ec9c-11e8-b381-001a4a1602ba",
          "3ca7d1cd-ec9c-11e8-b381-001a4a1602ba",
          "2d5b18ea-01a1-11e9-ab6d-001a4a1602ba",
          "0c4c3dd9-29be-11e9-9856-001a4a1602ba",
          "0c623ca7-29be-11e9-9856-001a4a1602ba",
          "0c6998b9-29be-11e9-9856-001a4a1602ba",
          "b8d8fb89-2de0-11e9-9856-001a4a1602ba",
          "f1f0948c-3a31-11e9-9856-001a4a1602ba",
          "d538a202-3ff3-11e9-9856-001a4a1602ba"
        ]


    Examples:

        >>> str(ls_origin_local_volumes_pods.pods[1])
        '18b6e8aa-b70f-11e8-a370-001a4a1602ba'

    Attributes:
        pods (List): The list of pods uid under the directory /var/lib/origin/openshift.local.volumes/pods
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty output.")
        content = ''.join(content)
        try:
            self.data = json.loads(content)
        except Exception:
            raise ParseException("Incorrect content: '{0}'".format(content))

        if not self.data:
            raise SkipException("Empty or useless output.")

        self.pods = self.data
