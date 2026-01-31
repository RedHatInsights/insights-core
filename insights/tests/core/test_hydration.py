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
from insights.core.exceptions import InvalidArchive
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
    return create_file(root, CLUSTER_ARCHIVE_CONTEXT_SAMPLE_ARCHIVE)


SERIALIZED_ARCHIVE_CONTEXT_ROOT = "serialized_archive_context"
SERIALIZED_ARCHIVE_CONTEXT_MARKER = "insights_archive.txt"


def create_serialized_archive_context(root):
    return create_file(root, join(SERIALIZED_ARCHIVE_CONTEXT_ROOT, SERIALIZED_ARCHIVE_CONTEXT_MARKER))


SOS_ARCHIVE_CONTEXT_ROOT = "sos_archive_context"
SOS_ARCHIVE_CONTEXT_MARKER = "sos_commands/uname_-a"


def create_sos_archive_context(root):
    return create_file(root, join(SOS_ARCHIVE_CONTEXT_ROOT, SOS_ARCHIVE_CONTEXT_MARKER))


HOST_ARCHIVE_CONTEXT_ROOT = "host_archive_context"
HOST_ARCHIVE_CONTEXT_MARKER = "insights_commands"


def create_host_archive_context(root):
    return create_file(root, join(HOST_ARCHIVE_CONTEXT_ROOT, HOST_ARCHIVE_CONTEXT_MARKER))


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
    expected_all_files = [
        create_serialized_archive_context(tmpdir),
        create_sos_archive_context(tmpdir),
    ]

    context = create_context(tmpdir)
    assert type(context) is SosArchiveContext
    assert context.root == join(tmpdir, SOS_ARCHIVE_CONTEXT_ROOT)
    assert sorted(context.all_files) == sorted(expected_all_files)


def test_create_context_autodetection_host_archive_context(caplog, tmpdir):
    """Automatic detection can select HostArchiveContext by marker when present.

    The path contains only HostArchiveContext (to prevent other execution contexts from being
    selected). The function correctly identifies HostArchiveContext location and selects it.

    This behavior is different from the case when HostArchiveContext is selected as the ultimate
    fallback option.
    """
    expected_all_files = [
        create_file(tmpdir, "some_file.txt"),
        create_host_archive_context(tmpdir),
    ]

    context = create_context(tmpdir)
    assert type(context) is HostArchiveContext
    assert context.root == join(tmpdir, HOST_ARCHIVE_CONTEXT_ROOT)
    assert sorted(context.all_files) == sorted(expected_all_files)


def test_create_context_autodetection_fallback(caplog, tmpdir):
    """HostArchiveContext is used if no other execution context is found.

    The path does not contain data for any loaded execution context. The function creates
    HostArchiveContext in that case (this behavior is kept for backwards compatibility; it is not
    clear why this behavior exists).
    """
    # autodetection fails if the archive is completely empty
    create_file(tmpdir, "some_file.txt")

    context = create_context(tmpdir)
    assert type(context) is HostArchiveContext
    assert context.root == tmpdir
    assert context.all_files == [join(tmpdir, "some_file.txt")]


def test_create_context_user_defined_host_archive_context(caplog, tmpdir):
    """HostArchiveContext is selected when present and requested by the user.

    The path contains HostArchiveContext and SosArchiveContext and the user requested
    HostArchiveContext. HostArchiveContext will be used.
    """
    expected_all_files = [
        create_host_archive_context(tmpdir),
        create_sos_archive_context(tmpdir),
    ]

    context = create_context(tmpdir, context=HostArchiveContext)
    assert type(context) is HostArchiveContext
    assert context.root == join(tmpdir, HOST_ARCHIVE_CONTEXT_ROOT)
    assert sorted(context.all_files) == sorted(expected_all_files)


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
    expected_all_files = [
        create_cluster_archive_context(tmpdir),
        create_serialized_archive_context(tmpdir),
        create_sos_archive_context(tmpdir),
    ]

    context = create_context(tmpdir, context=SerializedArchiveContext)
    assert type(context) is SerializedArchiveContext
    assert context.root == join(tmpdir, SERIALIZED_ARCHIVE_CONTEXT_ROOT)
    assert sorted(context.all_files) == sorted(expected_all_files)


TEST_CASES_USER_DEFINED_NOT_FOUND = [
    [
        "ClusterArchiveContext, non-empty dir",
        ClusterArchiveContext,
        [
            create_serialized_archive_context,
            create_sos_archive_context,
        ],
    ],
    [
        "SosArchiveContext, non-empty dir with ClusterArchiveContext",
        SosArchiveContext,
        [
            create_cluster_archive_context,
            create_serialized_archive_context,
        ],
    ],
    [
        "SosArchiveContext, non-empty dir without ClusterArchiveContext",
        SosArchiveContext,
        [
            create_host_archive_context,
            create_serialized_archive_context,
        ],
    ],
    [
        "HostArchiveContext, some other contexts",
        HostArchiveContext,
        [
            create_sos_archive_context,
            create_serialized_archive_context,
        ],
    ],
    [
        "HostArchiveContext, no other contexts",
        HostArchiveContext,
        [
            lambda tmpdir: create_file(tmpdir, "some_file.txt"),
        ],
    ],
]


@pytest.mark.parametrize(
    "context,create_archive_functions",
    [test_case[1:] for test_case in TEST_CASES_USER_DEFINED_NOT_FOUND],
    ids=[test_case[0] for test_case in TEST_CASES_USER_DEFINED_NOT_FOUND],
)
def test_create_context_user_defined_not_found(caplog, tmpdir, context, create_archive_functions):
    """Raise InvalidArchive when the user-defined context cannot be found."""
    for f in create_archive_functions:
        f(tmpdir)

    msg_regex = "Cannot find execution context '{0}.{1}'".format(
        context.__module__,
        context.__name__,
    )
    with pytest.raises(InvalidArchive, match=msg_regex):
        create_context(tmpdir, context=context)


@pytest.mark.parametrize(
    "context, message",
    [
        [None, "Cannot detect execution context: No files in path"],
        [HostArchiveContext, "Cannot find execution context"],
    ]
)
def test_create_context_empty_path(caplog, tmpdir, context, message):
    """Raises an exception when the path is empty."""
    with pytest.raises(InvalidArchive, match=message):
        create_context(tmpdir, context=context)
