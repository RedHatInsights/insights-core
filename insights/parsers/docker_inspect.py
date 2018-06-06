"""
DockerInspect - Command ``docker inspect --type={TYPE}``
========================================================

This module parses the output of the ``docker inspect`` command.  This uses
the ``core.marshalling.unmarshal`` function to parse the JSON output from the
commands.  The data is stored as a nested dictionary in the ``data``
attribute, and uses the ``LegacyItemAccess`` mixin class to provide ``get``
and ``contains`` access to the dictionary via the object itself.

Sample input::

    [
    {
        "Id": "97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07",
        "Created": "2016-06-23T05:12:25.433469799Z",
        "Path": "/bin/bash",
        "Args": [],
        "Name": "/sample_webapp",
        "State": {
            "Status": "running",
            "Running": true,
            "Paused": false,
            "Restarting": false,
    ...

Examples:

    >>> image = shared[DockerInspectContainer]
    >>> image.data['ID'] # new-style access
    '97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07'
    >>> image['Name'] # old-style access
    '/sample_webapp'
    >>> image.get('State').get('Paused') # sub-dictionaries
    False

"""

from .. import LegacyItemAccess, parser, CommandParser
from ..core.marshalling import unmarshal
from insights.specs import Specs


class DockerInspect(LegacyItemAccess, CommandParser):
    """
    Parse the output of command "docker inspect --type=image" and "docker
    inspect --type=container".  The output of these two commands is formatted
    as JSON, so "json.loads" is an option to parse the output in the future.
    """

    def parse_content(self, content):
        content = "\n".join(list(content))
        try:
            inspect_data = unmarshal(content)
            self.data = inspect_data[0]
        except:
            self.data = {}


@parser(Specs.docker_image_inspect)
class DockerInspectImage(DockerInspect):
    """
    Parse docker image inspect output using the DockerInspect parser class.
    """
    pass


@parser(Specs.docker_container_inspect)
class DockerInspectContainer(DockerInspect):
    """
    Parse docker container inspect output using the DockerInspect parser class.
    """
    pass
