import os

import pytest
from unittest.mock import MagicMock, patch

from insights.core.exceptions import ContentException
from insights.core.spec_factory import (
    CommandOutputProvider,
    HostBasedContainerCommandProvider,
    container_foreach_execute,
)
from insights.util.mangle import mangle_command


MOCK_WHICH = "insights.core.spec_factory.which"
MOCK_BLACKLIST = "insights.core.spec_factory.blacklist.allow_command"

SAMPLE_CMD = 'sh -c "command -v /usr/bin/rpm > /dev/null && /usr/bin/rpm -qa --root /var/lib/containers/overlay/merged"'
SAMPLE_IMAGE = "registry.access.redhat.com/ubi8/ubi:latest"
SAMPLE_ENGINE = "podman"
SAMPLE_CID = "abc123def456"
SAMPLE_MERGED_DIR = "/var/lib/containers/storage/overlay/abcdef123456/merged"


def _make_ctx():
    ctx = MagicMock()
    ctx.__class__ = type("FakeCtx", (), {})
    return ctx


# --- HostBasedContainerCommandProvider ---

@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_host_provider_stores_metadata(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    assert provider.image == SAMPLE_IMAGE
    assert provider.engine == SAMPLE_ENGINE
    assert provider.container_id == SAMPLE_CID


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_host_provider_relative_path(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    expected = os.path.join(SAMPLE_CID, "insights_commands", mangle_command(SAMPLE_CMD))
    assert provider.relative_path == expected


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_host_provider_root_is_insights_containers(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    assert provider.root == "insights_containers"


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_host_provider_inherits_command_output_provider(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    assert isinstance(provider, CommandOutputProvider)


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_host_provider_repr(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    r = repr(provider)
    assert r.startswith('HostBasedContainerCommandProvider(')
    assert SAMPLE_CMD in r


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_host_provider_defaults_none_image_engine(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(), container_id=SAMPLE_CID,
    )
    assert provider.image is None
    assert provider.engine is None


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_host_provider_requires_container_id_for_path(mock_which, mock_bl):
    with pytest.raises(TypeError):
        HostBasedContainerCommandProvider(SAMPLE_CMD, _make_ctx())


# --- container_foreach_execute ---

def _make_cfe(cmd="/usr/bin/rpm -qa --root %s"):
    """Create a container_foreach_execute instance with a mock provider."""
    mock_provider = MagicMock()
    mock_provider.__name__ = "mock_provider"
    cfe = object.__new__(container_foreach_execute)
    cfe.provider = mock_provider
    cfe.cmd = cmd
    cfe.context = MagicMock()
    cfe.split = True
    cfe.raw = False
    cfe.keep_rc = False
    cfe.timeout = None
    cfe.inherit_env = []
    cfe.override_env = {}
    cfe.signum = None
    return cfe


def _make_broker(cfe, source, ctx=None):
    """Build a mock broker dict for container_foreach_execute.__call__."""
    if ctx is None:
        ctx = _make_ctx()
    broker = MagicMock()
    broker.__getitem__ = lambda self, key: {
        cfe.provider: source,
        cfe.context: ctx,
    }[key]
    broker.get = lambda key, default=None: None
    return broker


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_cfe_simple_substitution(mock_which, mock_bl):
    cfe = _make_cfe("/usr/bin/rpm -qa --root %s")
    source = [(SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)]
    broker = _make_broker(cfe, source)

    result = cfe(broker)
    assert len(result) == 1
    provider = result[0]
    assert isinstance(provider, HostBasedContainerCommandProvider)
    assert SAMPLE_MERGED_DIR in provider.cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_cfe_preserves_container_metadata(mock_which, mock_bl):
    cfe = _make_cfe("/usr/bin/rpm -qa --root %s")
    source = [(SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)]
    broker = _make_broker(cfe, source)

    result = cfe(broker)
    provider = result[0]
    assert provider.image == SAMPLE_IMAGE
    assert provider.engine == SAMPLE_ENGINE
    assert provider.container_id == SAMPLE_CID


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_cfe_wraps_with_command_v(mock_which, mock_bl):
    cfe = _make_cfe("/usr/bin/rpm -qa --root %s")
    source = [(SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)]
    broker = _make_broker(cfe, source)

    result = cfe(broker)
    provider = result[0]
    assert provider.cmd.startswith('sh -c "command -v /usr/bin/rpm')
    assert '> /dev/null &&' in provider.cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_cfe_rpm_format_fallback(mock_which, mock_bl):
    rpm_format = "%{NAME}-%{VERSION}"
    cmd = "/usr/bin/rpm -qa --root %%s --qf '%s'" % rpm_format
    cfe = _make_cfe(cmd)
    source = [(SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)]
    broker = _make_broker(cfe, source)

    result = cfe(broker)
    assert len(result) == 1
    assert SAMPLE_MERGED_DIR in result[0].cmd
    assert rpm_format in result[0].cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_cfe_multiple_containers(mock_which, mock_bl):
    cfe = _make_cfe("/usr/bin/rpm -qa --root %s")
    source = [
        ("image1", "podman", "cid111111111", "/merged/1"),
        ("image2", "podman", "cid222222222", "/merged/2"),
        ("image3", "docker", "cid333333333", "/merged/3"),
    ]
    broker = _make_broker(cfe, source)

    result = cfe(broker)
    assert len(result) == 3
    for i, provider in enumerate(result):
        assert provider.image == source[i][0]
        assert provider.engine == source[i][1]
        assert provider.container_id == source[i][2]
        assert source[i][3] in provider.cmd


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_cfe_stores_original_tuple_as_args(mock_which, mock_bl):
    cfe = _make_cfe("/usr/bin/rpm -qa --root %s")
    entry = (SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)
    source = [entry]
    broker = _make_broker(cfe, source)

    result = cfe(broker)
    assert result[0].args == entry


def test_cfe_raises_content_exception_on_empty_source():
    cfe = _make_cfe("/usr/bin/rpm -qa --root %s")
    broker = _make_broker(cfe, [])

    with pytest.raises(ContentException):
        cfe(broker)


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/sh")
def test_cfe_format_used_not_percent(mock_which, mock_bl):
    """Verify .format() is used for wrapping (not %s), which avoids crashes with rpm specifiers."""
    cfe = _make_cfe("/usr/bin/rpm -qa --root %s --qf '%{NAME}'")
    source = [(SAMPLE_IMAGE, SAMPLE_ENGINE, SAMPLE_CID, SAMPLE_MERGED_DIR)]
    broker = _make_broker(cfe, source)

    result = cfe(broker)
    assert len(result) == 1
    assert "command -v /usr/bin/rpm > /dev/null" in result[0].cmd
