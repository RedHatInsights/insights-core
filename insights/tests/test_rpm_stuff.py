from insights import rpm_stuff
# import mock
import pytest
try:
    import rpm
    _skip_tests = False
except ImportError:
    _skip_tests = True


@pytest.mark.skipif(_skip_tests, reason="Skip rpm module")
def test_rpm_stuff():
    result, success, version = rpm_stuff.rpm_commands(1)
    print("RPM Version", version)
    print("RPM Version", rpm.__version__)
    assert result == 2
    assert success is True
