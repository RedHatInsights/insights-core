import os
import unittest
import tempfile
import subprocess
import shlex

from falafel.core import archives

HERE = os.path.abspath(os.path.dirname(__file__))

class TestOnDiskExtractor(unittest.TestCase):
    def test_from_buffer_with_directory(self):

        path = os.path.join(HERE, "insights_heartbeat.tar.gz")

        tmp_dir = tempfile.mkdtemp()

        command = "tar -a -x -f %s -C %s" % (path, tmp_dir)
        subprocess.call(shlex.split(command))

        with archives.OnDiskExtractor() as tar_ex:
            with archives.OnDiskExtractor() as dir_ex:
                tar_tf = tar_ex.from_path(path)
                tar_all_files = tar_tf.getnames()

                dir_tf = dir_ex.from_path(tmp_dir)
                dir_all_files = dir_tf.getnames()

                self.assertEqual(len(tar_all_files),len(dir_all_files))

                for tar_path in tar_all_files:
                    dir_path = os.path.join(dir_tf.tar_file.path,
                                            os.path.relpath(tar_path, tar_tf.tar_file.path))
                    tar_content = tar_tf.extractfile(tar_path)
                    dir_content = dir_tf.extractfile(dir_path)

                    self.assertEqual(tar_content, dir_content)

        command = "rm -rf %s" % tmp_dir
        subprocess.call(shlex.split(command))
