import shutil
import tempfile
from contextlib import closing

import os
import pytest

from insights.util import fs


def test_remove_exists():
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


@pytest.fixture(params=[('644', '644'), ('775', '755'), ('777', '755')])
def mode(request):
    yield request.param


@pytest.fixture
def mode_dir(mode):
    path = os.path.join('/tmp/insights-test-{mode}'.format(mode=mode[0]))
    yield path
    fs.remove(path)


def test_ensure_path_mode(mode, mode_dir):
    fs.ensure_path(mode_dir, int(mode[0], 8))
    assert oct(os.stat(mode_dir).st_mode)[-3:] == mode[1]


def test_ensure_path_mode_default():
    path = os.path.join('/tmp/insights-test-default')
    fs.ensure_path(path)
    assert oct(os.stat(path).st_mode)[-3:] == '755'
    fs.remove(path)


def test_touch_times():
    path = '/tmp/insights-test-touch-times'
    fs.touch(path, (1259798405, 1259798400))
    assert os.stat(path).st_atime == 1259798405
    assert os.stat(path).st_mtime == 1259798400
    fs.remove(path)
