"""
LsOriginLocalVolumePods - command ``ls /var/lib/origin/openshift.local.volumes/pods``
========================================================================================
Shared parsers for parsing output of the command ``ls /var/lib/origin/openshift.local.volumes/pods``.
"""

from insights.specs import Specs
from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
import re


@parser(Specs.ls_origin_local_volumes_pods)
class LsOriginLocalVolumePods(CommandParser):
    """
    Class to parse the output of command ``ls /var/lib/origin/openshift.local.volumes/pods``.

    Sample output of the command::


        5946c1f644096161a1242b3de0ee5875      7ad952a0-d34e-11e8-a142-001a4a160152  8e879171c85e221fb0a023e3f10ca276      dcf2fe412f6a174b0e1f360c2e0eb0a7
        6ea3d5cd-d34e-11e8-a142-001a4a160152  7b63e8aa-d34e-11e8-a142-001a4a160152  b6b60cca-d34f-11e8-a142-001a4a160152  ef66562d-d34f-11e8-a142-001a4a160152
        77d6d959-d34f-11e8-a142-001a4a160152  7d1f9443-d34f-11e8-a142-001a4a160152  bc70730f-d34f-11e8-a142-001a4a160152

    The content collected by insights-client::


        5946c1f644096161a1242b3de0ee5875
        6ea3d5cd-d34e-11e8-a142-001a4a160152
        77d6d959-d34f-11e8-a142-001a4a160152
        7ad952a0-d34e-11e8-a142-001a4a160152
        7b63e8aa-d34e-11e8-a142-001a4a160152
        7d1f9443-d34f-11e8-a142-001a4a160152
        8e879171c85e221fb0a023e3f10ca276
        b6b60cca-d34f-11e8-a142-001a4a160152
        bc70730f-d34f-11e8-a142-001a4a160152
        dcf2fe412f6a174b0e1f360c2e0eb0a7
        ef66562d-d34f-11e8-a142-001a4a160152


    Examples:

        >>> str(ls_origin_local_volumes_pods.data[1])
        '6ea3d5cd-d34e-11e8-a142-001a4a160152'

    Attributes:
        data (List): The list of pods uid under the directory /var/lib/origin/openshift.local.volumes/pods
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("Empty output.")
        for row in content:
            if not re.match('[0-9|a-e|\-]+', row):
                raise ParseException("Incorrect content: '{0}'".format(content))

        self.data = content
