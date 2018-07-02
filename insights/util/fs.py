import errno
import hashlib
import os

from insights.util import subproc


def read_in_chunks(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def hash_bytestr_iter(bytesiter, hasher):
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest()


def file_as_blockiter(afile, blocksize=65536):
    block = afile.read(blocksize)
    while len(block) > 0:
        yield block
        block = afile.read(blocksize)


def sha256(path):
    with open(path, "rb") as f:
        block_iter = file_as_blockiter(f)
        hasher = hashlib.sha256()
        return hash_bytestr_iter(block_iter, hasher)


def remove(path, chmod=False):
    """Remove a file or directory located on the filesystem at path.

    If chmod is True, chmod -R 755 is executed on the path
    before rm -rf path is called.

    Parameters
    ----------
    path : str
        file system path to an existing file or directory
    chmod : bool
        If True, chmod -R 755 is executed on path before
        it's removed.

    Raises
    ------
    CalledProcessError
        If any part of the removal process fails.
    """

    if not os.path.exists(path):
        return

    if chmod:
        cmd = "chmod -R 755 %s" % path
        subproc.call(cmd)

    cmd = 'rm -rf "{p}"'.format(p=path)
    subproc.call(cmd)


def ensure_path(path, mode=0o777):
    """Ensure that path exists in a multiprocessing safe way.

    If the path does not exist, recursively create it and its parent
    directories using the provided mode.  If the path already exists,
    do nothing.  The umask is cleared to enable the mode to be set,
    and then reset to the original value after the mode is set.

    Parameters
    ----------
    path : str
        file system path to a non-existent directory
        that should be created.
    mode : int
        octal representation of the mode to use when creating
        the directory.

    Raises
    ------
    OSError
        If os.makedirs raises an OSError for any reason
        other than if the directory already exists.
    """

    if path:
        try:
            umask = os.umask(000)
            os.makedirs(path, mode)
            os.umask(umask)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


def size(path):
    """Return the size of the file.

    Parameters
    ----------
    path : str
        absolute path to a file.

    Returns
    -------
    int
        size of the file in bytes.
    """

    return os.stat(path).st_size
