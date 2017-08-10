import gzip
import os
import pytest
import shlex
import subprocess
import tempfile
import zipfile

from insights.core import archives
from insights.core.specs import SpecMapper
from . import insights_heartbeat


def test_from_buffer_with_directory():
    arc_path = insights_heartbeat()
    tmp_dir = tempfile.mkdtemp()
    command = "tar -a -x -f %s -C %s" % (arc_path, tmp_dir)
    subprocess.call(shlex.split(command))

    with archives.TarExtractor() as tar_ex:
        with archives.TarExtractor() as dir_ex:
            tar_tf = tar_ex.from_path(arc_path)
            tar_all_files = tar_tf.getnames()

            dir_tf = dir_ex.from_path(tmp_dir)
            dir_all_files = dir_tf.getnames()

            assert len(tar_all_files) == len(dir_all_files)

            for tar_path in tar_all_files:
                dir_path = os.path.join(dir_tf.tar_file.path,
                                        os.path.relpath(tar_path, tar_tf.tar_file.path))
                if not os.path.isdir(tar_path):
                    tar_content = tar_tf.extractfile(tar_path)
                    dir_content = dir_tf.extractfile(dir_path)
                    assert tar_content == dir_content

    command = "rm -rf %s"
    subprocess.call(shlex.split(command % tmp_dir))
    subprocess.call(shlex.split(command % arc_path))


def test__assert_type_gzip_tar():
    arc_path = insights_heartbeat()
    with archives.TarExtractor() as tar_ex:
        tar_ex._assert_type(arc_path, False)
        assert tar_ex.content_type in archives.TarExtractor.TAR_FLAGS
    subprocess.call(shlex.split("rm -rf %s" % arc_path))


def test__assert_type_gzip_no_tar():
    tmp_dir = tempfile.mkdtemp()

    archive_path = os.path.join(tmp_dir, "file.log.gz")
    with gzip.open(archive_path, 'wb') as f:
        f.write("testing contents")

    with archives.TarExtractor() as tar_ex:
        with pytest.raises(archives.InvalidArchive) as cm:
            tar_ex._assert_type(archive_path, False)
            assert cm.msg == "No compressed tar archive"


def test_with_zip():

    tmp_dir = tempfile.mkdtemp()
    arc_path = insights_heartbeat()
    command = "tar -a -x -f %s -C %s" % (arc_path, tmp_dir)
    subprocess.call(shlex.split(command))

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

    with zipfile.ZipFile("/tmp/test.zip", "w") as zf:
        _add_to_zip(zf, tmp_dir, os.path.basename(tmp_dir))

    try:
        with archives.ZipExtractor() as ex:
            ex.from_path("/tmp/test.zip")
            assert "foo" not in ex.getnames()
            assert any(f.endswith("/sys/kernel/kexec_crash_size") for f in ex.getnames())

            spec_mapper = SpecMapper(ex)
            assert spec_mapper.get_content("hostname") == ["insights-heartbeat-9cd6f607-6b28-44ef-8481-62b0e7773614"]
    finally:
        os.unlink("/tmp/test.zip")

    subprocess.call(shlex.split("rm -rf %s" % tmp_dir))
    subprocess.call(shlex.split("rm -rf %s" % arc_path))
