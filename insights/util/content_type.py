# libmagic (python-magic / file-magic) was removed from this module.
#
# Security rationale: libmagic is a C library that parses untrusted binary
# content. It loads its full magic database and, with MAGIC_CONTINUE, runs the
# complete set of tests and accumulates every match — exposing a large C parser
# to attacker-controlled bytes on every upload. This class of parsing has led to
# multiple exploitable CVEs in libmagic:
#   CVE-2019-18218  stack buffer overflow in cdf_read_property_info
#   CVE-2022-48554  buffer overflow in file_copystr
#   CVE-2017-1000249 stack buffer overflow
#
# Memory / performance: loading the magic database and running the full test
# suite (MAGIC_CONTINUE) against every uploaded file accounted for a large share
# of heap allocation in profiling. The header-signature approach below reads a
# fixed 262 bytes and runs a handful of byte comparisons, so per-call work and
# allocation are effectively constant and negligible.
#
# For the purpose of selecting an extractor (zip vs. tar family), reading the
# first few bytes of the file and comparing against known magic signatures is
# both safer and sufficient: no C library and no external process.

# Signatures are checked in order; first match wins.
# Offset is the byte position within the header where the signature must appear.
_MAGIC_SIGNATURES = [
    (b"PK\x03\x04", 0, "application/zip"),
    (b"PK\x05\x06", 0, "application/zip"),  # empty archive
    (b"PK\x07\x08", 0, "application/zip"),  # spanned archive
    (b"\x1f\x8b\x08", 0, "application/gzip"),  # gzip magic + DEFLATE method byte
    (b"\xfd7zXZ\x00", 0, "application/x-xz"),
    # Compressed tarballs (.tar.gz/.tar.xz/.tar.bz2 — the common insights archive
    # format) match their outer compression magic at offset 0 above; this ustar
    # entry only catches an *uncompressed* .tar.
    (b"ustar", 257, "application/x-tar"),  # POSIX tar magic
]

# 262 bytes reaches offset 257 + len("ustar") — covers all signatures above.
_HEADER_BYTES = 262

# Valid bzip2 block-size digits ('1'-'9'); handled outside the fixed-signature
# table because the digit varies. Matching "BZh" alone is too loose — any file
# starting with those three bytes would be misrouted to the tar extractor.
_BZIP2_BLOCK_SIZES = b"123456789"


def _detect(header):
    for sig, offset, mime in _MAGIC_SIGNATURES:
        end = offset + len(sig)
        if len(header) >= end and header[offset:end] == sig:
            return mime
    # bzip2: "BZh" followed by a block-size digit ('1'-'9').
    if len(header) >= 4 and header[:3] == b"BZh" and header[3:4] in _BZIP2_BLOCK_SIZES:
        return "application/x-bzip2"
    return "application/octet-stream"


def from_file(name):
    with open(name, "rb") as f:
        return _detect(f.read(_HEADER_BYTES))


def from_buffer(b):
    return _detect(b[:_HEADER_BYTES])
