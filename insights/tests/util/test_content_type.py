import tempfile

import pytest

from insights.core.archives import TarExtractor
from insights.util.content_type import from_buffer, from_file


# A real POSIX tar header carries the "ustar" magic at offset 257.
def _tar_header():
    return b"\x00" * 257 + b"ustar" + b"\x00" * (512 - 262)


DETECTION_CASES = [
    (b"PK\x03\x04rest-of-file", "application/zip"),
    (b"PK\x05\x06", "application/zip"),                 # empty archive
    (b"PK\x07\x08", "application/zip"),                 # spanned archive
    (b"\x1f\x8b\x08\x00", "application/gzip"),
    (b"\x1f\x8b\x00", "application/octet-stream"),      # gzip magic, wrong method
    (b"\x1f\x8b", "application/octet-stream"),          # gzip magic, no method byte
    (b"\xfd7zXZ\x00", "application/x-xz"),
    (b"BZh91AY", "application/x-bzip2"),
    (b"BZh1", "application/x-bzip2"),                   # minimal valid bzip2 prefix
    (b"BZh0", "application/octet-stream"),              # invalid block-size digit
    (b"BZhx", "application/octet-stream"),              # non-digit block size
    (b"BZh", "application/octet-stream"),               # no block-size digit
    (b"\x28\xb5\x2f\xfd", "application/octet-stream"),  # zstd is not supported
    (_tar_header(), "application/x-tar"),
    (b"not an archive at all", "application/octet-stream"),
    (b"", "application/octet-stream"),                  # too short to match
    (b"PK", "application/octet-stream"),                # partial zip magic
]


@pytest.mark.parametrize("data, expected", DETECTION_CASES)
def test_from_buffer(data, expected):
    assert from_buffer(data) == expected


@pytest.mark.parametrize("data, expected", DETECTION_CASES)
def test_from_file(data, expected):
    with tempfile.NamedTemporaryFile() as tf:
        tf.write(data)
        tf.flush()
        assert from_file(tf.name) == expected


def test_detection_stays_aligned_with_extraction():
    """
    Every content type the detector can return must be extractable: either the
    zip special case in archives.extract() or a key in TarExtractor.TAR_FLAGS.
    Guards against reintroducing a detect-but-fail type.
    """
    for _, expected in DETECTION_CASES:
        if expected == "application/octet-stream":
            continue
        assert (
            expected == "application/zip"
            or expected in TarExtractor.TAR_FLAGS
        ), "%s is detected but not extractable" % expected
