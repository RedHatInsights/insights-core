# libmagic (python-magic / file-magic) was removed from this module.
#
# Security rationale: libmagic is a C library that parses untrusted binary
# content. When opened with MAGIC_CONTINUE it decompresses archives to inspect
# inner layers, exposing a large C parser to attacker-controlled bytes on every
# upload. This class of usage has led to multiple exploitable CVEs in libmagic:
#   CVE-2019-18218  stack buffer overflow in cdf_read_property_info
#   CVE-2022-48554  buffer overflow in file_copystr
#   CVE-2017-1000249 stack buffer overflow
#
# For the purpose of selecting an extractor (zip vs. tar family), reading the
# first few bytes of the file and comparing against known magic signatures is
# both safer and sufficient. No decompression, no C library, no external process.

# Signatures are checked in order; first match wins.
# Offset is the byte position within the header where the signature must appear.
_MAGIC_SIGNATURES = [
    (b"PK\x03\x04",       0,   "application/zip"),
    (b"PK\x05\x06",       0,   "application/zip"),   # empty archive
    (b"PK\x07\x08",       0,   "application/zip"),   # spanned archive
    (b"\x1f\x8b",         0,   "application/gzip"),
    (b"\xfd7zXZ\x00",     0,   "application/x-xz"),
    (b"BZh",              0,   "application/x-bzip2"),
    (b"\x28\xb5\x2f\xfd", 0,   "application/zstd"),
    (b"ustar",            257, "application/x-tar"),  # POSIX tar magic
]

# 262 bytes reaches offset 257 + len("ustar") — covers all signatures above.
_HEADER_BYTES = 262


def _detect(header):
    for sig, offset, mime in _MAGIC_SIGNATURES:
        end = offset + len(sig)
        if len(header) >= end and header[offset:end] == sig:
            return mime
    return "application/octet-stream"


def from_file(name):
    with open(name, "rb") as f:
        return _detect(f.read(_HEADER_BYTES))


def from_buffer(b):
    return _detect(b[:_HEADER_BYTES])
