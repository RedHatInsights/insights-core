import pytest
import sys
import tempfile

from os import chmod, makedirs
from os.path import dirname, join
from shutil import rmtree

from insights.core.context import (
    ClusterArchiveContext,
    HostArchiveContext,
    SerializedArchiveContext,
    SosArchiveContext,
)
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


def create_file(root, relpath, content=""):
    file_path = join(root, relpath)
    # Python 2.7 does not support exist_ok and raises an exception when path exists
    try:
        makedirs(dirname(file_path))
    except FileExistsError:
        pass
    fd = open(file_path, "w")
    fd.write(content)
    fd.close()
    return file_path


CLUSTER_ARCHIVE_CONTEXT_SAMPLE_ARCHIVE = "cluster_archive_context_archive1.tar.gz"


def create_cluster_archive_context(root):
    create_file(root, CLUSTER_ARCHIVE_CONTEXT_SAMPLE_ARCHIVE)


SERIALIZED_ARCHIVE_CONTEXT_ROOT = "serialized_archive_context"
SERIALIZED_ARCHIVE_CONTEXT_MARKER = "insights_archive.txt"


def create_serialized_archive_context(root):
    create_file(root, join(SERIALIZED_ARCHIVE_CONTEXT_ROOT, SERIALIZED_ARCHIVE_CONTEXT_MARKER))


SOS_ARCHIVE_CONTEXT_ROOT = "sos_archive_context"
SOS_ARCHIVE_CONTEXT_MARKER = "sos_commands/uname_-a"


def create_sos_archive_context(root):
    create_file(root, join(SOS_ARCHIVE_CONTEXT_ROOT, SOS_ARCHIVE_CONTEXT_MARKER))


def test_create_context_autodetection_cluster_archive_context(caplog, tmpdir):
    """Automatic detection selects ClusterArchiveContext whenever present.

    The path contains ClusterArchiveContext, SerializedArchiveContext and SosArchiveContext.
    In the current implementation, ClusterArchiveContext takes precedence over any other execution
    context when the automatic detection is used.
    """
    create_cluster_archive_context(tmpdir)
    create_serialized_archive_context(tmpdir)
    create_sos_archive_context(tmpdir)

    context = create_context(tmpdir)
    assert type(context) is ClusterArchiveContext
    assert context.root == tmpdir
    assert context.all_files == [join(tmpdir, CLUSTER_ARCHIVE_CONTEXT_SAMPLE_ARCHIVE)]


def test_create_context_autodetection_other(caplog, tmpdir):
    """Automatic detection selects the last-defined execution context that matches the path.

    The path contains SerializedArchiveContext and SosArchiveContext. SosArchiveContext gets
    selected because it is defined after SerializedArchiveContext.
    """
    create_serialized_archive_context(tmpdir)
    create_sos_archive_context(tmpdir)

    context = create_context(tmpdir)
    assert type(context) is SosArchiveContext
    assert context.root == join(tmpdir, SOS_ARCHIVE_CONTEXT_ROOT)
    assert sorted(context.all_files) == [
        join(tmpdir, SERIALIZED_ARCHIVE_CONTEXT_ROOT, SERIALIZED_ARCHIVE_CONTEXT_MARKER),
        join(tmpdir, SOS_ARCHIVE_CONTEXT_ROOT, SOS_ARCHIVE_CONTEXT_MARKER),
    ]


def test_create_context_autodetection_fallback(caplog, tmpdir):
    """HostArchiveContext is used if no other execution context is found.

    The path does not contain data for any loaded execution context. The function creates
    HostArchiveContext in that case.
    """
    # at least one file or directory has to exist otherwise an exception gets raised
    create_file(tmpdir, "some_file.txt")

    context = create_context(tmpdir)
    assert type(context) is HostArchiveContext
    assert context.root == tmpdir
    assert context.all_files == [join(tmpdir, "some_file.txt")]


