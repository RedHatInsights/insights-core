"""
CoroSyncConfig - file ``/etc/sysconfig/corosync``
=================================================

This mapper reads the ``/etc/sysconfig/corosync`` file.  It uses the
``SysconfigOptions`` mapper class to convert the file into a dictionary of
options.  It also provides the ``options`` property as a helper to retrieve
the ``COROSYNC_OPTIONS`` variable.

Sample data::

    # Corosync init script configuration file

    # COROSYNC_INIT_TIMEOUT specifies number of seconds to wait for corosync
    # initialization (default is one minute).
    COROSYNC_INIT_TIMEOUT=60

    # COROSYNC_OPTIONS specifies options passed to corosync command
    # (default is no options).
    # See "man corosync" for detailed descriptions of the options.
    COROSYNC_OPTIONS=""

Examples:

    >>> csconfig = shared[CoroSyncConfig]
    >>> 'COROSYNC_OPTIONS' in csconfig.data
    True
    >>> csconfig.options
    ''

"""

from .. import SysconfigOptions, mapper


@mapper("corosync")
class CoroSyncConfig(SysconfigOptions):
    """
    Parse the ``/etc/sysconfig/corosync`` file using the SysconfigOptions
    mapper class.
    """

    @property
    def options(self):
        """ (str): The value of the ``COROSYNC_OPTIONS`` variable."""
        return self.data.get('COROSYNC_OPTIONS', '')
