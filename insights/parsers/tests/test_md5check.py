from insights.tests import context_wrap
from insights.parsers import md5check

PRELINK_SAMPLE = """
039a62d3e9786f5a63e84def09cb3b27  /usr/lib64/libfreeblpriv3.so
""".strip()

MD5_SAMPLE = """
4777325b4a49cfae41a3991887920b68  /usr/lib64/libfreebl3.so
""".strip()

BAD_INPUT_SAMPLE = """
""".strip()

FILES_NOT_FOUND_SAMPLE = """
d41d8cd98f00b204e9800998ecf8427e  /dev/null
""".strip()


def test_md5check_prelink():
    md5info = md5check.MD5CheckSum(context_wrap(PRELINK_SAMPLE))
    assert md5info.data['md5sum'] == '039a62d3e9786f5a63e84def09cb3b27'
    assert md5info.data['filename'] == '/usr/lib64/libfreeblpriv3.so'
    assert md5info.md5sum == '039a62d3e9786f5a63e84def09cb3b27'
    assert md5info.filename == '/usr/lib64/libfreeblpriv3.so'


def test_md5check_md5():
    md5info = md5check.MD5CheckSum(context_wrap(MD5_SAMPLE))
    assert md5info.data['md5sum'] == '4777325b4a49cfae41a3991887920b68'
    assert md5info.data['filename'] == '/usr/lib64/libfreebl3.so'
    assert md5info.md5sum == '4777325b4a49cfae41a3991887920b68'
    assert md5info.filename == '/usr/lib64/libfreebl3.so'


def test_md5check_bad_input():
    md5info = md5check.MD5CheckSum(context_wrap(BAD_INPUT_SAMPLE))
    assert md5info.data == {}
    assert md5info.md5sum is None
    assert md5info.filename is None


def test_md5check_files_not_found():
    md5info = md5check.MD5CheckSum(context_wrap(FILES_NOT_FOUND_SAMPLE))
    assert md5info.data == {}
    assert md5info.md5sum is None
    assert md5info.filename is None
