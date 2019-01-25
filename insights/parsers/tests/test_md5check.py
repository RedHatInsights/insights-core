from insights.tests import context_wrap
from insights.parsers import md5check
from insights.parsers import ParseException
import pytest

NORMAL_MD5_SAMPLE = """
d41d8cd98f00b204e9800998ecf8427e  /dev/null
7d4855248419b8a3ce6616bbc0e58301  /etc/localtime
910c11e6b93ae222b44143cb14f2b670  /usr/share/zoneinfo/America/Sao_Paulo
96db70199bdca045254f321a5e06d7b9  /usr/share/zoneinfo/America/Campo_Grande
ddc716ed2eac2ebfab07db289dd4270d  /usr/share/zoneinfo/America/Cuiaba
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

ONLY_NULL_SAMPLE = """
d41d8cd98f00b204e9800998ecf8427e  /dev/null
""".strip()

PRELINK_SAMPLE = """
b4949565c561187ebc69d21cf20b0207  /etc/pki/product/69.pem
""".strip()


def test_normal_md5():
    md5info = md5check.NormalMD5(context_wrap(NORMAL_MD5_SAMPLE))
    assert "/dev/null" not in md5info.files
    assert "/etc/localtime" in md5info.files
    assert "/usr/share/zoneinfo/America/Sao_Paulo" in md5info.files
    assert md5info['/etc/localtime'] == "7d4855248419b8a3ce6616bbc0e58301"
    assert md5info.get('/etc/hostname') is None
    assert "/etc/hostname" not in md5info.files


def test_normal_md5_blank_input():
    ctx = context_wrap(BLANK_INPUT_SAMPLE)
    with pytest.raises(ParseException) as sc:
        md5check.NormalMD5(ctx)
    assert "Input content is empty." in str(sc)


def test_normal_md5_bad_input():
    md5info = md5check.NormalMD5(context_wrap(BAD_INPUT_SAMPLE))
    assert md5info.data == {}
    assert md5info.files == []


def test_normal_md5_only_null():
    md5info = md5check.NormalMD5(context_wrap(ONLY_NULL_SAMPLE))
    assert md5info.data == {}
    assert md5info.files == []


def test_normal_md5_bad_mix():
    md5info = md5check.NormalMD5(context_wrap(BAD_INPUT_MIX))
    assert md5info.data == {}
    assert md5info.files == []


def test_prelink_md5():
    md5info = md5check.PrelinkMD5(context_wrap(PRELINK_SAMPLE))
    assert "/etc/pki/product/69.pem" in md5info.files
    assert md5info['/etc/pki/product/69.pem'] == "b4949565c561187ebc69d21cf20b0207"
