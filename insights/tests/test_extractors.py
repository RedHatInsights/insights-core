import os
import shlex
import subprocess
import tempfile
import zipfile
from contextlib import closing

from insights.core.hydration import get_all_files
from insights.core.archives import extract


def test_with_zip():
    tmp_dir = tempfile.mkdtemp()

    d = os.path.join(tmp_dir, 'sys', 'kernel')
    os.makedirs(d)
    with open(os.path.join(d, 'kexec_crash_size'), "w") as f:
        f.write("ohyeahbaby")

    try:
        os.unlink("/tmp/test.zip")
    except:
        pass

    # stolen from zipfile.py:main
    def _add_to_zip(zf, path, zippath):
        if os.path.isfile(path):
            zf.write(path, zippath, zipfile.ZIP_DEFLATED)
        elif os.path.isdir(path):
            if zippath:
                zf.write(path, zippath)
            for nm in os.listdir(path):
                _add_to_zip(zf, os.path.join(path, nm), os.path.join(zippath, nm))
        # else: ignore

    with closing(zipfile.ZipFile("/tmp/test.zip", "w")) as zf:
        _add_to_zip(zf, tmp_dir, os.path.basename(tmp_dir))

    try:
        with extract("/tmp/test.zip") as ex:
            assert any(f.endswith("/sys/kernel/kexec_crash_size") for f in get_all_files(ex.tmp_dir))

    finally:
        os.unlink("/tmp/test.zip")

    subprocess.call(shlex.split("rm -rf %s" % tmp_dir))
