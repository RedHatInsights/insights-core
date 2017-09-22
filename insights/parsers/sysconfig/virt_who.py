"""
SysconfigVirtWho - File ``/etc/sysconfig/virt-who``
===================================================

Parser for parsing file ``/etc/sysconfig/virt-who``.
"""
from ... import parser, SysconfigOptions


@parser('sysconfig_virt_who')
class SysconfigVirtWho(SysconfigOptions):
    """
    A parser for analyzing the ``virt-who`` service configuration file in the
    ``/etc/sysconfig`` directory.

    Sample Input::

        # Register ESX machines using vCenter
        # VIRTWHO_ESX=0
        # Register guests using RHEV-M
        VIRTWHO_RHEVM=1

        # Options for RHEV-M mode
        VIRTWHO_RHEVM_OWNER=

        TEST_OPT="A TEST"

    Examples:
        >>> vwho_syscfg = shared[SysconfigVirtWho]
        >>> vwho_syscfg['VIRTWHO_RHEVM']
        '1'
        >>> vwho_syscfg.get('VIRTWHO_RHEVM_OWNER')
        ''
        >>> vwho_syscfg.get('NO_SUCH_OPTION')
        None
        >>> 'NOSUCHOPTION' in vwho_syscfg
        False
        >>> vwho_syscfg.get('TEST_OPT')
        'A TEST'  # Quotes are stripped
    """
    pass
