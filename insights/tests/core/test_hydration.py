import pytest
import sys
import tempfile

from insights.core.hydration import get_all_files
from os import chmod, makedirs
from os.path import join
from shutil import rmtree


def test_get_all_files():
    tmp_dir = tempfile.mkdtemp()

    d = join(tmp_dir, 'sys', 'kernel')
    makedirs(d)
    with open(join(d, 'kexec_crash_size'), "w") as f:
        f.write("ohyeahbaby")

    with open(join(d, 'kexec_loaded'), "w") as f:
        f.write("1")

    assert any(f.endswith("/sys/kernel/kexec_crash_size") for f in get_all_files(tmp_dir))

    rmtree(tmp_dir, ignore_errors=True)


@pytest.mark.skipif(sys.version_info < (3, 6), reason="This issue only occurs on python3+.")
def test_get_all_files_oserror(caplog):
    tmp_dir = tempfile.mkdtemp()

    d = join(tmp_dir, 'sys', 'kernel')
    makedirs(d)
    with open(join(d, 'kexec_crash_size'), "w") as f:
        f.write("ohyeahbaby")

    chmod(d, 0o644)
    chmod(join(tmp_dir, "sys"), 0o677)

    any(f.endswith("/sys/kernel/kexec_crash_size") for f in get_all_files(tmp_dir))
    assert "Errno 13" in caplog.text

    chmod(join(tmp_dir, "sys"), 0o777)
    chmod(d, 0o777)
    rmtree(tmp_dir, ignore_errors=True)
