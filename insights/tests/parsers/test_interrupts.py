import pytest
from insights.parsers import ParseException
from insights.parsers.interrupts import Interrupts
from insights.tests import context_wrap

INT_MULTI = """
           CPU0       CPU1       CPU2       CPU3       CPU4       CPU5       CPU6       CPU7
  0:         37          0          0          0          0          0          0          0  IR-IO-APIC   2-edge      timer
  1:          3          2          1          0          3          3          0          3  IR-IO-APIC   1-edge      i8042
  8:          0          1          0          0          0          0          0          0  IR-IO-APIC   8-edge      rtc0
  9:      11107       2316       4040       1356       1324       1006        548        537  IR-IO-APIC   9-fasteoi   acpi
 12:         44         13          8         10          7         16        320         93  IR-IO-APIC  12-edge      i8042
 16:          4          2          2          8          0          6          7          0  IR-IO-APIC  16-fasteoi   ehci_hcd:usb1, mmc0
 18:          0          0          0          0          0          0          0          0  IR-IO-APIC  18-fasteoi   i801_smbus
 23:          6          6          4          4          0         10          3          0  IR-IO-APIC  23-fasteoi   ehci_hcd:usb2
 24:          0          0          0          0          0          0          0          0  DMAR-MSI   0-edge      dmar0
 25:          0          0          0          0          0          0          0          0  DMAR-MSI   1-edge      dmar1
 27:     242965     155333      52536      47894      35496      32961      27934      96634  IR-PCI-MSI 512000-edge      ahci[0000:00:1f.2]
 28:    2524672     433481     227987     212406     162014     175712     150609     151638  IR-PCI-MSI 327680-edge      xhci_hcd
 29:     974462     273360      84814     115282      66423      72322      48783      56791  IR-PCI-MSI 409600-edge      enp0s25
 30:        100         22         12         19         16          6         10          5  IR-PCI-MSI 524288-edge
 31:     321958      46760      42215      27668      34390      22665      29484      20514  IR-PCI-MSI 32768-edge      i915
 32:          7          1          2          7          0          3          0          6  IR-PCI-MSI 360448-edge      mei_me
 33:     193890      10271      22883       6823       3023       3918       2610       3798  IR-PCI-MSI 1572864-edge      iwlwifi
 34:        123         95         81         18         61          9         23         38  IR-PCI-MSI 442368-edge      snd_hda_intel:card2
 35:        460        102        375        269        123         48         38         23  IR-PCI-MSI 49152-edge      snd_hda_intel:card1
NMI:        210         92        179         96        177          0          0          0   Non-maskable interrupts
LOC:    7561411    2488524    6527767    2448192    6244091    2942086    6199519    2508884   Local timer interrupts
SPU:          0          0          0          0          0          0          0          0   Spurious interrupts
PMI:        210         92        179         96        177          0          0          0   Performance monitoring interrupts
IWI:          2          0          0          0          0          1          0          0   IRQ work interrupts
RTR:          0          0          0          0          0          0          0          0   APIC ICR read retries
RES:     181183     110341     106958      66026      92237      61031      72582      55959   Rescheduling interrupts
CAL:       2946       2842       2954       2995       2098       2835       2895       3016   Function call interrupts
TLB:     362051     255750     355120     266627     354757     264554     360694     266051   TLB shootdowns
TRM:          0          0          0          0          0          0          0          0   Thermal event interrupts
THR:          0          0          0          0          0          0          0          0   Threshold APIC interrupts
DFR:          0          0          0          0          0          0          0          0   Deferred Error APIC interrupts
MCE:          0          0          0          0          0          0          0          0   Machine check exceptions
MCP:        381        381        381        381        381        381        381        381   Machine check polls
ERR:          0
MIS:          0
PIN:          0          0          0          0          0          0          0          0   Posted-interrupt notification event
PIW:          0          0          0          0          0          0          0          0   Posted-interrupt wakeup event
""".strip()

INT_SINGLE = """
           CPU0
  0:         45   IO-APIC-edge      timer
  1:          3   IO-APIC-edge      i8042
  6:          3   IO-APIC-edge      floppy
  7:          0   IO-APIC-edge      parport0
  8:          1   IO-APIC-edge      rtc0
  9:          0   IO-APIC-fasteoi   acpi
HYP:          0   Hypervisor callback interrupts
ERR:          0
MIS:          0
""".strip()

INT_INVALID_1 = """
  0:         45   IO-APIC-edge      timer
  1:          3   IO-APIC-edge      i8042
  6:          3   IO-APIC-edge      floppy
""".strip()

INT_INVALID_2 = """


""".strip()

INT_NO_INTERRUPTS = """
           CPU0
"""


def test_interrupts():
    all_ints = Interrupts(context_wrap(INT_MULTI))
    assert len(all_ints.data) == 37
    assert all_ints.num_cpus == 8
    assert all_ints.get("i8042") == [all_ints.data[1], all_ints.data[4]]
    assert len(all_ints.get("IR-PCI-MSI")) == 9
    for one_int in all_ints:
        if one_int['irq'] == "NMI:":
            assert one_int['counts'] == ["210", "92", "179", "96", "177", "0", "0", "0"]
            assert one_int['type_device'] == "Non-maskable interrupts"
    all_ints = Interrupts(context_wrap(INT_SINGLE))
    assert len(all_ints.data) == 9
    for one_int in all_ints:
        assert len(one_int['counts']) == 1
    assert 'type_device' in all_ints.data[6]
    assert 'type_device' not in all_ints.data[7]
    assert 'type_device' not in all_ints.data[8]

    with pytest.raises(ParseException):
        Interrupts(context_wrap(INT_INVALID_1))

    with pytest.raises(ParseException):
        Interrupts(context_wrap(INT_INVALID_2))

    with pytest.raises(ParseException):
        Interrupts(context_wrap(INT_NO_INTERRUPTS))
