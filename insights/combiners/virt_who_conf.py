"""
virt-who configuration
======================
virt-who can accept configuration from several sources listed below in order
of precedence.

Configuration sources of virt-who::

    1. command line             # Ignored
    2. environment variables    # Ignored
    3. /etc/sysconfig/virt-who  # SysconfigVirtWho
    4. /etc/virt-who.d/*.conf  # VirtWhoConf
    5. /etc/virt-who.conf       # VirtWhoConf

"""

from insights.core.plugins import combiner
from insights.parsers.sysconfig.virt_who import SysconfigVirtWho
from insights.parsers.virt_who_conf import VirtWhoConf


@combiner(requires=[SysconfigVirtWho, VirtWhoConf])
class AllVirtWhoConf(object):
    """
    Combiner for accessing part of valid ``virt-who`` configurations

    Attributes:
        oneshot(boolean): is ``virt-who`` running in ``one-shot`` mode or not
        interval(int): how often to check connected hypervisors for changes (seconds)
        sm_type(str): what subscription manager will ``virt-who`` report to
        hypervisors(list): list of dict of each connected hypervisors
        hypervisor_types(list): list of the connected hypervisors' type
    """

    def __init__(self, shared):
        self.oneshot = True
        self.interval = 3600
        self.sm_type = 'cp'  # report to Red Hat Customer Portal by default
        self.hypervisors = []
        self.hypervisor_types = []

        vwc = shared[VirtWhoConf]
        svw = shared[SysconfigVirtWho]

        # Check VirtWhoConf at first
        types = set()
        for c in vwc:
            if c.has_option('global', 'oneshot'):
                self.oneshot = c.getboolean('global', 'oneshot')
            if c.has_option('global', 'interval'):
                self.interval = c.getint('global', 'interval')
            for section in c.sections():
                # Check Hypervisor back-ends
                if c.has_option(section, 'type'):
                    hyper = {'name': section}
                    hyper.update(c.items(section))
                    types.add(hyper['type'])
                    self.hypervisors.append(hyper)
        self.hypervisor_types = list(types)

        ost = svw.get('VIRTWHO_ONE_SHOT')
        self.oneshot = (ost == '1') if ost else self.oneshot
        itv = svw.get('VIRTWHO_INTERVAL')
        self.interval = int(itv) if itv and itv.isdigit() else self.interval

        # Check which subscription manager will report to
        if svw.get('VIRTWHO_SAM') == '1':
            self.sm_type = 'sam'  # report to SAM
        elif svw.get('VIRTWHO_SATELLITE6') == '1':
            self.sm_type = 'sat6'  # report to Satellite 6
        elif svw.get('VIRTWHO_SATELLITE5') == '1' or svw.get('VIRTWHO_SATELLITE') == '1':
            self.sm_type = 'sat5'  # report to Satellite 5
