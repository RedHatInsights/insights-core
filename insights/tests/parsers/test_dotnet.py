import doctest
import pytest

from insights.core.exceptions import ContentException, ParseException, SkipComponent
from insights.parsers import dotnet
from insights.parsers.dotnet import DotNetVersion, ContainerDotNetVersion
from insights.tests import context_wrap

dotnet_version_1 = "3.1.108"
dotnet_version_2 = "2.1.518"
dotnet_version_3 = """
-bash: /usr/bin/dotnet: No such file or directory
""".strip()
dotnet_version_4 = "2."
dotnet_version_5 = """
abc
-bash: /usr/bin/dotnet: No such file or directory
"""


def test_dotnet_version():
    ret = DotNetVersion(context_wrap(dotnet_version_1))
    assert ret.major == 3
    assert ret.minor == 1
    assert ret.raw == dotnet_version_1

    ret = DotNetVersion(context_wrap(dotnet_version_2))
    assert ret.major == 2
    assert ret.minor == 1
    assert ret.raw == dotnet_version_2


def test_dotnet_version_ab():
    with pytest.raises(ContentException):
        ret = DotNetVersion(context_wrap(dotnet_version_3))
        assert ret is None

    with pytest.raises(ParseException) as pe:
        ret = DotNetVersion(context_wrap(dotnet_version_4))
        assert ret is None
        assert "Unrecognized version" in str(pe)

    with pytest.raises(SkipComponent):
        ret = DotNetVersion(context_wrap(dotnet_version_5))
        assert ret is None


def test_container_dotnet_version():
    ret = ContainerDotNetVersion(
        context_wrap(
            dotnet_version_1,
            container_id='cc2883a1a369',
            image='quay.io/rhel8',
            engine='podman'
        )
    )
    assert ret.major == 3
    assert ret.minor == 1
    assert ret.raw == dotnet_version_1
    assert ret.image == "quay.io/rhel8"
    assert ret.engine == "podman"
    assert ret.container_id == "cc2883a1a369"


def test_container_dotnet_version_error():
    with pytest.raises(ContentException):
        ret = ContainerDotNetVersion(
            context_wrap(
                dotnet_version_3,
                container_id='cc2883a1a369',
                image='quay.io/rhel8',
                engine='podman'
            )
        )
        assert ret is None


def test_doc_examples():
    env = {
        'dotnet_ver': DotNetVersion(context_wrap(dotnet_version_1)),
        'con_dotnet_ver': ContainerDotNetVersion(
            context_wrap(
                dotnet_version_1,
                container_id='cc2883a1a369',
                image='quay.io/rhel8',
                engine='podman'
            )
        )
    }
    failed, total = doctest.testmod(dotnet, globs=env)
    assert failed == 0
