from insights.core.context import (
    ExecutionContextMeta,
    HostArchiveContext,
    SerializedArchiveContext,
    SosArchiveContext,
)


def test_host_archive_context():
    files = ["/foo/junk", "/insights_commands"]
    actual = HostArchiveContext.handles(files)
    assert actual == ("/", HostArchiveContext), actual

    files = ["/foo/junk", "/insights_commands/things"]
    actual = HostArchiveContext.handles(files)
    assert actual == ("/", HostArchiveContext), actual

    files = ["/foo/junk", "/foo/junk/insights_commands/foobar.txt"]
    actual = HostArchiveContext.handles(files)
    assert actual == ("/foo/junk", HostArchiveContext), actual


def test_host_archive_context_unsupported():
    files = ["/foo/junk", "/not_insights_commands"]
    actual = HostArchiveContext.handles(files)
    assert actual == (None, None), actual

    files = ["/foo/junk", "/insights_commands_not"]
    actual = HostArchiveContext.handles(files)
    assert actual == (None, None), actual


def test_sos_archive_context_supported():
    files = ["/foo/junk", "/sos_commands"]
    actual = SosArchiveContext.handles(files)
    assert actual == ("/", SosArchiveContext), actual

    files = ["/foo/junk", "/sos_commands/things"]
    actual = SosArchiveContext.handles(files)
    assert actual == ("/", SosArchiveContext), actual

    files = ["/foo/junk", "/foo/junk/sos_commands/foobar.txt"]
    actual = SosArchiveContext.handles(files)
    assert actual == ("/foo/junk", SosArchiveContext), actual


def test_sos_archive_context_unsupported():
    files = ["/foo/junk", "/sos_commands_not"]
    actual = SosArchiveContext.handles(files)
    assert actual == (None, None), actual

    files = ["/foo/junk", "/not_sos_commands"]
    actual = SosArchiveContext.handles(files)
    assert actual == (None, None), actual


def test_serialize_archive_context_supported():
    files = ["/foo/junk", "/insights_archive.txt"]
    actual = SerializedArchiveContext.handles(files)
    assert actual == ("/", SerializedArchiveContext), actual


def test_serialized_archive_context_unsupported():
    files = ["/foo/junk", "/sos_commands_not"]
    actual = SerializedArchiveContext.handles(files)
    assert actual == (None, None), actual

    files = ["/foo/junk", "/insights_archive"]
    actual = SerializedArchiveContext.handles(files)
    assert actual == (None, None), actual


def test_unrecognized():
    files = ["/foo/junk", "/bar/junk"]
    actual = ExecutionContextMeta.identify(files)
    assert actual == (None, None), actual


def test_archive_context_identify_all():
    files = ["/foo/junk", "/insights_archive.txt"]
    actual = ExecutionContextMeta.identify_all(files)
    assert len(actual) == 1
    assert actual["/"] == SerializedArchiveContext

    files = ["/foo/junk", "/sos_commands/things"]
    actual = ExecutionContextMeta.identify_all(files)
    assert len(actual) == 1
    assert actual["/"] == SosArchiveContext

    files = ["/foo/junk", "/data/insights_commands", "/insights_archive.txt"]
    actual = ExecutionContextMeta.identify_all(files)
    assert len(actual) == 2
    assert actual["/"] == SerializedArchiveContext
    assert actual["/data"] == HostArchiveContext

    files = ["/foo/junk", "/bar/junk"]
    actual = ExecutionContextMeta.identify_all(files)
    assert len(actual) == 0
