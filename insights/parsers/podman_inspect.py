"""
PodmanInspect - Command ``podman inspect --type={TYPE}``
========================================================

This module parses the output of the ``podman inspect`` command.  This uses
the ``core.marshalling.unmarshal`` function to parse the JSON output from the
commands.  The data is stored as a dictionary.

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

    Raises:
        SkipException: If content is not provided
    """

    def parse_content(self, content):
        if not content:
            raise SkipException

        content = "\n".join(list(content))

        try:
            inspect_data = unmarshal(content)
            self.update(inspect_data[0])
        except:
            raise SkipException


@parser(Specs.podman_image_inspect)
class PodmanInspectImage(PodmanInspect):
    """
    Parse podman image inspect output using the PodmanInspect parser class.

    Sample input::

        [
            {
                "Id": "013125b8a088f45be8f85f88b5504f05c02463b10a6eea2b66809a262bb911ca",
                "Digest": "sha256:f9662cdd45e3db182372a4fa6bfff10e1c601cc785bac09ccae3b18f0bc429df",
                "RepoTags": [
                    "192.168.24.1:8787/rhosp15/openstack-rabbitmq:20190819.1",
                    "192.168.24.1:8787/rhosp15/openstack-rabbitmq:pcmklatest"
                ],
            ...

    Examples:
        >>> image['Id'] == '013125b8a088f45be8f85f88b5504f05c02463b10a6eea2b66809a262bb911ca'
        True
        >>> image['RepoTags'][0] == '192.168.24.1:8787/rhosp15/openstack-rabbitmq:20190819.1'
        True
    """
    pass


@parser(Specs.podman_container_inspect)
class PodmanInspectContainer(PodmanInspect):
    """
    Parse podman container inspect output using the PodmanInspect parser class.

    Sample input::

        [
            {
                "ID": "66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda",
                "Created": "2019-08-21T10:38:34.753548542Z",
                "Path": "dumb-init",
                "State": {
                    "OciVersion": "1.0.1-dev",
                    "Status": "running",
                    "Running": true,
                    "Paused": false,
                },
            ...

    Examples:
        >>> container['ID'] == '66db151828e9beede0cdd9c17fc9bd5ebb5d125dd036f7230bc6b6433e5c0dda'
        True
        >>> container['Path'] == 'dumb-init'
        True
        >>> container.get('State').get('Paused') is False
        True
    """
    pass
