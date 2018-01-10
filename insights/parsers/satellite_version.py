"""
Satellite6Version - file ``/usr/share/foreman/lib/satellite/version.rb``
========================================================================

Module for parsing the content of file ``version.rb`` or ``satellite_version``,
which is a simple file in foreman-debug or sosreport archives of Satellite 6.x.

Typical content of "satellite_version" is::

    COMMAND> cat /usr/share/foreman/lib/satellite/version.rb

    module Satellite
      VERSION = "6.1.3"
    end

Note:
    This module can only be used for Satellite 6.x

Examples:
    >>> sat6_ver = shared[SatelliteVersion]
    >>> sat6_ver.full
    "6.1.3"
    >>> sat6_ver.version
    "6.1.3"
    >>> sat6_ver.major
    6
    >>> sat6_ver.minor
    1
    >>> sat6_ver.release
    None

"""
from .. import parser, Parser
from ..parsers import ParseException
from insights.specs import Specs


@parser(Specs.satellite_version_rb)
class Satellite6Version(Parser):
    """ Class for parsing the content of ``satellite_version``."""

    def parse_content(self, content):
        # To keep compatible with combiner satellite_version
        self.full = self.release = None
        self.version = None
        for line in content:
            if line.strip().upper().startswith('VERSION'):
                self.full = line.split()[-1].strip('"')
                self.version = self.full
                break
        if self.version is None:
            raise ParseException('Cannot parse satellite version')

    @property
    def major(self):
        if self.version:
            return int(self.version.split(".")[0])

    @property
    def minor(self):
        if self.version:
            s = self.version.split(".")
            if len(s) > 1:
                return int(s[1])
