from insights.core.context import HostArchiveContext, SosArchiveContext, SerializedArchiveContext

def test_host_archive_context():
    files = [
            "/foo/junk",
            "/insights_commands",
            ]
    actual = HostArchiveContext.handles(files)
    assert actual == ("/", HostArchiveContext), actual


def test_host_archive_context_unsupported():
    files = [
            "/foo/junk",
            "/not_insights_commands",
            ]
    actual = HostArchiveContext.handles(files)
    assert actual == (None, None), actual
