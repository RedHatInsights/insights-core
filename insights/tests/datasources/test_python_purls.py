"""
Tests for the Python-library detection datasource
(:py:mod:`insights.specs.datasources.python_purls`).

These cover dist-info/METADATA + egg-info/PKG-INFO header parsing, PEP 503 name normalization, purl
percent-encoding, the header-block-only read (body is ignored), the fleet-scale safety caps
(MAX_PACKAGES / MAX_METADATA_BYTES / MAX_SECONDS), the opt-in (off-by-default) extra-dir scan,
de-duplication, skip-on-empty behavior, and the data-governance guarantee (dist-info basenames only,
no absolute paths in the emitted payload).
"""
import json
import os

import pytest

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources import python_purls as ds


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
class _Ctx(object):
    def __init__(self, root="/"):
        self.root = root


def _broker(root="/"):
    return {HostContext: _Ctx(root)}


def _write_dist_info(base, dist_dirname, name, version, extra_body="", installer=None):
    """Create a <base>/<dist_dirname>/METADATA (+ optional INSTALLER) file and return the METADATA path."""
    d = os.path.join(base, dist_dirname)
    os.makedirs(d)
    path = os.path.join(d, "METADATA")
    with open(path, "w") as fh:
        fh.write("Metadata-Version: 2.1\n")
        fh.write("Name: %s\n" % name)
        fh.write("Version: %s\n" % version)
        fh.write("Summary: a test package\n")
        fh.write("\n")  # end of headers
        fh.write(extra_body)
    if installer is not None:
        with open(os.path.join(d, "INSTALLER"), "w") as fh:
            fh.write(installer + "\n")
    return path


def _write_egg_info(base, egg_dirname, name, version):
    """Create a <base>/<egg_dirname>/PKG-INFO file and return its path."""
    d = os.path.join(base, egg_dirname)
    os.makedirs(d)
    path = os.path.join(d, "PKG-INFO")
    with open(path, "w") as fh:
        fh.write("Metadata-Version: 1.0\n")
        fh.write("Name: %s\n" % name)
        fh.write("Version: %s\n" % version)
        fh.write("\n")
    return path


@pytest.fixture
def isolated_scan(monkeypatch, tmp_path):
    """Scan ONLY the returned tmp dir (no host site-packages leakage into results)."""
    site = str(tmp_path / "site-packages")
    os.makedirs(site)
    monkeypatch.setattr(ds, "_default_site_dirs", lambda root: [])
    monkeypatch.setenv("PYTHON_PURLS_SCAN_DIRS", site)
    return site


# ---------------------------------------------------------------------------
# header reading
# ---------------------------------------------------------------------------
def test_read_headers_basic(tmp_path):
    path = _write_dist_info(str(tmp_path), "Jinja2-2.11.3.dist-info", "Jinja2", "2.11.3")
    assert ds._read_headers(path) == ("Jinja2", "2.11.3")


def test_read_headers_stops_at_body(tmp_path):
    # A "Name:"-looking line in the body must NOT be picked up.
    path = _write_dist_info(
        str(tmp_path), "Foo-1.0.dist-info", "Foo", "1.0", extra_body="Name: not-the-name\n"
    )
    assert ds._read_headers(path) == ("Foo", "1.0")


def test_read_headers_oversized_skipped(tmp_path, monkeypatch):
    path = _write_dist_info(str(tmp_path), "Big-1.0.dist-info", "Big", "1.0")
    monkeypatch.setattr(ds, "MAX_METADATA_BYTES", 1)
    assert ds._read_headers(path) == (None, None)


def test_read_headers_missing_file():
    assert ds._read_headers("/nonexistent/METADATA") == (None, None)


# ---------------------------------------------------------------------------
# normalization + encoding
# ---------------------------------------------------------------------------
def test_normalize_name():
    assert ds._normalize_name("Jinja2") == "jinja2"
    assert ds._normalize_name("ruamel.yaml") == "ruamel-yaml"
    assert ds._normalize_name("Foo__Bar--Baz") == "foo-bar-baz"
    assert ds._normalize_name("A.-_B") == "a-b"


def test_enc():
    assert ds._enc("1.0") == "1.0"
    assert ds._enc("1.0+local") == "1.0%2Blocal"


# ---------------------------------------------------------------------------
# collection
# ---------------------------------------------------------------------------
def test_collect_dist_and_egg(isolated_scan):
    _write_dist_info(isolated_scan, "Jinja2-2.11.3.dist-info", "Jinja2", "2.11.3", installer="rpm")
    _write_egg_info(isolated_scan, "Babel-2.9.1.egg-info", "Babel", "2.9.1")
    out = ds._collect(ds._scan_dirs("/"))
    purls = sorted(f["purl"] for f in out)
    assert purls == ["pkg:pypi/babel@2.9.1", "pkg:pypi/jinja2@2.11.3"]
    by_purl = {f["purl"]: f for f in out}
    assert by_purl["pkg:pypi/jinja2@2.11.3"]["source"] == "dist-info"
    assert by_purl["pkg:pypi/jinja2@2.11.3"]["dist"] == "Jinja2-2.11.3.dist-info"
    # INSTALLER marker read from the dist-info dir
    assert by_purl["pkg:pypi/jinja2@2.11.3"]["installer"] == "rpm"
    assert by_purl["pkg:pypi/babel@2.9.1"]["source"] == "egg-info"
    # egg-info has no INSTALLER marker
    assert by_purl["pkg:pypi/babel@2.9.1"]["installer"] is None


