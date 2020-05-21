"""
SystemdAnalyzeBlame - command ``systemd-analyze blame``
=======================================================

This module parses the output of command ``systemd-analyze blame``.
"""
from insights.specs import Specs
from insights import CommandParser, parser
from insights.parsers import SkipException


@parser(Specs.systemd_analyze_blame)
class SystemdAnalyzeBlame(CommandParser, dict):
    """Parse the output of ``systemd-analyze blame`` as ``dict``. The time to
    initialize is converted into seconds.

    Typical output::

        33.080s cloud-init-local.service
        32.423s unbound-anchor.service
         2.773s kdump.service
         1.699s dnf-makecache.service
         1.304s cloud-init.service
         1.073s initrd-switch-root.service
          939ms cloud-config.service
          872ms tuned.service
          770ms cloud-final.service

    Examples:

        >>> 'cloud-init-local.service' in output
        True
        >>> output.get('cloud-init.service', 0)
        1.304

    Returns:
        (dict): With unit-name & time as key-value pair.
                Ex::

                    {'cloud-config.service': 0.939,
                     'cloud-final.service': 0.77,
                     'cloud-init-local.service': 33.08,
                     'cloud-init.service': 1.304,
                     'dnf-makecache.service': 1.699,
                     'initrd-switch-root.service': 1.073,
                     'kdump.service': 2.773,
                     'tuned.service': 0.872,
                     'unbound-anchor.service': 32.423}

    Raises:
        SkipException: If content is not provided.
    """
    def parse_content(self, content):
        if not content:
            raise SkipException

        for c in content:
            time, service = c.split()
            if time.endswith('ms'):
                _time = round(float(time.strip('ms')) / 1000, 5)
            else:
                _time = round(float(time.strip('ms')), 5)

            self[service] = _time
