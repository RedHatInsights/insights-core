"""
DockerList - command ``/usr/bin/docker (images|ps)``
====================================================

Parse the output of command "docker_list_images" and "docker_list_containers",
which have very similar formats.

The header line is parsed and used as the names for the remaining columns.
All fields in both header and data are assumed to be separated by at least
three spaces.  This allows single spaces in values and headers, so headers
such as 'IMAGE ID' are captured as is.

If the header line and at least one data line are not found, no data is
stored.

Each row is stored as a dictionary, keyed on the header fields.  The data is
available in two formats:

* The old format is a list of row dictionaries.
* The new format stores each dictionary in a dictionary keyed on the value of
  a given field, given by the subclass.

Sample output of command ``/usr/bin/docker images --all --no-trunc --digests``::

    REPOSITORY                           TAG                 DIGEST              IMAGE ID                                                           CREATED             VIRTUAL SIZE
    rhel7_imagemagick                    latest              <none>              882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2   4 days ago          785.4 MB
    rhel6_nss-softokn                    latest              <none>              dd87dad2c7841a19263ae2dc96d32c501ee84a92f56aed75bb67f57efe4e48b5   5 days ago          449.7 MB


Sample output of command ``/usr/bin/docker ps --all --no-trunc --size``::

    CONTAINER ID                                                       IMAGE                                                              COMMAND                                            CREATED             STATUS                        PORTS                  NAMES               SIZE
    95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102   bd8638c869ea40a9269d87e9af6741574562af9ee013e03ac2745fb5f59e2478   "/bin/sh -c 'yum install -y vsftpd-2.2.2-6.el6'"   51 minutes ago      Exited (137) 50 minutes ago                          tender_rosalind     4.751 MB (virtual 200.4 MB)
    03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216   rhel7_httpd                                                        "/usr/sbin/httpd -DFOREGROUND"                     45 seconds ago      Up 37 seconds                 0.0.0.0:8080->80/tcp   angry_saha          796 B (virtual 669.2 MB)

Examples:

    >>> images = shared[DockerListImages]
    >>> images.rows[0]['REPOSITORY']
    'rhel7_imagemagick'
    >>> images.rows[1]['VIRTUAL SIZE']
    '449.7 MB'
    >>> images.data['rhel7_imagemagick']['CREATED'] # keyed on REPOSITORY
    '4 days ago'
    >>> images.data['rhel6_nss-softokn']['VIRTUAL SIZE']
    '449.7 MB'

    >>> containers = shared[DockerListContainers]
    >>> containers.rows[0]['STATUS']
    'Exited (137) 50 minutes ago'
    >>> containers.data['tender_rosalind']['STATUS'] # keyed on NAMES
    'Exited (137) 50 minutes ago'

"""

from .. import parser, CommandParser
import re
from insights.specs import Specs


class DockerList(CommandParser):
    """
    A general class for parsing tabular docker list information.  Parsing
    rules are:

    * The first line is the header line.
    * The other lines are data lines.
    * All fields line up vertically.
    * Fields are separated from each other by at least three spaces.
    * Some fields can contain nothing, and this is shown as spaces, so we
      need to catch that and turn it into None.

    Why not just use hard-coded fields and columns?  So that we can adapt to
    different output lists.
    """
    key_field = None

    def parse_content(self, content):
        """
        Parse the lines given into a list of dictionaries for each row.  This
        is stored in the ``rows`` attribute.

        If the ``key_field`` property is set, use this to key a ``data``
        dictionary attribute.
        """
        self.rows = []
        if len(content) < 2:
            self.no_data = True
            return

        # Parse header, remembering column numbers for data capture.  We use
        # a finditer to get the positions, and we find by field rather than
        # splitting on three or more spaces because of this.
        headers = []
        field_re = re.compile(r'\w+(\s\w+)*')
        for match in field_re.finditer(content[0]):
            headers.append({'name': match.group(), 'start': match.start()})

        # Parse the rest of the line.  Each field starts at the column
        # given by the header and ends with at least three spaces.
        for line in content[1:]:
            # I think the dictionary comprehension version of this is too
            # complicated for words :-)
            row = {}
            for header in headers:
                value = line[header['start']:].split('   ', 1)[0]
                if value == '':
                    value = None
                row[header['name']] = value
            self.rows.append(row)

        # If we have a key_field set, construct a data dictionary on it.
        # Note that duplicates will be overwritten, but we ignore '<none>'.
        if self.key_field and self.key_field in self.rows[0]:
            self.data = {}
            for row in self.rows:
                k = row[self.key_field]
                if k is not None and k != '<none>':
                    self.data[k] = row


@parser(Specs.docker_list_images)
class DockerListImages(DockerList):
    """
    Handle the list of docker images using the DockerList parser class.
    """
    key_field = 'REPOSITORY'


@parser(Specs.docker_list_containers)
class DockerListContainers(DockerList):
    """
    Handle the list of docker images using the DockerList parser class.
    """
    key_field = 'NAMES'
