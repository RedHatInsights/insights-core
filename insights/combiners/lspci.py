"""
LsPci - Commands ``lspci``
==========================

This combiner combines the following Parsers to a list.
- LsPci - the output of command ``lspci -k``
- LsPciVmmkn - the output of command ``lspci -vmmkn``
"""
from insights import combiner
from insights.parsers import keyword_search
from insights.parsers.lspci import LsPci, LsPciVmmkn


@combiner([LsPci, LsPciVmmkn])
class LsPci(list):
    """
    Combines the Parser LsPci of ``/sbin/lspci -k`` command and Parser
    LsPciVmmkn of ``/sbin/lspci -vmmkn`` command.

    Typical output of the ``lspci -k`` command is::

        00:00.0 Host bridge: Intel Corporation Haswell-ULT DRAM Controller (rev 09)
                Subsystem: Lenovo ThinkPad X240
                Kernel driver in use: hsw_uncore
        00:02.0 VGA compatible controller: Intel Corporation Haswell-ULT Integrated Graphics Controller (rev 09)
                Subsystem: Lenovo ThinkPad X240
                Kernel driver in use: i915
                Kernel modules: i915
        00:03.0 Audio device: Intel Corporation Haswell-ULT HD Audio Controller (rev 09)
                Subsystem: Lenovo ThinkPad X240
                Kernel driver in use: snd_hda_intel
                Kernel modules: snd_hda_intel
        00:16.0 Communication controller: Intel Corporation 8 Series HECI #0 (rev 04)
                Subsystem: Lenovo ThinkPad X240
                Kernel driver in use: mei_me
                Kernel modules: mei_me
        00:19.0 Ethernet controller: Intel Corporation Ethernet Connection I218-LM (rev 04)
                Subsystem: Lenovo ThinkPad X240
                Kernel driver in use: e1000e
                Kernel modules: e1000e
        00:1b.0 Audio device: Intel Corporation 8 Series HD Audio Controller (rev 04)
                Subsystem: Lenovo ThinkPad X240
                Kernel driver in use: snd_hda_intel
                Kernel modules: snd_hda_intel

    Typical output of the ``lspci -vmmkn`` command is::

        Slot:   00:00.0
        Class:  0600
        Vendor: 8086
        Device: 0a04
        SVendor:        17aa
        SDevice:        2214
        Rev:    09
        Driver: hsw_uncore

        Slot:   00:02.0
        Class:  0300
        Vendor: 8086
        Device: 0a16
        SVendor:        17aa
        SDevice:        2214
        Rev:    09
        Driver: i915
        Module: i915

        Slot:   00:03.0
        Class:  0403
        Vendor: 8086
        Device: 0a0c
        SVendor:        17aa
        SDevice:        2214
        Rev:    09
        Driver: snd_hda_intel
        Module: snd_hda_intel

        Slot:   00:16.0
        Class:  0780
        Vendor: 8086
        Device: 9c3a
        SVendor:        17aa
        SDevice:        2214
        Rev:    04
        Driver: mei_me
        Module: mei_me

        Slot:   00:19.0
        Class:  0200
        Vendor: 8086
        Device: 155a
        SVendor:        17aa
        SDevice:        2214
        Rev:    04
        Driver: e1000e
        Module: e1000e

        Slot:   00:1b.0
        Class:  0403
        Vendor: 8086
        Device: 9c20
        SVendor:        17aa
        SDevice:        2214
        Rev:    04
        Driver: snd_hda_intel
        Module: snd_hda_intel

    Examples:
        >>> type(lspci)
        <class 'insights.combiners.lspci.LsPci'>
        >>> sorted(lspci.pci_dev_list)
        ['00:00.0', '00:02.0', '00:03.0', '00:16.0', '00:19.0', '00:1b.0']
        >>> lspci.search(Dev_Details__contains='I218')[0]['Slot']
        '00:19.0'
    """
    def __init__(self, lspci_k, lspci_vmmkn):
        if lspci_vmmkn:
            for dev in lspci_vmmkn:
                if lspci_k and dev['Slot'] in lspci_k:
                    dev_k = lspci_k.data[dev['Slot']]
                    dev_k.pop('Kernel driver in use') if 'Kernel driver in use' in dev_k else None
                    dev_k.pop('Kernel modules') if 'Kernel modules' in dev_k else None
                    dev.update(dev_k)
                self.append(dev)
            self._pci_dev_list = lspci_vmmkn.pci_dev_list
        else:
            for dev in lspci_k.data.values():
                dev.update(Driver=dev.pop('Kernel driver in use')) if 'Kernel driver in use' in dev else None
                dev.update(Module=[i.strip() for i in dev.pop('Kernel modules').split(',')]) if 'Kernel modules' in dev else None
                self.append(dev)
            self._pci_dev_list = lspci_k.pci_dev_list

    @property
    def pci_dev_list(self):
        """
        The list of PCI devices.
        """
        return self._pci_dev_list

    def search(self, **kwargs):
        """
        Get the details of PCI devices by searching the table with kwargs.

        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details. If no search
        parameters are given, no rows are returned.

        It simplify the value of the column according to actual usage.

        Returns:
            list: A list of dictionaries of PCI devices that match the given
            search criteria.

        Examples:
            >>> len(lspci.search(Subsystem__startswith='Lenovo'))
            6
            >>> len(lspci.search(Subsystem__startswith='Lenovo', Dev_Details__startswith='Audio device'))
            2
            >>> lspci.search(Driver='snd_hda_intel', Dev_Details__contains='8') == [
            ... {'Slot': '00:1b.0', 'Class': '0403', 'Vendor': '8086',
            ...  'Device': '9c20', 'SVendor': '17aa', 'SDevice': '2214',
            ...  'Rev': '04', 'Driver': 'snd_hda_intel',
            ...  'Module': ['snd_hda_intel'], 'Subsystem': 'Lenovo ThinkPad X240',
            ...  'Dev_Details': 'Audio device: Intel Corporation 8 Series HD Audio Controller (rev 04)'}]
            True
        """
        return keyword_search(self, **kwargs)
