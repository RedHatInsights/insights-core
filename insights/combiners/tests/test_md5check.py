import doctest
from insights.tests import context_wrap
from insights.combiners import md5check
from insights.combiners.md5check import NormalMD5
from insights.parsers.md5check import NormalMD5 as NormalMD5Parser

NORMAL_MD5_SAMPLE_1 = """
7d4855248419b8a3ce6616bbc0e58301  /etc/localtime1
""".strip()

NORMAL_MD5_SAMPLE_2 = """
d41d8cd98f00b204e9800998ecf8427e  /etc/localtime2
""".strip()


def test_normal_md5():
    parser1 = NormalMD5Parser(context_wrap(NORMAL_MD5_SAMPLE_1))
    parser2 = NormalMD5Parser(context_wrap(NORMAL_MD5_SAMPLE_2))
    md5info = NormalMD5([parser1, parser2])
    assert md5info is not None
    assert set(md5info.keys()) == set(["/etc/localtime1", "/etc/localtime2"])
    assert md5info["/etc/localtime1"] == "7d4855248419b8a3ce6616bbc0e58301"
    assert md5info["/etc/localtime2"] == "d41d8cd98f00b204e9800998ecf8427e"


def test_md5_docs():
    parser1 = NormalMD5Parser(context_wrap(NORMAL_MD5_SAMPLE_1))
    parser2 = NormalMD5Parser(context_wrap(NORMAL_MD5_SAMPLE_2))
    env = {'md5sums': NormalMD5([parser1, parser2])}
    failed, total = doctest.testmod(md5check, globs=env)
    assert failed == 0
