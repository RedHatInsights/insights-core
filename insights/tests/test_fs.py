import os
import shutil
import tempfile

from contextlib import closing
from insights.util import fs


def test_remove_exists():
    full_path = None
    with closing(tempfile.NamedTemporaryFile(delete=False)) as f:
        full_path = f.name
        f.write(b'test')

    assert os.path.exists(full_path)
    fs.remove(full_path)
    assert not os.path.exists(full_path)


def test_remove_not_exists():
    full_path = os.path.expandvars('$PWD/not/a/path')
    assert not os.path.exists(full_path)
    fs.remove(full_path)
    assert not os.path.exists(full_path)


def test_not_exists_ensure_path():
    base_path = os.path.expandvars('$PWD/a')
    path = os.path.expandvars('$PWD/a/b/c')

    assert not os.path.exists(base_path)

    fs.ensure_path(path)
    assert os.path.exists(path)

    shutil.rmtree(base_path)
    assert not os.path.exists(base_path)


def test_exists_ensure_path_exists():
    path = os.path.expandvars('$PWD')
    assert os.path.exists(path)
    fs.ensure_path(path)
    assert os.path.exists(path)
