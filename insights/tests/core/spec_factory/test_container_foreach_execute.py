from unittest.mock import patch

from insights import dr
from insights.core.context import HostContext
from insights.core.exceptions import NoFilterException
from insights.core.plugins import datasource
from insights.core.spec_factory import (
    DatasourceProvider,
    HostBasedContainerCommandProvider,
    container_foreach_execute,
    foreach_execute,
)


MOCK_WHICH = "insights.core.spec_factory.which"
MOCK_BLACKLIST = "insights.core.spec_factory.blacklist.allow_command"

SAMPLE_IMAGE = "registry.access.redhat.com/ubi8/ubi:latest"
SAMPLE_ENGINE = "podman"
SAMPLE_CID = "abc123def456"
SAMPLE_MERGED_DIR = "/var/lib/containers/storage/overlay/abcdef123456/merged"

MULTIPLE_CONTAINERS_DATA = [
    ("image1", "podman", "cid111111111", "/merged/1"),
    ("image2", "podman", "cid222222222", "/merged/2"),
    ("image3", "docker", "cid333333333", "/merged/3"),
]


def test_container_foreach_execute_inherits_from_foreach_execute():
    """Verify container_foreach_execute inherits from foreach_execute."""
    assert issubclass(container_foreach_execute, foreach_execute), \
        "container_foreach_execute must inherit from foreach_execute"


# Test datasources - defined at module level like in production
@datasource(HostContext)
def mock_single_container(broker):
    return [(SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)]


@datasource(HostContext)
def mock_multiple_containers(broker):
    return MULTIPLE_CONTAINERS_DATA


@datasource(HostContext)
def mock_empty_containers(broker):
    return []


# Define specs at module level - mimics production usage
container_rpms_single = container_foreach_execute(
    mock_single_container,
    "/usr/bin/rpm -qa --root %s",
    context=HostContext
)

container_rpms_multiple = container_foreach_execute(
    mock_multiple_containers,
    "/usr/bin/rpm -qa --root %s",
    context=HostContext
)

container_rpms_with_format = container_foreach_execute(
    mock_single_container,
    "/usr/bin/rpm -qa --root %s --qf '%%{NAME}-%%{VERSION}'",
    context=HostContext
)

container_rpms_empty = container_foreach_execute(
    mock_empty_containers,
    "/usr/bin/rpm -qa --root %s",
    context=HostContext
)

container_rpms_two_placeholders = container_foreach_execute(
    mock_single_container,
    "/usr/bin/rpm --root %s --dbpath %s",
    context=HostContext
)


def _run(spec):
    """Run spec through the framework like in production."""
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    return dr.run(dr.get_dependency_graph(spec), broker)


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_simple_substitution(mock_which, mock_bl):
    """Test basic %s substitution with merged directory path."""
    broker = _run(container_rpms_single)
    result = broker[container_rpms_single]

    assert len(result) == 1
    provider = result[0]
    assert isinstance(provider, HostBasedContainerCommandProvider)
    assert SAMPLE_MERGED_DIR in provider.cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_preserves_container_metadata(mock_which, mock_bl):
    """Test that container metadata (image, engine, container_id) is preserved."""
    broker = _run(container_rpms_single)
    result = broker[container_rpms_single]

    provider = result[0]
    assert provider.image == SAMPLE_IMAGE
    assert provider.engine == SAMPLE_ENGINE
    assert provider.container_id == SAMPLE_CID


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_passes_command_directly(mock_which, mock_bl):
    """Test that the command is substituted correctly."""
    broker = _run(container_rpms_single)
    result = broker[container_rpms_single]

    provider = result[0]
    assert provider.cmd == "/usr/bin/rpm -qa --root %s" % SAMPLE_MERGED_DIR


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_rpm_format_strings(mock_which, mock_bl):
    """Test that RPM format strings like %{NAME} are preserved."""
    broker = _run(container_rpms_with_format)
    result = broker[container_rpms_with_format]

    assert len(result) == 1
    assert SAMPLE_MERGED_DIR in result[0].cmd
    assert "%{NAME}-%{VERSION}" in result[0].cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_multiple_containers(mock_which, mock_bl):
    """Test processing multiple containers."""
    broker = _run(container_rpms_multiple)
    result = broker[container_rpms_multiple]

    assert len(result) == 3
    for i, provider in enumerate(result):
        assert provider.image == MULTIPLE_CONTAINERS_DATA[i][0]
        assert provider.engine == MULTIPLE_CONTAINERS_DATA[i][1]
        assert provider.container_id == MULTIPLE_CONTAINERS_DATA[i][2]
        assert MULTIPLE_CONTAINERS_DATA[i][3] in provider.cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_stores_original_tuple_as_args(mock_which, mock_bl):
    """Test that the original tuple is stored in args."""
    broker = _run(container_rpms_single)
    result = broker[container_rpms_single]

    entry = (SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)
    assert result[0].args == entry


