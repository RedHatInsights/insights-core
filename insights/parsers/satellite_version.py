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

.. warning::
    This module only works for Satellite 6.0.x and 6.1.x
    Please use the combiner
    :class:`insights.combiners.satellite_version.SatelliteVersion` class to
    cover all versions.

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
from insights.core import Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.satellite_version_rb)
class Satellite6Version(Parser):
    """

    Class for parsing the content of ``satellite_version``.
    """

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
        ver_sp = self.version.split(".")
        self.major = int(ver_sp[0])
        self.minor = int(ver_sp[1]) if len(ver_sp) > 1 else None
