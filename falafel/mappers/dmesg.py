"""
DMesgLineList - command ``dmesg``
=================================

DMesgLineList is a simple mapper that is based on the ``LogFileOutput``
mapper class.

It provides one additional helper method:

* ``has_startswith`` - does the log contain any line that starts with the
  given string?

Sample input::

[    0.000000] Linux version 3.10.0-327.36.3.el7.x86_64 (mockbuild@x86-037.build.eng.bos.redhat.com) (gcc version 4.8.5 20150623 (Red Hat 4.8.5-4) (GCC) ) #1 SMP Thu Oct 20 04:56:07 EDT 2016
[    0.000000] Command line: BOOT_IMAGE=/vmlinuz-3.10.0-327.36.3.el7.x86_64 root=/dev/RHEL7CSB/Root ro rd.lvm.lv=RHEL7CSB/Root rd.luks.uuid=luks-96c66446-77fd-4431-9508-f6912bd84194 crashkernel=auto vconsole.keymap=us rd.lvm.lv=RHEL7CSB/Swap vconsole.font=latarcyrheb-sun16 rhgb quiet LANG=en_GB.utf8
[    0.000000] PID hash table entries: 4096 (order: 3, 32768 bytes)
[    0.000000] x86/fpu: xstate_offset[2]: 0240, xstate_sizes[2]: 0100
[    0.000000] xsave: enabled xstate_bv 0x7, cntxt size 0x340
[    0.000000] AGP: Checking aperture...
[    0.000000] AGP: No AGP bridge found
[    0.000000] Memory: 15918544k/17274880k available (6444k kernel code, 820588k absent, 535748k reserved, 4265k data, 1632k init)
[    0.000000] SLUB: HWalign=64, Order=0-3, MinObjects=0, CPUs=8, Nodes=1
[    0.000000] Hierarchical RCU implementation.

Examples:

    >>> dmesg = shared[DmesgLineList]
    >>> 'BOOT_IMAGE' in dmesg
    True
    >>> dmesg.get('AGP')
    ['[    0.000000] AGP: Checking aperture...', '[    0.000000] AGP: No AGP bridge found']

"""

from .. import LogFileOutput, mapper


@mapper('dmesg')
class DmesgLineList(LogFileOutput):
    """
    Class for reading output of ``dmesg`` using the LogFileOutput mapper class.
    """
    def has_startswith(self, prefix):
        """
        Parameters:
            prefix (str): The prefix of the line to look for.

        Returns:
            (bool): Does any line start with the given prefix?

        Notes:
            Does not ignore the time stamp of the line - if the dmesg output
            contains timestamps then these are considered to start the line.
        """
        return any(line.startswith(prefix) for line in self.lines)


@mapper('dmesg')
def dmesg(context):
    """
    Returns an object of DmesgLineList
    """
    return DmesgLineList(context)


@mapper('vmcore-dmesg')
def vmcore_dmesg(context):
    """
    Returns an object of DmesgLineList
    """
    return DmesgLineList(context)