def test_installer_absent_is_none(isolated_scan):
    _write_dist_info(isolated_scan, "Foo-1.0.dist-info", "Foo", "1.0")  # no INSTALLER
    out = ds._collect(ds._scan_dirs("/"))
    assert out[0]["installer"] is None


def test_read_installer_oversized_ignored(tmp_path):
    d = os.path.join(str(tmp_path), "Big-1.0.dist-info")
    os.makedirs(d)
    with open(os.path.join(d, "INSTALLER"), "w") as fh:
        fh.write("x" * 500)
    assert ds._read_installer(d) is None


def test_read_installer_missing_dir():
    assert ds._read_installer("/nonexistent") is None


def test_collect_skips_missing_headers(isolated_scan):
    d = os.path.join(isolated_scan, "Broken-0.dist-info")
    os.makedirs(d)
    with open(os.path.join(d, "METADATA"), "w") as fh:
        fh.write("Metadata-Version: 2.1\nSummary: no name or version\n\n")
    assert ds._collect(ds._scan_dirs("/")) == []


def test_collect_respects_max_packages(isolated_scan, monkeypatch):
    for i in range(5):
        _write_dist_info(isolated_scan, "Pkg%d-1.0.dist-info" % i, "Pkg%d" % i, "1.0")
    monkeypatch.setattr(ds, "MAX_PACKAGES", 2)
    assert len(ds._collect(ds._scan_dirs("/"))) == 2


def test_collect_respects_deadline(isolated_scan, monkeypatch):
    for i in range(3):
        _write_dist_info(isolated_scan, "Pkg%d-1.0.dist-info" % i, "Pkg%d" % i, "1.0")
    monkeypatch.setattr(ds, "MAX_SECONDS", -1)  # already past the budget before the first file
    assert ds._collect(ds._scan_dirs("/")) == []


# ---------------------------------------------------------------------------
# dedup
# ---------------------------------------------------------------------------
def test_dedup_preserves_first_seen():
    rows = [
        {"purl": "pkg:pypi/a@1"},
        {"purl": "pkg:pypi/a@1"},
        {"purl": "pkg:pypi/b@2"},
        {"purl": None},
    ]
    uniq = ds._dedup(rows)
    assert [r["purl"] for r in uniq] == ["pkg:pypi/a@1", "pkg:pypi/b@2"]


# ---------------------------------------------------------------------------
# full datasource
# ---------------------------------------------------------------------------
def test_datasource_end_to_end(isolated_scan):
    _write_dist_info(isolated_scan, "Jinja2-2.11.3.dist-info", "Jinja2", "2.11.3")
    _write_egg_info(isolated_scan, "Babel-2.9.1.egg-info", "Babel", "2.9.1")
    result = ds.python_purls(_broker())
    assert isinstance(result, DatasourceProvider)
    assert result.relative_path == "insights_datasources/python_purls.json"
    payload = json.loads("".join(result.content))
    purls = sorted(f["purl"] for f in payload)
    assert purls == ["pkg:pypi/babel@2.9.1", "pkg:pypi/jinja2@2.11.3"]
    # data governance: never an absolute path in the payload (dist basenames only)
    for f in payload:
        assert not os.path.isabs(f["dist"])
        assert os.sep not in f["dist"]


def test_datasource_skips_when_empty(isolated_scan):
    with pytest.raises(SkipComponent):
        ds.python_purls(_broker())


def test_opt_in_scan_dirs_off_by_default(monkeypatch, tmp_path):
    # With no PYTHON_PURLS_SCAN_DIRS set and defaults stubbed out, nothing is scanned.
    monkeypatch.setattr(ds, "_default_site_dirs", lambda root: [])
    monkeypatch.delenv("PYTHON_PURLS_SCAN_DIRS", raising=False)
    assert ds._scan_dirs("/") == []


class TestDefensiveBranches:
    def test_read_headers_unreadable_path(self, tmp_path):
        # getsize succeeds but open() fails (a directory raises IsADirectoryError/OSError) -> (None, None)
        assert ds._read_headers(str(tmp_path)) == (None, None)

    def test_read_headers_name_without_version(self, tmp_path):
        p = tmp_path / "m"
        p.write_text("Name: solo\nSummary: no version and no blank line")
        assert ds._read_headers(str(p)) == ("solo", None)  # loop exits at EOF, not via blank-line break

    def test_default_site_dirs_identity_root(self):
        dirs = ds._default_site_dirs("/")
        assert any("site-packages" in d for d in dirs)
        assert all(not d.startswith("/fakeroot") for d in dirs)

    def test_default_site_dirs_under_nonroot(self):
        dirs = ds._default_site_dirs("/fakeroot")
        # every entry is re-rooted under the context root (no bare absolute escapes)
        assert dirs and all(d.startswith("/fakeroot") for d in dirs)
