from insights.parsers import kpatch_patches
from insights.tests import context_wrap
from insights.core.plugins import ContentException
import pytest


ASSORTED_KPATCHES = """
asdfasdfasdf_asdfasdfasdf-asdfasdfasdf_asdfasdfasdf.ko
asdfasdfasdf_asdfasdfasdf-asdfasdfasdf_asdfasdfasdf.ko.xz
foo-bar.ko
foo-bar.ko.xz
foo.ko
foo.ko.xz
test_klp_callbacks_demo.ko
test_klp_callbacks_demo.ko.xz
""".strip()

NO_KPATCH = """
/bin/ls: cannot access '/var/lib/kpatch/4.18.0-147.8.el8.x86_64': No such file or directory
""".strip()


# Try a bunch of random potential patch names
# Compare to expected module names
def test_assorted():
    kp = kpatch_patches.KpatchPatches(context_wrap(ASSORTED_KPATCHES))
    for patch in [
            'asdfasdfasdf_asdfasdfasdf_asdfasdfasdf_asdfasdfasdf',
            'foo_bar',
            'foo',
            'test_klp_callbacks_demo']:
        assert patch in kp.patches


# Try the case of no patches installed
def test_no_kpatch():
    with pytest.raises(ContentException):
        kpatch_patches.KpatchPatches(context_wrap(NO_KPATCH))
