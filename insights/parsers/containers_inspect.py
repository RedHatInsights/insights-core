"""
Containers inspect
==================

This parser reads the output of commands: "/usr/bin/docker|podman inspect <containers ID>"
which are used to show the metadata information of containers.
"""
from insights import parser, JSONParser
from insights.specs import Specs


@parser(Specs.containers_inspect)
class ContainersInspect(JSONParser):
    """
    Class for parsing the output of the containers inspect commands
    ``/usr/bin/docker|podman inspect <containers ID>``


    Typical Output of this command after datasource containers_inspect is::

        [
            {
                "Id": "aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8",
                "Image": "538460c14d75dee1504e56ad8ddb7fe039093b1530ef8f90442a454b9aa3dc8b",
                "engine": "podman",
                "Privileged": false,
                "Cmd": ["sleep", "1000000"]
            }
        ]

    Attributes:
        data (list): A list containing the parsed information

    Examples:
        >>> str(inspect_containers.data[0]["Id"])
        'aeaea3ead527'
        >>> str(inspect_containers.data[0]["engine"])
        'podman'
        >>> inspect_containers.data[0]["Privileged"]
        False
    """

    def parse_content(self, content):
        super(ContainersInspect, self).parse_content(content[0])
