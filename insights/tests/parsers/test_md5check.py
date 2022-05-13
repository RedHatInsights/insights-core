import doctest
import pytest
from insights.tests import context_wrap
from insights.parsers import md5check
from insights.parsers import ParseException

NORMAL_MD5_SAMPLE = """
7d4855248419b8a3ce6616bbc0e58301  /etc/localtime
""".strip()

BAD_INPUT_SAMPLE = """
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  /dev/null
""".strip()

BAD_INPUT_MIX = """
d41d8cd98f00b204e9800998ecf8427e  /dev/null
/usr/bin/md5sum: /etc/pki/product/69.pem: No such file or directory
/usr/bin/md5sum: /etc/pki/product-default/69.pem: No such file or directory
""".strip()

BLANK_INPUT_SAMPLE = """
""".strip()


def test_normal_md5():
    md5info = md5check.NormalMD5(context_wrap(NORMAL_MD5_SAMPLE))
    assert md5info is not None
    assert md5info.filename == "/etc/localtime"
    assert md5info.md5sum == "7d4855248419b8a3ce6616bbc0e58301"


def test_normal_md5_blank_input():
    ctx = context_wrap(BLANK_INPUT_SAMPLE)
    with pytest.raises(ParseException) as sc:
        md5check.NormalMD5(ctx)
    assert "Incorrect length for input" in str(sc)


def test_normal_md5_bad_input():
    ctx = context_wrap(BAD_INPUT_SAMPLE)
    with pytest.raises(ParseException) as sc:
        md5check.NormalMD5(ctx)
    assert "Invalid MD5sum value" in str(sc)


def test_normal_md5_bad_mix():
    ctx = context_wrap(BAD_INPUT_MIX)
    with pytest.raises(ParseException) as sc:
        md5check.NormalMD5(ctx)
    assert "Incorrect length for input" in str(sc)


def test_md5_docs():
    env = {'md5info': md5check.NormalMD5(context_wrap(NORMAL_MD5_SAMPLE))}
    failed, total = doctest.testmod(md5check, globs=env)
    assert failed == 0
