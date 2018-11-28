"""
Gluster vol info - command  to retrive information of gluster volumes
=====================================================================

The parsers here provide information about the time sources used by
``glusterd``.
"""
from insights.core.plugins import parser
from insights.core import CommandParser, LegacyItemAccess
from insights.parsers import ParseException, get_active_lines
from insights.specs import Specs


@parser(Specs.gluster_v_info)
class GlusterVolInfo(LegacyItemAccess, CommandParser):
    """
    This parser processes the output of the command `gluster vol info` and provides
    the information as a dictionary.

    The LegacyItemAccess class provides some helper functions for dealing with a
    class having a `data` attribute.

    Sample input::

        Volume Name: test_vol
        Type: Replicate
        Volume ID: 2c32ed8d-5a07-4a76-a73a-123859556974
        Status: Started
        Snapshot Count: 0
        Number of Bricks: 1 x 3 = 3
        Transport-type: tcp
        Bricks:
        Brick1: 172.17.18.42:/home/brick
        Brick2: 172.17.18.43:/home/brick
        Brick3: 172.17.18.44:/home/brick

    Examples:

        >>> vol_info.data['test_vol']['Type']
        'Replicate'
    """

    def parse_content(self, content):
        """
        Override the base class parse_content to parse the output of the '''gluster vol info'''  command.
        Information that is stored in the object is made available to the rule plugins.

        Attributes:
            data (dict): Dictionary containing each of the key:value pairs from the command
                output.

        Raises:
            ParseException: raised if data is not parsable."""

        # Stored data in a dictionary data structure
        self.data = {}

        name = None
        body = {}

        # Input data is available in text file. Reading each line in file and parsing it to a dictionary.
        for line in get_active_lines(content):
            if ':' in line:
                key, val = line.strip().split(":", 1)
                key = key.strip()
                val = val.lstrip()
            else:
                raise ParseException("Unable to parse gluster volume options: {}".format(content))
            if key == "Volume Name":
                if name is None:
                    name = val
                else:
                    self.data[name] = body
                    name = val
                    body = {}
            else:
                body[key.strip()] = val.lstrip(" ")

        if name and body:
            self.data[name] = body

        if not self.data:
            # If no data is obtained in the command execution then throw an exception instead of returning an empty
            # object.  Rules depending solely on this parser will not be invoked, so they don't have to
            # explicitly check for invalid data.
            raise ParseException("Unable to parse gluster volume options: {0}".format(content))
