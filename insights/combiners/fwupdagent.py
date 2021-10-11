"""
Fwupdagent
==========

Combiners for information from ``fwupdagent`` commands. The information is invalid in virtual
machines.
"""
from insights import SkipComponent
from insights.combiners.virt_what import VirtWhat
from insights.core.plugins import combiner
from insights.parsers.fwupdagent import FwupdagentDevices, FwupdagentSecurity


@combiner(FwupdagentDevices, VirtWhat)
class FwupdagentDevicesHW(object):
    """
    Store device information from ``fwupdagent`` command.

    Raises:
        SkipComponent: when system is a virtual machine.

    Attributes:
        devices (list): Device information.

    Examples:
        >>> type(devices)
        <class 'insights.combiners.fwupdagent.FwupdagentDevicesHW'>
        >>> len(devices.devices)
        2
    """
    def __init__(self, devices, virt):
        if virt.is_virtual:
            raise SkipComponent("Firmware information invalid in VM.")

        self.devices = devices.data["Devices"]


@combiner(FwupdagentSecurity, VirtWhat)
class FwupdagentSecurityHW(object):
    """
    Store security information from ``fwupdagent`` command.

    Raises:
        SkipComponent: when system is a virtual machine.

    Attributes:
        security (list): Security information.

    Examples:
        >>> type(security)
        <class 'insights.combiners.fwupdagent.FwupdagentSecurityHW'>
        >>> len(security.security)
        2
    """
    def __init__(self, security, virt):
        if virt.is_virtual:
            raise SkipComponent("Firmware information invalid in VM.")

        self.security = security.data["HostSecurityAttributes"]
