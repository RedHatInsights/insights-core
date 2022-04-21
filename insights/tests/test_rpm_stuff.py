from insights import rpm_stuff

_skip_tests = False
import mock
import pytest
try:
    import rpm
except ImportError:
    _skip_tests = True


@pytest.mark.skipif(_skip_tests, reason="Skip rpm module")
def test_rpm_stuff():
    assert rpm_stuff.rpm_commands(1) == (2, True)
