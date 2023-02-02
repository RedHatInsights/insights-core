"""
SystemdAnalyzeBlame - command ``systemd-analyze blame``
=======================================================

This module parses the output of command ``systemd-analyze blame``.
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


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
        SkipComponent: If content is not provided.
    """
    def parse_content(self, content):
        if not content:
            raise SkipComponent

        for c in content:
            cols = c.split()
            # Check to make sure that the first character of the first
            # entry is a number. This will hopefully exclude any errors
            # that are outputted in the file.
            if cols[0][0].isdigit():
                # The service should be the last column, so just
                # remove the last column from the list before looping.
                service = cols.pop()
                time = 0
                for x in cols:
                    # Convert each column to seconds, and add them up.
                    if x.endswith('y'):
                        # Pulled the 31557600 from systemd src.
                        time += int(x.strip('y')) * 31557600
                    elif x.endswith('month'):
                        # Pulled the 2629800 from systemd src.
                        time += int(x.strip('month')) * 2629800
                    elif x.endswith('w'):
                        time += int(x.strip('w')) * 7 * 24 * 60 ** 2
                    elif x.endswith('d'):
                        time += int(x.strip('d')) * 24 * 60 ** 2
                    elif x.endswith('h'):
                        time += int(x.strip('h')) * 60 ** 2
                    elif x.endswith('min'):
                        time += int(x.strip('min')) * 60
                    elif x.endswith('ms'):
                        time += float(x.strip('ms')) / 1000
                    elif x.endswith('s'):
                        time += float(x.strip('s'))

                self[service] = time