def test_cfe_raises_content_exception_on_empty_source():
    """Test that ContentException is raised when no containers are provided."""
    broker = _run(container_rpms_empty)

    # When empty source, ContentException is raised and caught by the framework,
    # so the spec doesn't get added to broker
    assert container_rpms_empty not in broker


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_no_shell_wrapping(mock_which, mock_bl):
    """Verify the command is passed directly without sh -c wrapping."""
    broker = _run(container_rpms_with_format)
    result = broker[container_rpms_with_format]

    assert len(result) == 1
    assert "sh -c" not in result[0].cmd
    assert SAMPLE_MERGED_DIR in result[0].cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_not_enough_args_for_placeholders(mock_which, mock_bl):
    """Verify that ValueError is raised when command has unfilled placeholders."""
    broker = _run(container_rpms_two_placeholders)

    # When all containers fail, the spec doesn't get added to broker
    # (ValueError is caught, logged, and that container is skipped)
    assert container_rpms_two_placeholders not in broker


@datasource(HostContext)
def mock_contentprovider_source(broker):
    """Returns a ContentProvider wrapping container data (tests line 1508)."""
    return DatasourceProvider(
        content=[(SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)],
        relative_path="test/containers"
    )


@datasource(HostContext)
def mock_single_tuple_source(broker):
    """Returns a single tuple instead of list (tests line 1510)."""
    return (SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)


@datasource(HostContext)
def mock_source_raising_contentexception(broker):
    """Returns mixed valid/invalid data to trigger ContentException inside loop (tests line 1554)."""
    return [
        (SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR),
        ("invalid",),  # Will cause unpacking error -> ContentException
    ]


# Specs for additional coverage tests

container_rpms_contentprovider = container_foreach_execute(
    mock_contentprovider_source,
    "/usr/bin/rpm -qa --root %s",
    context=HostContext
)

container_rpms_single_tuple = container_foreach_execute(
    mock_single_tuple_source,
    "/usr/bin/rpm -qa --root %s",
    context=HostContext
)

container_rpms_no_placeholder = container_foreach_execute(
    mock_single_container,
    "/usr/bin/echo 'test'",  # No %s placeholder (tests line 1530)
    context=HostContext
)

container_rpms_with_contentexception = container_foreach_execute(
    mock_source_raising_contentexception,
    "/usr/bin/rpm -qa --root %s",
    context=HostContext
)


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_contentprovider_source(mock_which, mock_bl):
    """Test that ContentProvider source is unwrapped (line 1508)."""
    broker = _run(container_rpms_contentprovider)
    result = broker[container_rpms_contentprovider]

    assert len(result) == 1
    assert SAMPLE_MERGED_DIR in result[0].cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_single_tuple_source(mock_which, mock_bl):
    """Test that single tuple is wrapped in list (line 1510)."""
    broker = _run(container_rpms_single_tuple)
    result = broker[container_rpms_single_tuple]

    assert len(result) == 1
    assert result[0].image == SAMPLE_IMAGE
    assert SAMPLE_MERGED_DIR in result[0].cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/echo")
def test_cfe_command_without_placeholder(mock_which, mock_bl):
    """Test command without %s placeholder uses cmd directly (line 1530)."""
    broker = _run(container_rpms_no_placeholder)
    result = broker[container_rpms_no_placeholder]

    assert len(result) == 1
    assert result[0].cmd == "/usr/bin/echo 'test'"
    assert "%s" not in result[0].cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
@patch("insights.core.spec_factory.log")
def test_cfe_contentexception_inside_loop(mock_log, mock_which, mock_bl):
    """Test that ContentException inside loop is logged (line 1554)."""
    broker = _run(container_rpms_with_contentexception)
    result = broker[container_rpms_with_contentexception]

    # Should have 1 valid result (invalid one was skipped and logged)
    assert len(result) == 1
    assert result[0].image == SAMPLE_IMAGE

    # Verify log.debug was called for the exception
    assert mock_log.debug.called


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_cfe_nofilterexception_propagates(mock_which, mock_bl):
    """Test that NoFilterException is re-raised (line 1552)."""
    # Create a datasource that will trigger NoFilterException
    @datasource(HostContext)
    def mock_source_with_filter_issue(broker):
        return [(SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)]

    spec = container_foreach_execute(
        mock_source_with_filter_issue,
        "/usr/bin/rpm -qa --root %s",
        context=HostContext
    )

    # Mock HostBasedContainerCommandProvider to raise NoFilterException
    with patch('insights.core.spec_factory.HostBasedContainerCommandProvider') as mock_provider:
        mock_provider.side_effect = NoFilterException("Filter not matched")

        broker = dr.Broker()
        broker[HostContext] = HostContext()

        # NoFilterException should propagate (not be caught)
        result = dr.run(dr.get_dependency_graph(spec), broker)

        # Spec should not be in broker due to NoFilterException
        assert spec not in result
