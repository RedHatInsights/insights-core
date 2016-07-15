from falafel.core.context import OSP
from falafel.mappers.osp_metadata import osp_metadata_role
from falafel.tests import context_wrap

UNAME1 = "Linux ceehadoop1.gsslab.rdu2.redhat.com 2.6.32-504.el6.x86_64 #1 SMP Tue Sep 16 01:56:35 EDT 2014 x86_64 x86_64 x86_64 GNU/Linux"

osp_c = OSP()
osp_c.role = "Controller"

osp_d = OSP()
osp_d.role = "Director"

osp_n = OSP()
osp_n.role = "Compute"


def test_osp_metadata_role():
    context = context_wrap(UNAME1, osp=osp_c)
    i_role = osp_metadata_role(context)
    assert i_role.isController()

    context = context_wrap(UNAME1, osp=osp_d)
    i_role = osp_metadata_role(context)
    assert i_role.isDirector()

    context = context_wrap(UNAME1, osp=osp_n)
    i_role = osp_metadata_role(context)
    assert i_role.isCompute()

    context = context_wrap(UNAME1)
    i_role = osp_metadata_role(context)
    assert i_role is None
