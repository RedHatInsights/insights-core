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

"""
from insights import CommandParser, parser
from insights.parsers import SkipException, parse_fixed_table
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

    Raises:
        NotImplementedError: If `key_field` or `attr_name` is not defined
        SkipException: If no data to parse
    """
    key_field = None
    heading_ignore = []
    attr_name = ''
    substitutions = []

    def parse_content(self, content):
        """
        Parse the lines given into a list of dictionaries for each row.  This
        is stored in the ``rows`` attribute.

        If the ``key_field`` property is set, use this to key a ``data``
        dictionary attribute.
        """
        if not (self.key_field and self.attr_name):
            raise NotImplementedError("'key_field' or 'attr_name' is not defined")

        self.rows = parse_fixed_table(content,
                                      heading_ignore=self.heading_ignore,
                                      header_substitute=self.substitutions)

        if not self.rows:
            raise SkipException('No data.')

        data = {}
        for row in self.rows:
            k = row.get(self.key_field)
            for sub in self.substitutions:
                row[sub[0]] = row.pop(sub[1]) if sub[1] in row else None
            if k is not None and k != '<none>':
                data[k] = row
        setattr(self, self.attr_name, data)


@parser(Specs.docker_list_images)
class DockerListImages(DockerList):
    """
    Handle the list of docker images using the DockerList parser class.

    Sample output of command ``docker images --all --no-trunc --digests``::

        REPOSITORY                           TAG                 DIGEST              IMAGE ID                                                           CREATED             VIRTUAL SIZE
        rhel7_imagemagick                    latest              <none>              882ab98aae5394aebe91fe6d8a4297fa0387c3cfd421b2d892bddf218ac373b2   4 days ago          785.4 MB
        rhel6_nss-softokn                    latest              <none>              dd87dad2c7841a19263ae2dc96d32c501ee84a92f56aed75bb67f57efe4e48b5   5 days ago          449.7 MB

    Attributes:
        rows (list): List of row dictionaries.
        images (dict): Dictionary keyed on the value of the "REPOSITORY" fileld

    Examples:
        >>> images.rows[0]['REPOSITORY']
        'rhel6_vsftpd'
        >>> images.rows[1]['VIRTUAL SIZE']
        '785.4 MB'
        >>> images.images['rhel6_vsftpd']['CREATED']
        '37 minutes ago'
    """
    key_field = 'REPOSITORY'
    heading_ignore = [key_field]
    attr_name = 'images'
    substitutions = [("IMAGE ID", "IMAGE_ID"), ("VIRTUAL SIZE", "VIRTUAL_SIZE")]

    @property
    def data(self):
        return self.images


@parser(Specs.docker_list_containers)
class DockerListContainers(DockerList):
    """
    Handle the list of docker images using the DockerList parser class.

    Sample output of command ``docker ps --all --no-trunc --size``::

        CONTAINER ID                                                       IMAGE                                                              COMMAND                                            CREATED             STATUS                        PORTS                  NAMES               SIZE
        95516ea08b565e37e2a4bca3333af40a240c368131b77276da8dec629b7fe102   bd8638c869ea40a9269d87e9af6741574562af9ee013e03ac2745fb5f59e2478   "/bin/sh -c 'yum install -y vsftpd-2.2.2-6.el6'"   51 minutes ago      Exited (137) 50 minutes ago                          tender_rosalind     4.751 MB (virtual 200.4 MB)
        03e2861336a76e29155836113ff6560cb70780c32f95062642993b2b3d0fc216   rhel7_httpd                                                        "/usr/sbin/httpd -DFOREGROUND"                     45 seconds ago      Up 37 seconds                 0.0.0.0:8080->80/tcp   angry_saha          796 B (virtual 669.2 MB)

    Attributes:
        rows (list): List of row dictionaries.
        containers(dict): Dictionary keyed on the value of the "NAMES" field

    Examples:
        >>> containers.rows[0]['STATUS']
        'Up 37 seconds'
        >>> containers.containers['tender_rosalind']['STATUS']
        'Exited (137) 18 hours ago'
    """
    key_field = 'NAMES'
    heading_ignore = ['CONTAINER']
    attr_name = 'containers'
    substitutions = [("CONTAINER ID", "CONTAINER_ID")]

    @property
    def data(self):
        return self.containers
