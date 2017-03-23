import os
import unittest
import tempfile
import subprocess
import shlex
from falafel.core import archives
from falafel.core.specs import SpecMapper

HERE = os.path.abspath(os.path.dirname(__file__))
ARC = os.path.join(HERE, "insights_heartbeat.tar.gz")


class TestTarExtractor(unittest.TestCase):
    def test_from_buffer_with_directory(self):

        tmp_dir = tempfile.mkdtemp()

        command = "tar -a -x -f %s -C %s" % (ARC, tmp_dir)
        subprocess.call(shlex.split(command))

        with archives.TarExtractor() as tar_ex:
            with archives.TarExtractor() as dir_ex:
                tar_tf = tar_ex.from_path(ARC)
                tar_all_files = tar_tf.getnames()

                dir_tf = dir_ex.from_path(tmp_dir)
                dir_all_files = dir_tf.getnames()

                self.assertEqual(len(tar_all_files), len(dir_all_files))

                for tar_path in tar_all_files:
                    dir_path = os.path.join(dir_tf.tar_file.path,
                                            os.path.relpath(tar_path, tar_tf.tar_file.path))
                    if not os.path.isdir(tar_path):
                        tar_content = tar_tf.extractfile(tar_path)
                        dir_content = dir_tf.extractfile(dir_path)
                        self.assertEqual(tar_content, dir_content)

        command = "rm -rf %s" % tmp_dir
        subprocess.call(shlex.split(command))


class TestZipFileExtractor(unittest.TestCase):
    def test_with_zip(self):

        tmp_dir = tempfile.mkdtemp()
        command = "tar -a -x -f %s -C %s" % (ARC, tmp_dir)
        subprocess.call(shlex.split(command))

        try:
            os.unlink("/tmp/test.zip")
        except:
            pass

        subprocess.call(shlex.split("zip -r /tmp/test.zip %s" % tmp_dir))

        with archives.ZipExtractor() as ex:
            ex.from_path("/tmp/test.zip")
            self.assertFalse("foo" in ex.getnames())
            self.assertTrue(any(f.endswith("insights_heartbeat/sys/kernel/kexec_crash_loaded") for f in ex.getnames()))

            spec_mapper = SpecMapper(ex)
            self.assertEquals(spec_mapper.get_content("hostname"), ["insights-heartbeat-9cd6f607-6b28-44ef-8481-62b0e7773614"])

        try:
            os.unlink("/tmp/test.zip")
        except:
            pass

        subprocess.call(shlex.split("rm -rf %s" % tmp_dir))
