"""
PodmanInspect - Command ``podman inspect --type={TYPE}``
========================================================

This module parses the output of the ``podman inspect`` command.  This uses
the ``core.marshalling.unmarshal`` function to parse the JSON output from the
commands.  The data is stored as a dictionary.

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

    >>> image = shared[PodmanInspectContainer]
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


class PodmanInspect(LegacyItemAccess, CommandParser):
    """
    Parse the output of command "podman inspect --type=image" and "podman
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


@parser(Specs.podman_image_inspect)
class PodmanInspectImage(PodmanInspect):
    """
    Parse podman image inspect output using the PodmanInspect parser class.
    """
    pass


@parser(Specs.podman_container_inspect)
class PodmanInspectContainer(PodmanInspect):
    """
    Parse podman container inspect output using the PodmanInspect parser class.
    """
    pass
