import doctest
import pytest
from insights.parsers import dotnet
from insights.core.plugins import ContentException
from insights.parsers import SkipException, ParseException
from insights.parsers.dotnet import DotNetVersion
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

    with pytest.raises(SkipException):
        ret = DotNetVersion(context_wrap(dotnet_version_5))
        assert ret is None


def test_doc_examples():
    env = {
        'dotnet_ver': DotNetVersion(context_wrap(dotnet_version_1))
    }
    failed, total = doctest.testmod(dotnet, globs=env)
    assert failed == 0
