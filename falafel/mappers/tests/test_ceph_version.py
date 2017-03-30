from falafel.mappers.ceph_version import CephVersion
from falafel.mappers.ceph_version import CephVersionError
from falafel.tests import context_wrap
import pytest

CV1 = "ceph version 0.94.9-9.el7cp (b83334e01379f267fb2f9ce729d74a0a8fa1e92c)"
CV2 = ""
CV3 = "error"
CV4 = "ceph version 10.2.2-38.el7cp (b83334e01379f267fb2f9ce729d74a0a8fa1e92c)"
CV5 = "ceph version 1"
CV6 = "ceph version 1.2.3-5"


def test_ceph_version():
    with pytest.raises(CephVersionError) as error_context2:
        CephVersion(context_wrap(CV2))
    with pytest.raises(CephVersionError) as error_context3:
        CephVersion(context_wrap(CV3))
    with pytest.raises(CephVersionError) as error_context5:
        CephVersion(context_wrap(CV5))
    with pytest.raises(CephVersionError) as error_context6:
        CephVersion(context_wrap(CV6))
    assert 'Empty Ceph Version Line' in str(error_context2)
    assert 'Wrong Format Ceph Version' in str(error_context3)
    assert 'Wrong Format Ceph Version' in str(error_context5)
    assert 'No Mapping Release Version' in str(error_context6)
    ceph_version1 = CephVersion(context_wrap(CV1))
    ceph_version4 = CephVersion(context_wrap(CV4))
    assert ceph_version1.release == "1.3.3"
    assert ceph_version1.major == '1.3'
    assert ceph_version1.minor == "3"
    assert ceph_version4.release == "2.0"
    assert ceph_version4.major == '2'
    assert ceph_version4.minor == "0"
