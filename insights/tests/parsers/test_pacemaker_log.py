from insights.parsers.pacemaker_log import PacemakerLog
from insights.tests import context_wrap

from datetime import datetime

PACEMAKER_LOG = """
Aug 21 12:58:32 [11661] example.redhat.com       crmd:     info: crm_timer_popped: 	PEngine Recheck Timer (I_PE_CALC) just popped (900000ms)
Aug 21 12:58:32 [11661] example.redhat.com       crmd:   notice: do_state_transition: 	State transition S_IDLE -> S_POLICY_ENGINE [ input=I_PE_CALC cause=C_TIMER_POPPED origin=crm_timer_popped ]
Aug 21 12:58:32 [11661] example.redhat.com       crmd:     info: do_state_transition: 	Progressed to state S_POLICY_ENGINE after C_TIMER_POPPED
Aug 21 12:58:32 [11656] example.redhat.com        cib:     info: cib_process_request: 	Completed cib_query operation for section 'all': OK (rc=0, origin=local/crmd/262, version=0.10.3)
Aug 21 12:58:32 [11660] example.redhat.com    pengine:   notice: unpack_config: 	On loss of CCM Quorum: Ignore
Aug 21 12:58:32 [11660] example.redhat.com    pengine:     info: determine_online_status: 	Node d-d9ckmw1 is online
Aug 21 12:58:32 [11660] example.redhat.com    pengine:     info: determine_online_status: 	Node d-gqynnw1 is online
Aug 21 12:58:32 [11660] example.redhat.com    pengine:   notice: stage6: 	Delaying fencing operations until there are resources to manage
Aug 21 12:58:32 [11660] example.redhat.com    pengine:   notice: process_pe_message: 	Calculated Transition 125: /var/lib/pacemaker/pengine/pe-input-14.bz2
Aug 21 12:58:33 [11661] example.redhat.com       crmd:     info: do_state_transition: 	State transition S_POLICY_ENGINE -> S_TRANSITION_ENGINE [ input=I_PE_SUCCESS
"""


def test_pacemaker_log():
    pacemaker = PacemakerLog(context_wrap(PACEMAKER_LOG))
    assert "Progressed to state S_POLICY_ENGINE after C_TIMER_POPPED" in pacemaker
    assert len(list(pacemaker.get_after(datetime(2017, 8, 21, 12, 58, 30)))) == 10
