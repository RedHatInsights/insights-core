import pytest
from insights.components.openstack import IsOpenStackCompute
from insights.parsers.ps import PsAuxcww
from insights.tests import context_wrap
from insights.core.dr import SkipComponent


PS_MULTIPATHD = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START    TIME  COMMAND
root         9  0.0  0.0      0     0 ?        S    Mar24   0:05  multipathd
""".strip()


PS_OSP_COMPUTE = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START    TIME  COMMAND
nova     24928  0.1  1.1 390180 89368 ?        Ss   11:30   0:09  nova-compute
root         9  0.0  0.0      0     0 ?        S    Mar24   0:05  multipathd
""".strip()

PS_OSP_DIRECTOR = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START    TIME  COMMAND
nova     24928  0.1  1.1 390180 89368 ?        Ss   11:30   0:09  nova-compute
nova     24928  0.1  1.1 390180 89368 ?        Ss   11:30   0:09  nova-conductor
root         9  0.0  0.0      0     0 ?        S    Mar24   0:05  multipathd
""".strip()

PS_OSP_CONTROLLER = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START    TIME  COMMAND
nova     24928  0.1  1.1 390180 89368 ?        Ss   11:30   0:09  nova-conductor
root         9  0.0  0.0      0     0 ?        S    Mar24   0:05  multipathd
""".strip()


def test_generic_process():
    """The ``psauxcww`` does not have ``nova-compute`` process."""
    ps = PsAuxcww(context_wrap(PS_MULTIPATHD))
    with pytest.raises(SkipComponent) as e:
        IsOpenStackCompute(ps)
    assert "Not OpenStack Compute node" in str(e)


def test_compute_node():
    ps = PsAuxcww(context_wrap(PS_OSP_COMPUTE))
    result = IsOpenStackCompute(ps)
    assert isinstance(result, IsOpenStackCompute)


def test_controller_node():
    ps = PsAuxcww(context_wrap(PS_OSP_CONTROLLER))
    with pytest.raises(SkipComponent) as e:
        IsOpenStackCompute(ps)
    assert "Not OpenStack Compute node" in str(e)


def test_director_node():
    # A director act as an Compute as well as a Controller node.
    ps = PsAuxcww(context_wrap(PS_OSP_DIRECTOR))
    result = IsOpenStackCompute(ps)
    assert isinstance(result, IsOpenStackCompute)
