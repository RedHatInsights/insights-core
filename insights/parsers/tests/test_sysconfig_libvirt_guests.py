from insights.parsers.sysconfig import LibvirtGuestsSysconfig
from insights.tests import context_wrap

SYSCONFIG_LIBVIRT_GUESTS = """
# URIs to check for running guests
# example: URIS='default xen:/// vbox+tcp://host/system lxc:///'
#URIS=default

# action taken on host boot
# - start   all guests which were running on shutdown are started on boot
#           regardless on their autostart settings
# - ignore  libvirt-guests init script won't start any guest on boot, however,
#           guests marked as autostart will still be automatically started by
#           libvirtd
ON_BOOT=ignore

# Number of seconds to wait between each guest start. Set to 0 to allow
# parallel startup.
#START_DELAY=0

# action taken on host shutdown
# - suspend   all running guests are suspended using virsh managedsave
# - shutdown  all running guests are asked to shutdown. Please be careful with
#             this settings since there is no way to distinguish between a
#             guest which is stuck or ignores shutdown requests and a guest
#             which just needs a long time to shutdown. When setting
#             ON_SHUTDOWN=shutdown, you must also set SHUTDOWN_TIMEOUT to a
#             value suitable for your guests.
#ON_SHUTDOWN=suspend

# If set to non-zero, shutdown will suspend guests concurrently. Number of
# guests on shutdown at any time will not exceed number set in this variable.
#PARALLEL_SHUTDOWN=0

# Number of seconds we're willing to wait for a guest to shut down. If parallel
# shutdown is enabled, this timeout applies as a timeout for shutting down all
# guests on a single URI defined in the variable URIS. If this is 0, then there
# is no time out (use with caution, as guests might not respond to a shutdown
# request). The default value is 300 seconds (5 minutes).
#SHUTDOWN_TIMEOUT=300

# If non-zero, try to bypass the file system cache when saving and
# restoring guests, even though this may give slower operation for
# some file systems.
#BYPASS_CACHE=0

# If non-zero, try to sync guest time on domain resume. Be aware, that
# this requires guest agent with support for time synchronization
# running in the guest. For instance, qemu-ga doesn't support guest time
# synchronization on Windows guests, but Linux ones. By default, this
# functionality is turned off.
#SYNC_TIME=1
""".strip()


def test_sysconfig_libvirt_guests():
    libvirt_guests_sysconfig = LibvirtGuestsSysconfig(context_wrap(SYSCONFIG_LIBVIRT_GUESTS))
    assert 'ON_BOOT' in libvirt_guests_sysconfig
    assert libvirt_guests_sysconfig.get('ON_BOOT') == 'ignore'
    assert libvirt_guests_sysconfig.get('SYNC_TIME') is None
