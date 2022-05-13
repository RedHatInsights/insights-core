from insights.parsers.ls_docker_volumes import DockerVolumesDir
from insights.tests import context_wrap

DOCKER_VOLUME_EMPTY_DIR = """
/var/lib/docker/volumes/:
total 0
drwx------. 3 0 0   77 Mar 15 10:50 .
drwx-----x. 9 0 0 4096 Nov 18 22:04 ..
"""

# Truncated 64-character hash into '7HASH7' for legibility
DOCKER_VOLUME_HAS_VOL_DIR = """
/var/lib/docker/volumes/:
total 4
drwx------. 3 0 0   77 Mar 15 10:50 .
drwx-----x. 9 0 0 4096 Nov 18 22:04 ..
drwxr-xr-x. 3 0 0   18 Mar 15 10:50 7HASH7

/var/lib/docker/volumes/7HASH7:
total 0
drwxr-xr-x. 3 0 0 18 Mar 15 10:50 .
drwx------. 3 0 0 77 Mar 15 10:50 ..
drwxr-xr-x. 2 0 0  6 Mar 15 10:50 _data

/var/lib/docker/volumes/7HASH7/_data:
total 0
drwxr-xr-x. 2 0 0  6 Mar 15 10:50 .
drwxr-xr-x. 3 0 0 18 Mar 15 10:50 ..
"""

BASE_DIR = '/var/lib/docker/volumes/'


def test_empty_dir():
    ctx = context_wrap(DOCKER_VOLUME_EMPTY_DIR, path='/bin/ls -lanR /var/lib/docker/volumes')
    dirs = DockerVolumesDir(ctx)

    assert BASE_DIR in dirs
    assert dirs.dirs_of(BASE_DIR) == ['.', '..']
    assert dirs.files_of(BASE_DIR) == []


def test_has_volumes():
    ctx = context_wrap(DOCKER_VOLUME_HAS_VOL_DIR, path='/bin/ls -lanR /var/lib/docker/volumes')
    dirs = DockerVolumesDir(ctx)

    assert BASE_DIR in dirs
    assert dirs.dirs_of(BASE_DIR) == ['.', '..', '7HASH7']
    assert dirs.files_of(BASE_DIR) == []

    volume_dir = BASE_DIR + '7HASH7'
    assert volume_dir in dirs
    assert dirs.dirs_of(volume_dir) == ['.', '..', '_data']
    assert dirs.files_of(volume_dir) == []
