import doctest
from insights.parsers.bond_dynamic_lb import BondDynamicLB
from insights.parsers import bond_dynamic_lb
from insights.tests import context_wrap


CONTEXT_PATH = "/sys/class/net/bond0/bonding/tlb_dynamic_lb"
CONTEXT_PATH_1 = "/sys/class/net/bond1/bonding/tlb_dynamic_lb"
CONTEXT_PATH_2 = "/sys/class/net/bond2/bonding/tlb_dynamic_lb"

BOND_LD_BALANCE = """
0
""".strip()

BOND_LD_BALANCE_1 = """
1
""".strip()

BOND_LD_BALANCE_2 = """
off
""".strip()

BOND_LD_BALANCE_NO = """

""".strip()


def test_netstat_doc_examples():
    env = {
        'tlb_bond': BondDynamicLB(context_wrap(BOND_LD_BALANCE_1, CONTEXT_PATH)),
    }
    failed, total = doctest.testmod(bond_dynamic_lb, globs=env)
    assert failed == 0


def test_bond_dynamic_lb_class():

    tlb_bond = BondDynamicLB(context_wrap(BOND_LD_BALANCE, CONTEXT_PATH))
    assert tlb_bond.bond_name == 'bond0'
    assert tlb_bond.dynamic_lb_status == 0

    tlb_bond = BondDynamicLB(context_wrap(BOND_LD_BALANCE_1, CONTEXT_PATH_1))
    assert tlb_bond.bond_name == 'bond1'
    assert tlb_bond.dynamic_lb_status == 1

    tlb_bond = BondDynamicLB(context_wrap(BOND_LD_BALANCE_2, CONTEXT_PATH_2))
    assert tlb_bond.bond_name == 'bond2'
    assert tlb_bond.dynamic_lb_status is None

    tlb_bond = BondDynamicLB(context_wrap(BOND_LD_BALANCE_NO, CONTEXT_PATH_2))
    assert tlb_bond.bond_name == 'bond2'
    assert tlb_bond.dynamic_lb_status is None
