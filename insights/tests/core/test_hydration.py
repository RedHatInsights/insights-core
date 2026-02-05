import pytest
import sys
import tempfile

from os import chmod, makedirs
from os.path import join
from shutil import rmtree

from insights.core.context import HostArchiveContext, SerializedArchiveContext, SosArchiveContext
from insights.core.exceptions import ContextException, InvalidArchive
from insights.core.hydration import get_all_files, create_context


def test_get_all_files():
    tmp_dir = tempfile.mkdtemp()

    d = join(tmp_dir, 'sys', 'kernel')
    makedirs(d)
    with open(join(d, 'kexec_crash_size'), "w") as f:
        f.write("ohyeahbaby")

    with open(join(d, 'kexec_loaded'), "w") as f:
        f.write("1")

    assert any(f.endswith("/sys/kernel/kexec_crash_size") for f in get_all_files(tmp_dir))

    rmtree(tmp_dir, ignore_errors=True)


# here we also skip testing it in Python 3.6, as `root` might be used in the
# test image, "Error 13" won't be occurred
@pytest.mark.skipif(sys.version_info < (3, 8), reason="This issue only occurs on python3+.")
def test_get_all_files_oserror(caplog):
    tmp_dir = tempfile.mkdtemp()

    d = join(tmp_dir, 'sys', 'kernel')
    makedirs(d)
    with open(join(d, 'kexec_crash_size'), "w") as f:
        f.write("ohyeahbaby")

    chmod(d, 0o644)
    chmod(join(tmp_dir, "sys"), 0o677)

    any(f.endswith("/sys/kernel/kexec_crash_size") for f in get_all_files(tmp_dir))
    assert "Errno 13" in caplog.text

    chmod(join(tmp_dir, "sys"), 0o777)
    chmod(d, 0o777)
    rmtree(tmp_dir, ignore_errors=True)


def test_create_context_no_option():
    tmp_dir = tempfile.mkdtemp()

    d = join(tmp_dir, 'data')
    makedirs(d)

    open(join(tmp_dir, 'insights_archive.txt'), 'a').close()

    context = create_context(tmp_dir)
    assert SerializedArchiveContext == type(context), context

    rmtree(tmp_dir, ignore_errors=True)


def test_create_context_with_option_regular():
    tmp_dir = tempfile.mkdtemp()

    d1 = join(tmp_dir, 'data')
    makedirs(d1)
    d2 = join(d1, 'insights_commands')
    makedirs(d2)

    open(join(tmp_dir, 'insights_archive.txt'), 'a').close()
    open(join(d2, 'uname_-a'), 'a').close()

    # Try to identify SerializedArchiveContext first and match
    context = create_context(tmp_dir, SerializedArchiveContext)
    assert SerializedArchiveContext == type(context), context
    assert context.root == tmp_dir, context.root

    # Try to identify HostArchiveContext first and match
    context = create_context(tmp_dir, HostArchiveContext)
    assert HostArchiveContext == type(context), context
    assert context.root == d1, context.root

    # Try to identify SosArchiveContext first and NOT match
    with pytest.raises(ContextException) as ce:
        create_context(tmp_dir, SosArchiveContext)
    assert "ExecutionContext mismatch:" in str(ce)
    assert "Cannot found '{0}.{1}'".format(
        SosArchiveContext.__module__, SosArchiveContext.__name__
    ) in str(ce.value)
    assert "{0}.{1} ({2})".format(
        SerializedArchiveContext.__module__, SerializedArchiveContext.__name__, tmp_dir
    ) in str(ce.value)

    rmtree(tmp_dir, ignore_errors=True)


def test_create_context_with_option_exception_1():
    tmp_dir = tempfile.mkdtemp()

    d1 = join(tmp_dir, 'data')
    makedirs(d1)

    with pytest.raises(InvalidArchive) as ce:
        create_context(tmp_dir, HostArchiveContext)
    assert "No files in archive" in str(ce.value)

    rmtree(tmp_dir, ignore_errors=True)
