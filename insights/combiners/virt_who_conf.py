"""
virt-who configuration
======================
virt-who can accept configuration from several sources listed below in order
of precedence.

Configuration sources of virt-who::

    1. command line             # Ignored
    2. environment variables    # Ignored
    3. /etc/sysconfig/virt-who  # VirtWhoSysconfig
    4. /etc/virt-who.d/*.conf   # VirtWhoConf
    5. /etc/virt-who.conf       # VirtWhoConf

"""

from insights.core.plugins import combiner
from insights.parsers.sysconfig import VirtWhoSysconfig
from insights.parsers.virt_who_conf import VirtWhoConf


@combiner(VirtWhoSysconfig, VirtWhoConf)
class AllVirtWhoConf(object):
    """
    Combiner for accessing part of valid ``virt-who`` configurations

    Sample content of ``/etc/sysconfig/virt-who``::

        # Start virt-who on background, perform doublefork and monitor for virtual guest
        # events (if possible). It is NOT recommended to turn off this option for
        # starting virt-who as service.
        VIRTWHO_BACKGROUND=1
        # Enable debugging output.
        VIRTWHO_DEBUG=1
        # Send the list of guest IDs and exit immediately.
        VIRTWHO_ONE_SHOT=0
        # Acquire and send list of virtual guest each N seconds, 0 means default
        # configuration.
        VIRTWHO_INTERVAL=3600
        # Virt-who subscription manager backend. Enable only one option from the following:
        # Report to Subscription Asset Manager (SAM) or the Red Hat Customer Portal
        # Report to Sattellite version 6
        VIRTWHO_SATELLITE6=1


    Sample content of ``/etc/virt-who.conf``::

        [global]
        debug=False
        oneshot=True
        [defaults]
        owner=test

    Sample content of ``/etc/virt-who.d/satellite_esx.conf``::

        [esx_satellite]
        type=esx
        server=10.72.32.209
        owner=Satellite
        env=Satellite

    Examples:
        >>> shared = {VirtWhoSysconfig: vw_sys, VirtWhoConf: [vw_conf, vwd_conf]}
        >>> all_vw_conf = AllVirtWhoConf(None, shared)
        >>> all_vw_conf.background
        True
        >>> all_vw_conf.oneshot
        False  # `/etc/sysconfig/virt-who` has high priority
        >>> all_vw_conf.interval
        3600
        >>> all_vw_conf.sm_type
        'sat6'
        >>> all_vw_conf.hypervisors
        [{'name': 'esx_satellite', 'server': '10.72.32.209',
          'owner': 'Satellite', 'env': 'Satellite', type: 'esx'}]
        >>> all_vw_conf.hypervisor_types
        ['esx']


    Attributes:
        background(boolean): is ``virt-who`` running as a service
        oneshot(boolean): is ``virt-who`` running in ``one-shot`` mode or not
        interval(int): how often to check connected hypervisors for changes (seconds)
        sm_type(str): what subscription manager will ``virt-who`` report to
        hypervisors(list): list of dict of each connected hypervisors
        hypervisor_types(list): list of the connected hypervisors' type
    """

    def __init__(self, svw, vwc):
        self.background = False
        self.oneshot = True
        self.interval = 3600
        self.sm_type = 'cp'  # report to Red Hat Customer Portal by default
        self.hypervisors = []
        self.hypervisor_types = []

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

        self.background = ('1' == svw.get('VIRTWHO_BACKGROUND'))
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
