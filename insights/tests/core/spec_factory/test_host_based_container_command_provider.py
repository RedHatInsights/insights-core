import os

import pytest
from unittest.mock import MagicMock, patch

from insights.core.spec_factory import (
    CommandOutputProvider,
    HostBasedContainerCommandProvider,
)
from insights.util.mangle import mangle_command


MOCK_WHICH = "insights.core.spec_factory.which"
MOCK_BLACKLIST = "insights.core.spec_factory.blacklist.allow_command"

SAMPLE_CMD = "/usr/bin/rpm -qa --root /var/lib/containers/overlay/merged"
SAMPLE_IMAGE = "registry.access.redhat.com/ubi8/ubi:latest"
SAMPLE_ENGINE = "podman"
SAMPLE_CID = "abc123def456"


def _make_ctx():
    ctx = MagicMock()
    ctx.__class__ = type("FakeCtx", (), {})
    return ctx


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_host_provider_stores_metadata(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    assert provider.image == SAMPLE_IMAGE
    assert provider.engine == SAMPLE_ENGINE
    assert provider.container_id == SAMPLE_CID


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_host_provider_relative_path(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    expected = os.path.join(SAMPLE_CID, "insights_commands", mangle_command(SAMPLE_CMD))
    assert provider.relative_path == expected


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_host_provider_root_is_insights_containers(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    assert provider.root == "insights_containers"


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_host_provider_inherits_command_output_provider(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    assert isinstance(provider, CommandOutputProvider)


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_host_provider_repr(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(),
        image=SAMPLE_IMAGE, engine=SAMPLE_ENGINE, container_id=SAMPLE_CID,
    )
    assert repr(provider) == f"HostBasedContainerCommandProvider('{SAMPLE_CMD}')"


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_host_provider_defaults_none_image_engine(mock_which, mock_bl):
    provider = HostBasedContainerCommandProvider(
        SAMPLE_CMD, _make_ctx(), container_id=SAMPLE_CID,
    )
    assert provider.image is None
    assert provider.engine is None


@patch(MOCK_BLACKLIST, return_value=True)
@patch(MOCK_WHICH, return_value="/usr/bin/rpm")
def test_host_provider_requires_container_id_for_path(mock_which, mock_bl):
    with pytest.raises(TypeError):
        HostBasedContainerCommandProvider(SAMPLE_CMD, _make_ctx())
