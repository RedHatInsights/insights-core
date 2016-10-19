import os
import shutil
import tempfile
import unittest

from contextlib import closing
from falafel.util import fs


class TestFS(unittest.TestCase):
    def test_remove_exists(self):
        full_path = None
        with closing(tempfile.NamedTemporaryFile(delete=False)) as f:
            full_path = f.name
            f.write('test')

        self.assertTrue(os.path.exists(full_path))
        fs.remove(full_path)
        self.assertFalse(os.path.exists(full_path))

    def test_remove_not_exists(self):
        full_path = os.path.expandvars('$PWD/not/a/path')
        self.assertFalse(os.path.exists(full_path))
        fs.remove(full_path)
        self.assertFalse(os.path.exists(full_path))

    def test_not_exists_ensure_path(self):
        base_path = os.path.expandvars('$PWD/a')
        path = os.path.expandvars('$PWD/a/b/c')

        self.assertFalse(os.path.exists(base_path))

        fs.ensure_path(path)
        self.assertTrue(os.path.exists(path))

        shutil.rmtree(base_path)
        self.assertFalse(os.path.exists(base_path))

    def test_exists_ensure_path_exists(self):
        path = os.path.expandvars('$PWD')
        self.assertTrue(os.path.exists(path))
        fs.ensure_path(path)
        self.assertTrue(os.path.exists(path))
