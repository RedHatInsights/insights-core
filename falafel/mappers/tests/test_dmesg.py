from falafel.mappers import dmesg
from falafel.tests import context_wrap

MSGINFO = """
lo: Dropping TSO features since no CSUM feature.
bnx2 0000:0b:00.0: irq 86 for MSI/MSI-X
bnx2 0000:0b:00.0: eth0: using MSIX
(null): Dropping TSO features since no CSUM feature.
(null): Dropping TSO6 features since no CSUM feature.
bonding: bond0: enslaving eth0 as a backup interface with a down link.
HP HPSA Driver (v 3.4.4-1-RH2)
  alloc irq_desc for 34 on node 0
  alloc kstat_irqs on node 0
scsi4 : hpsa
hpsa 0000:02:00.0: RAID              device c4b3t0l0 added.
hpsa 0000:02:00.0: Direct-Access     device c4b0t0l0 added.
scsi 4:3:0:0: RAID              HP       P420i            3.04 PQ: 0 ANSI: 5
scsi 4:0:0:0: Direct-Access     HP       LOGICAL VOLUME   3.04 PQ: 0 ANSI: 5
HP HPSA Driver (v 3.4.4-1-RH2)
[    8.687252] HP HPSA Driver (v 3.4.4-1-RH2) 2.5.0
lo: Dropping TSO features since no CSUM feature duplicated.
""".strip()


def test_dmesg():
    dmesg_info = dmesg.dmesg(context_wrap(MSGINFO))
    assert dmesg_info.get("HPSA") == ['HP HPSA Driver (v 3.4.4-1-RH2)', 'HP HPSA Driver (v 3.4.4-1-RH2)', '[    8.687252] HP HPSA Driver (v 3.4.4-1-RH2) 2.5.0']
    assert len(dmesg_info.get("lo:")) == 2
    assert dmesg_info.__contains__("Dropping")
    assert dmesg_info.has_startswith("bonding:")
