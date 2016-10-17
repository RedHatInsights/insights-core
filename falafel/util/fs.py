import errno
import os

from falafel.util import subproc


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

    cmd = 'rm -rf {p}'.format(p=path)
    subproc.call(cmd)


def ensure_path(path, mode=0777):
    """Ensure that path exists in a multiprocessing safe way.

    If the path does not exist, recursively create it and its parent
    directories using the provided mode.  If the path already exists,
    do nothing.

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
            os.makedirs(path, mode)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
