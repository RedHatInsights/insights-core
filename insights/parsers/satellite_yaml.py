"""
SatelliteYaml - file ``/etc/foreman-installer/scenarios.d/satellite.yaml``
==========================================================================

Parse the file ``/etc/foreman-installer/scenarios.d/satellite.yaml``.

Sample input::

    ---
    :answer_file: /etc/foreman-installer/scenarios.d/satellite-answers.yaml
    :installer_dir: /usr/share/foreman-installer/katello
    :custom:
        :lock_package_versions: true
    :facts:
        tuning: default
        mongo_cache_size: 6.25

Examples:
    >>> ':facts' in SatelliteYaml
    True
    >>> SatelliteYaml[':facts']['tuning']
    'default'
"""

from insights.core.plugins import parser
from insights.core import YAMLParser
from insights.specs import Specs


@parser(Specs.satellite_yaml)
class SatelliteYaml(YAMLParser):
    pass
