from insights.parsers.ceph_version import CephVersion
from insights.tests import context_wrap
from insights.parsers import SkipException
import pytest

CV1 = "ceph version 0.94.9-9.el7cp (b83334e01379f267fb2f9ce729d74a0a8fa1e92c)"
CV2 = ""
CV3 = "error"
CV4 = "ceph version 10.2.2-38.el7cp (b83334e01379f267fb2f9ce729d74a0a8fa1e92c)"
CV5 = "ceph version 1"
CV6 = "ceph version 1.2.3-5"
CV_5 = "ceph version 10.2.5-37.el7cp (c461ee19ecbc0c5c330aca20f7392c9a00730367)"
CV7 = "ceph version 10.2.5-37.el7cp (033f137cde8573cfc5a4662b4ed6a63b8a8d1464)"
CV8 = "ceph version 10.2.7-27.el7cp (abcd137cde8573cfc5a4662b4ed6a63b8a8kadf1)"
CV9 = "ceph version 12.2.5-59.el7cp (d4b9f17b56b3348566926849313084dd6efc2ca2)"
CV10 = "ceph version 12.2.8-128.el7cp (030358773c5213a14c1444a5147258672b2dc15f)"
CV10_1 = "ceph version 12.2.12-74.el7cp (030358773c5213a14c1444a5147258672b2dc15f)"
CV_els = "ceph version 10.2.10-51.el7cp (030358773c5213a14c1444a5147258672b2dc15f)"


def test_ceph_version():
    with pytest.raises(SkipException) as error_context2:
        CephVersion(context_wrap(CV2))
    assert 'Empty Ceph Version Line' in str(error_context2)
    with pytest.raises(SkipException) as error_context3:
        CephVersion(context_wrap(CV3))
    assert 'Wrong Format Ceph Version' in str(error_context3)
    with pytest.raises(SkipException) as error_context5:
        CephVersion(context_wrap(CV5))
    assert 'Wrong Format Ceph Version' in str(error_context5)
    with pytest.raises(SkipException) as error_context6:
        CephVersion(context_wrap(CV6))
    assert 'No Mapping Release Version' in str(error_context6)

    ceph_version1 = CephVersion(context_wrap(CV1))
    assert ceph_version1.version == "1.3.3"
    assert ceph_version1.major == '1.3'
    assert ceph_version1.minor == "3"
    assert not ceph_version1.is_els
    assert ceph_version1.downstream_release == "async 2"

    ceph_version4 = CephVersion(context_wrap(CV4))
    assert ceph_version4.version == "2.0"
    assert ceph_version4.major == '2'
    assert ceph_version4.minor == "0"
    assert not ceph_version4.is_els
    assert ceph_version4.downstream_release == "0"

    ceph = CephVersion(context_wrap(CV_5))
    assert ceph.version == "2.2"
    assert ceph.major == '2'
    assert ceph.minor == '2'
    assert not ceph.is_els
    assert ceph.downstream_release == "0"

    ceph_version7 = CephVersion(context_wrap(CV7))
    assert ceph_version7.version == "2.2"
    assert ceph_version7.major == '2'
    assert ceph_version7.minor == "2"
    assert not ceph_version7.is_els
    assert ceph_version7.downstream_release == "0"

    ceph_version8 = CephVersion(context_wrap(CV8))
    assert ceph_version8.version == "2.3"
    assert ceph_version8.major == '2'
    assert ceph_version8.minor == "3"
    assert not ceph_version8.is_els
    assert ceph_version8.downstream_release == "0"

    ceph_version9 = CephVersion(context_wrap(CV9))
    assert ceph_version9.version == "3.1.1"
    assert ceph_version9.major == '3'
    assert ceph_version9.minor == "1"
    assert not ceph_version9.is_els
    assert ceph_version9.downstream_release == "1"

    ceph_version10 = CephVersion(context_wrap(CV10))
    assert ceph_version10.version == "3.2.2"
    assert ceph_version10.major == '3'
    assert ceph_version10.minor == "2"
    assert not ceph_version10.is_els
    assert ceph_version10.downstream_release == "2"

    ceph_version10_1 = CephVersion(context_wrap(CV10_1))
    assert ceph_version10_1.version == "3.3.1"
    assert ceph_version10_1.major == '3'
    assert ceph_version10_1.minor == "3"
    assert not ceph_version10_1.is_els
    assert ceph_version10_1.downstream_release == "1"

    ceph_version_els = CephVersion(context_wrap(CV_els))
    assert ceph_version_els.version == "2.5.5"
    assert ceph_version_els.major == '2'
    assert ceph_version_els.minor == "5"
    assert ceph_version_els.is_els
    assert ceph_version_els.downstream_release == "5"
