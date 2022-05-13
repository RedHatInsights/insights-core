from insights.parsers.sysconfig import IrqbalanceSysconfig
from insights.tests import context_wrap

IRQBALANCE_SYSCONF_TEST = """
# irqbalance is a daemon process that distributes interrupts across
# CPUS on SMP systems. The default is to rebalance once every 10
# seconds. This is the environment file that is specified to systemd via the
# EnvironmentFile key in the service unit file (or via whatever method the init
# system you're using has.
#
# ONESHOT=yes
# after starting, wait for a minute, then look at the interrupt
# load and balance it once; after balancing exit and do not change
# it again.
#IRQBALANCE_ONESHOT=yes

#
# IRQBALANCE_BANNED_CPUS
# 64 bit bitmask which allows you to indicate which cpu's should
# be skipped when reblancing irqs. Cpu numbers which have their
# corresponding bits set to one in this mask will not have any
# irq's assigned to them on rebalance
#
IRQBALANCE_BANNED_CPUS=f8

#
# IRQBALANCE_ARGS
# append any args here to the irqbalance daemon as documented in the man page
#
IRQBALANCE_ARGS="-d"
""".strip()


def test_irqbalance_conf():
    ret = IrqbalanceSysconfig(context_wrap(IRQBALANCE_SYSCONF_TEST))
    assert ret['IRQBALANCE_BANNED_CPUS'] == 'f8'
    assert 'IRQBALANCE_ARGS' in ret
    assert ret.get('IRQBALANCE_ARGS') == '-d'
    assert 'IRQBALANCE_ONESHOT' not in ret
