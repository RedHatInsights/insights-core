'''
NetConsole - file ``/etc/sysconfig/netconsole``
===============================================

This parser reads the ``/etc/sysconfig/netconsole`` file.  It uses the
``SysconfigOptions`` parser class to convert the file into a dictionary of
options.

Sample data::

    # This is the configuration file for the netconsole service.  By starting
    # this service you allow a remote syslog daemon to record console output
    # from this system.

    # The local port number that the netconsole module will use
    LOCALPORT=6666


Examples:

    >>> config = shared[NetConsole]
    >>> 'LOCALPORT' in config.data
    True
    >>> 'DEV' in config # Direct access to options
    False

'''

from .. import parser, SysconfigOptions, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.netconsole)
class NetConsole(SysconfigOptions, LegacyItemAccess):
    '''
    Contents of the ``/etc/sysconfig/netconsole`` file.  Uses the
    ``SysconfigOptions`` shared parser class.
    '''
    pass