def test_create_context_user_defined_fallback(caplog, tmpdir):
    """Use HostArchiveContext even if it is not found when requested.

    The path contains no execution context while the user specified HostArchiveContext.

    The HostArchiveContext was not found in the path, but it is the ultimate fallback that would be
    selected by auto-detection regardless. We need to create it to remain consistent with
    auto-detection.
    """
    # at least one file or directory has to exist for the auto-detection mechanism to choose
    # HostArchiveContext
    create_file(tmpdir, "some_file.txt")

    context = create_context(tmpdir, context=HostArchiveContext)
    assert type(context) is HostArchiveContext
    assert context.root == tmpdir
    assert context.all_files == [join(tmpdir, "some_file.txt")]


def test_create_context_user_defined_cluster_archive_context(caplog, tmpdir):
    """ClusterArchiveContext is selected when requested by the user.

    The path contains ClusterArchiveContext, SerializedArchiveContext and SosArchiveContext and the
    user requested ClusterArchiveContext. ClusterArchiveContext will be used.

    This test is required because ClusterArchiveContext has custom initialization logic in
    create_context (bad!).
    """
    create_cluster_archive_context(tmpdir)
    create_serialized_archive_context(tmpdir)
    create_sos_archive_context(tmpdir)

    context = create_context(tmpdir, context=ClusterArchiveContext)
    assert type(context) is ClusterArchiveContext
    assert context.root == tmpdir
    assert context.all_files == [join(tmpdir, CLUSTER_ARCHIVE_CONTEXT_SAMPLE_ARCHIVE)]


def test_create_context_user_defined_other(caplog, tmpdir):
    """User-defined execution context takes precedence over everything else.

    The path contains ClusterArchiveContext, SerializedArchiveContext and SosArchiveContext.
    SerializedArchiveContext gets selected because it is requested by the user, despite
    ClusterArchiveContext taking precedence over everything else otherwise and SosArchiveContext
    being defined after SerializedArchiveContext.
    """
    create_cluster_archive_context(tmpdir)
    create_serialized_archive_context(tmpdir)
    create_sos_archive_context(tmpdir)

    context = create_context(tmpdir, context=SerializedArchiveContext)
    assert type(context) is SerializedArchiveContext
    assert context.root == join(tmpdir, SERIALIZED_ARCHIVE_CONTEXT_ROOT)
    assert sorted(context.all_files) == [
        join(tmpdir, CLUSTER_ARCHIVE_CONTEXT_SAMPLE_ARCHIVE),
        join(tmpdir, SERIALIZED_ARCHIVE_CONTEXT_ROOT, SERIALIZED_ARCHIVE_CONTEXT_MARKER),
        join(tmpdir, SOS_ARCHIVE_CONTEXT_ROOT, SOS_ARCHIVE_CONTEXT_MARKER),
    ]


def test_create_context_did_you_mean_cluster_archive_context(caplog, tmpdir):
    """ClusterArchiveContext is suggested whenever present.

    The path contains ClusterArchiveContext, SerializedArchiveContext and SosArchiveContext while
    the user specified HostArchiveContext. The function raises an exception and suggests
    ClusterArchiveContext. In the current implementation ClusterArchiveContext is selected
    automatically whenever present.
    """
    create_cluster_archive_context(tmpdir)
    create_serialized_archive_context(tmpdir)
    create_sos_archive_context(tmpdir)

    with pytest.raises(ContextException, match="Did you mean 'insights.core.context.ClusterArchiveContext'"):
        create_context(tmpdir, context=HostArchiveContext)


def test_create_context_did_you_mean_other(caplog, tmpdir):
    """ClusterArchiveContext is suggested whenever present.

    The path contains SerializedArchiveContext and SosArchiveContext while the user specified
    HostArchiveContext. The function raises an exception and suggests SosArchiveContext because it
    was defined after SerializedArchiveContext.
    """
    create_serialized_archive_context(tmpdir)
    create_sos_archive_context(tmpdir)

    with pytest.raises(ContextException, match="Did you mean 'insights.core.context.SosArchiveContext'"):
        create_context(tmpdir, context=HostArchiveContext)


@pytest.mark.parametrize("user_defined_context", [None, HostArchiveContext])
def test_create_context_empty_path(caplog, tmpdir, user_defined_context):
    """Raises an exception when the path is empty."""
    with pytest.raises(InvalidArchive) as ce:
        create_context(tmpdir, context=user_defined_context)
    assert "No files in archive" in str(ce)
