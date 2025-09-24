"""
CrictlPs - command ``crictl ps --quiet``
========================================

This parser reads the output of ``crictl ps --quiet`` command and returns a list of
container records with their associated metadata. The parser handles various container
states and time formats in the "created" field.

The parser is designed to handle the complex structure of crictl output where the
"created" field may contain spaces (e.g., "About a minute ago", "2 hours ago") and
uses intelligent parsing to correctly separate fields.
"""  # noqa: E501

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.core.exceptions import ParseException, SkipComponent


@parser(Specs.crictl_ps)
class CrictlPs(CommandParser, list):
    """
    Parser for the output of ``crictl ps --quiet`` command.

    The parser is designed to handle the complex structure of crictl output where the
    "created" field may contain spaces (e.g., "About a minute ago", "2 hours ago") and
    uses intelligent parsing to correctly separate fields.

    Sample input::

        CONTAINER           IMAGE                                                                                                                        CREATED              STATE               NAME                                          ATTEMPT             POD ID              POD
        93b10093a8263       bea2d277eb71530a376a68be9760260cedb59f2392bb6e7793b05d5350df8d4c                                                             About a minute ago   Running             oauth-apiserver                               185                 19d971fe5c478       apiserver-7cd97c59ff-dwckz
        e34ce05ade472       2c96c7c72cf99490b4bdbb7389020b7e4b5bb7dc43ea9cadc4d5af43cb300b3f                                                             9 days ago           Running             guard                                         1                   c48cc19e5b0b1       etcd-guard-nah-4jnq5-master-v8z5h-0
        471d75b135b5b       90e50eece96ef2a252b729a76a2ee3360d3623295cceb7d3e623b55cb7aef30a                                                             9 days ago           Running             etcd                                          39                  d2dd84f8db754       etcd-nah-4jnq5-master-v8z5h-0

    The parser returns a list of dictionaries, each containing one container record with the
    following fields:
    - container_id (str): The container ID (e.g., '93b10093a8263')
    - image (str): The container image hash or reference (e.g., 'bea2d277eb71530a...')
    - created (str): When the container was created (e.g., 'About a minute ago', '9 days ago')
    - state (str): Current container state (e.g., 'Running', 'Exited', 'ContainerCreating', 'Unknown')
    - name (str): Container name (e.g., 'oauth-apiserver')
    - attempt (str): Container restart attempt number (e.g., '185')
    - pod_id (str): Associated pod ID (e.g., '19d971fe5c478')
    - pod (str): Associated pod name (e.g., 'apiserver-7cd97c59ff-dwckz')

    Supported Container States:
    - Running: Container is currently running
    - Exited: Container has exited
    - Created: Container has been created but not started
    - ContainerCreating: Container is in the process of being created
    - Unknown: Container state is unknown
    - Pending: Container is pending (waiting for resources)

    Examples:

        Basic usage:
        >>> crictl_ps = CrictlPs(context)
        >>> len(crictl_ps)
        3
        >>> crictl_ps[0]['container_id']
        '93b10093a8263'
        >>> crictl_ps[0]['image']
        'bea2d277eb71530a376a68be9760260cedb59f2392bb6e7793b05d5350df8d4c'
        >>> crictl_ps[0]['created']
        'About a minute ago'
        >>> crictl_ps[0]['state']
        'Running'
        >>> crictl_ps[0]['name']
        'oauth-apiserver'
        >>> crictl_ps[0]['attempt']
        '185'
        >>> crictl_ps[0]['pod_id']
        '19d971fe5c478'
        >>> crictl_ps[0]['pod']
        'apiserver-7cd97c59ff-dwckz'

    Raises:
        ParseException: If the input content is invalid or doesn't contain the expected
            header line with "CONTAINER" keyword.
        SkipComponent: If no container records are found after parsing.
    """

    def parse_content(self, content):
        """
        Parse the crictl ps output content.

        Args:
            content (list): List of strings representing the crictl ps output lines.

        Raises:
            ParseException: If the content is invalid or doesn't contain the expected header.
            SkipComponent: If no container records are found after parsing.
        """
        if len(content) < 1 or "CONTAINER" not in content[0]:
            raise ParseException("invalid content: {0}".format(content) if content else 'empty file')

        # Skip the header line
        for line in content[1:]:
            line = line.strip()
            if not line:
                continue

            # Parse each line manually to handle the space-containing "created" field
            parsed = self._parse_line(line)
            if parsed:
                self.append(parsed)

        # Raise SkipComponent if no containers were found
        if not self:
            raise SkipComponent("No container records found")

    def _parse_line(self, line):
        """
        Parse a single line of crictl ps output.

        This method handles the complex parsing logic required for crictl output
        where the "created" field may contain spaces and the image field can be
        very long.

        Args:
            line (str): A single line from crictl ps output.

        Returns:
            dict: Parsed container record with all fields, or None if parsing fails.

        Note:
            The parsing logic:
            1. Splits the line by whitespace
            2. First two fields are always container_id and image
            3. Finds the state field by looking for known state keywords
            4. Everything between image and state is the "created" field
            5. Remaining fields are mapped in order: name, attempt, pod_id, pod
        """
        # Split by whitespace
        parts = line.split()

        if len(parts) < 8:
            return None

        # The structure is:
        # container_id image created... state name attempt pod_id pod

        # Find the state field (it's always a single word like "Running", "Exited", etc.)
        # Look for common state values
        state_keywords = ['Running', 'Exited', 'Created', 'Unknown', 'ContainerCreating', 'Pending']
        state_index = None
        for i, part in enumerate(parts[2:], 2):
            if part in state_keywords:
                state_index = i
                break

        if state_index is None:
            return None

        # The remaining parts after state
        remaining = parts[state_index + 1:]

        if len(remaining) < 4:
            return None

        return {
            'container_id': parts[0],  # First two parts are always container_id and image
            'image': parts[1],
            'created': ' '.join(parts[2:state_index]),  # Everything between image and state is the "created" field
            'state': parts[state_index],  # The state is at state_index
            'name': remaining[-4],  # The last 4 parts are: name, attempt, pod_id, pod
            'attempt': remaining[-3],
            'pod_id': remaining[-2],
            'pod': remaining[-1]
        }

    @property
    def container_ids(self):
        return [record['container_id'] for record in self]
