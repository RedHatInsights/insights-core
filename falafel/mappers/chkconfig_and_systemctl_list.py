"""
Enabled services - chkconfig and systemctl list-unit-files
==========================================================

This is a fairly simple mapper that handles the output of both ``chkconfig``
and ``systemctl list-unit-files``.  This returns the list of services that
had ``enabled`` or ``:on`` in the line.
"""

from .. import mapper


@mapper('systemctl_list-unit-files')
@mapper('chkconfig')
def enabled(context):
    """
    Returns the service name (the first word) for all services listed as
    ``enabled`` or ``on``.

    Sample input section from ``chkconfig``::

        abrt-oops       0:off   1:off   2:off   3:on    4:off   5:on    6:off
        abrtd           0:off   1:off   2:off   3:on    4:off   5:on    6:off
        acpid           0:off   1:off   2:on    3:on    4:on    5:on    6:off
        atd             0:off   1:off   2:off   3:on    4:on    5:on    6:off

    Sample input section from ``systemctl list-unit-files``::

        abrtd.service                               enabled
        accounts-daemon.service                     enabled
        alsa-restore.service                        static
        alsa-state.service                          static

    Examples:
        >>> services = shared[enabled]
        >>> 'abrtd' in services # RHEL 5-6
        True
        >>> 'abrtd.service' in services # RHEL 7
        True
    """
    return [line.split()[0] for line in context.content if "enabled" in line or ":on" in line]


def is_enabled(service, shared):
    """
    This is a convenience mapper that checks if ``service`` is in the
    ``enabled`` mapper within the ``shared`` shared mapper dictionary.
    """
    return enabled in shared and service in shared[enabled]
