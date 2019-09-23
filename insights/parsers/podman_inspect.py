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

    >>> image.get('ID') # new-style access
    '97d7cd1a5d8fd7730e83bb61ecbc993742438e966ac5c11910776b5d53f4ae07'
    >>> image.get('State').get('Paused') # sub-dictionaries
    False

"""

from insights import parser, CommandParser
from insights.core.marshalling import unmarshal
from insights.parsers import SkipException
from insights.specs import Specs


class PodmanInspect(CommandParser, dict):
    """
    Parse the output of command "podman inspect --type=image" and "podman
    inspect --type=container".  The output of these two commands is formatted
    as JSON, so "json.loads" is an option to parse the output in the future.

    Raises: SkipException if content is not provided
    """

    def parse_content(self, content):
        content = "\n".join(list(content))

        if not content:
            raise SkipException

        try:
            inspect_data = unmarshal(content)
            self.update(inspect_data[0])
        except:
            raise SkipException


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
