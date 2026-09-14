"""
Tests for the Java-library detection datasource
(:py:mod:`insights.specs.datasources.java_purls`).

These cover pom.properties / Spring-Boot SBOM parsing, purl percent-encoding, nested-jar recursion,
the fleet-scale safety caps (MAX_JARS / MAX_JAR_BYTES / MAX_NESTED_DEPTH), a real fake-``/proc``
fixture exercising the JVM-only FD walk end to end, the opt-in (off-by-default) disk scan,
skip-on-empty behavior, and the data-governance guarantees (jar basenames only, no pid / no sha1 /
no absolute paths in the emitted payload).
"""
import io
import json
import os
import zipfile

import pytest

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources import java_purls as ds


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
class _Ctx(object):
    def __init__(self, root="/"):
        self.root = root


def _broker(root="/"):
    return {HostContext: _Ctx(root)}


def _pom_props(group, artifact, version):
    return "groupId=%s\nartifactId=%s\nversion=%s\n" % (group, artifact, version)


def _make_jar(entries):
    """Build an in-memory jar (zip) from a {path: str/bytes} mapping and return the raw bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for path, content in entries.items():
            zf.writestr(path, content)
    return buf.getvalue()


def _write_jar(tmp_path, filename, entries):
    """Write a jar to disk under tmp_path and return its absolute path."""
    p = tmp_path / filename
    p.write_bytes(_make_jar(entries))
    return str(p)


def _content_str(result):
    """DatasourceProvider stores content as a list of lines; join it back for assertions."""
    return "\n".join(result.content)


# ---------------------------------------------------------------------------
# pom.properties / SBOM parsing + purl encoding
# ---------------------------------------------------------------------------
def test_parse_props_skips_blanks_and_comments():
    raw = b"# a comment\n\ngroupId=org.foo\n  artifactId = bar \nversion=1.0\nnoequals\n"
    props = ds._parse_props(raw)
    assert props == {"groupId": "org.foo", "artifactId": "bar", "version": "1.0"}


def test_pom_returns_gav_triple():
    assert ds._pom(_pom_props("org.foo", "bar", "1.2.3").encode()) == ("org.foo", "bar", "1.2.3")


def test_pom_returns_none_when_incomplete():
    assert ds._pom(b"groupId=org.foo\nartifactId=bar\n") is None
    assert ds._pom(b"") is None


def test_purl_from_pom_properties():
    data = _make_jar({"META-INF/maven/org.foo/bar/pom.properties": _pom_props("org.foo", "bar", "1.2.3")})
    out = ds._analyze("bar.jar", data=data)
    assert out == [{"purl": "pkg:maven/org.foo/bar@1.2.3", "jar": "bar.jar", "source": "pom.properties"}]


def test_purl_components_are_percent_encoded():
    # GAV values with characters reserved in a purl must be percent-encoded (never emitted raw).
    data = _make_jar({"META-INF/maven/g/a/pom.properties": _pom_props("org foo", "bar", "1.0+rh@1")})
    out = ds._analyze("weird.jar", data=data)
    assert out[0]["purl"] == "pkg:maven/org%20foo/bar@1.0%2Brh%401"


def test_purl_from_spring_boot_sbom():
    sbom = json.dumps({"components": [
        {"purl": "pkg:maven/org.foo/bar@2.0"},
        {"purl": "pkg:npm/ignored@1.0"},  # non-maven purls are ignored
        {"name": "no-purl"},
    ]})
    data = _make_jar({"META-INF/sbom/app.cdx.json": sbom})
    out = ds._analyze("app.jar", data=data)
    assert out == [{"purl": "pkg:maven/org.foo/bar@2.0", "jar": "app.jar", "source": "spring-boot-sbom"}]


def test_malformed_sbom_is_skipped_not_crashed():
    data = _make_jar({"META-INF/sbom/app.cdx.json": "{not valid json"})
    assert ds._analyze("app.jar", data=data) == []


def test_no_pom_yields_no_finding():
    # A jar with no pom.properties / SBOM resolves to nothing (no sha1 marker is emitted).
    data = _make_jar({"com/foo/Bar.class": b"cafebabe"})
    assert ds._analyze("mystery.jar", data=data) == []


def test_corrupt_jar_is_skipped_not_crashed():
    assert ds._analyze("bad.jar", data=b"not a zip") == []


# ---------------------------------------------------------------------------
# nested (fat/uber) jar recursion + depth cap
# ---------------------------------------------------------------------------
def test_nested_jar_recursion():
    inner = _make_jar({"META-INF/maven/org.inner/lib/pom.properties": _pom_props("org.inner", "lib", "3.0")})
    outer = _make_jar({"BOOT-INF/lib/inner.jar": inner, "META-INF/MANIFEST.MF": "Manifest-Version: 1.0\n"})
    out = ds._analyze("outer.jar", data=outer, depth=2)
    assert {f["purl"] for f in out} == {"pkg:maven/org.inner/lib@3.0"}


def test_max_nested_depth_stops_recursion():
    inner = _make_jar({"META-INF/maven/org.inner/lib/pom.properties": _pom_props("org.inner", "lib", "3.0")})
    outer = _make_jar({"BOOT-INF/lib/inner.jar": inner})
    # depth=0 => do not descend; outer itself has no pom -> nothing found, inner never read.
    assert ds._analyze("outer.jar", data=outer, depth=0) == []


# ---------------------------------------------------------------------------
# safety caps
# ---------------------------------------------------------------------------
def test_max_jars_cap_stops_scan(monkeypatch, tmp_path):
    monkeypatch.setattr(ds, "MAX_JARS", 1)
    j1 = _write_jar(tmp_path, "a.jar", {"META-INF/maven/g/a/pom.properties": _pom_props("g", "a", "1")})
    j2 = _write_jar(tmp_path, "b.jar", {"META-INF/maven/g/b/pom.properties": _pom_props("g", "b", "2")})
    monkeypatch.setattr(ds, "_scanned_jars", lambda root: {j1: None, j2: None})
    monkeypatch.setattr(ds, "_open_jars", lambda root: {})
    findings = json.loads(_content_str(ds.java_purls(_broker())))
    assert len(findings) == 1  # only one jar analyzed before the cap tripped


def test_max_jar_bytes_cap_skips_large_on_disk(monkeypatch, tmp_path):
    monkeypatch.setattr(ds, "MAX_JAR_BYTES", 1)  # every real jar exceeds 1 byte
    jar = _write_jar(tmp_path, "big.jar", {"META-INF/maven/g/a/pom.properties": _pom_props("g", "a", "1")})
    monkeypatch.setattr(ds, "_scanned_jars", lambda root: {jar: None})
    monkeypatch.setattr(ds, "_open_jars", lambda root: {})
    with pytest.raises(SkipComponent):
        ds.java_purls(_broker())


def test_max_jar_bytes_cap_skips_large_nested(monkeypatch):
    inner = _make_jar({"META-INF/maven/org.inner/lib/pom.properties": _pom_props("org.inner", "lib", "3.0")})
    outer = _make_jar({"BOOT-INF/lib/inner.jar": inner})
    monkeypatch.setattr(ds, "MAX_JAR_BYTES", 1)  # nested inner.jar exceeds the cap
    # Nested jar too big to read -> not analyzed -> outer has no pom -> nothing found.
    assert ds._analyze("outer.jar", data=outer, depth=2) == []


# ---------------------------------------------------------------------------
# JVM-only /proc filtering -- real fake-/proc fixture (no internal monkeypatching)
# ---------------------------------------------------------------------------
def _fake_proc(root, pid, comm=None, exe=None, fds=None):
    """Create root/proc/<pid> with comm, an exe symlink, and fd symlinks (host-absolute targets)."""
    proc = os.path.join(root, "proc", str(pid))
    os.makedirs(os.path.join(proc, "fd"))
    if comm is not None:
        with open(os.path.join(proc, "comm"), "w") as fh:
            fh.write(comm + "\n")
    if exe is not None:
        os.symlink(exe, os.path.join(proc, "exe"))
    for i, tgt in enumerate(fds or [], start=3):
        os.symlink(tgt, os.path.join(proc, "fd", str(i)))


def test_open_jars_end_to_end_fake_proc(tmp_path):
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "opt"))
    # a real jar on disk at root/opt/app.jar; the process sees it as the host path "/opt/app.jar"
    with open(os.path.join(root, "opt", "app.jar"), "wb") as fh:
        fh.write(_make_jar({"META-INF/maven/g/a/pom.properties": _pom_props("g", "a", "1")}))
    _fake_proc(root, 111, comm="java", fds=["/opt/app.jar", "/tmp/socket", "/opt/app.jar"])
    _fake_proc(root, 222, comm="nginx", fds=["/opt/app.jar"])  # not a JVM -> ignored
    seen = ds._open_jars(root)
    assert seen == {os.path.join(root, "opt", "app.jar"): "111"}


def test_is_jvm_variants(tmp_path):
    root = str(tmp_path)
    _fake_proc(root, 1, comm="java")
    _fake_proc(root, 2, comm="jsvc")                                   # Commons Daemon (Tomcat)
    _fake_proc(root, 3, comm="python", exe="/usr/lib/jvm/jre/bin/java")  # comm truncated, exe path
    _fake_proc(root, 4, comm="nginx", exe="/usr/sbin/nginx")           # not a JVM
    assert ds._is_jvm(1, root) is True
    assert ds._is_jvm(2, root) is True
    assert ds._is_jvm(3, root) is True
    assert ds._is_jvm(4, root) is False


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root bypasses DAC perms")
def test_jars_of_pid_handles_eacces(tmp_path):
    root = str(tmp_path)
    fd_dir = os.path.join(root, "proc", "9", "fd")
    os.makedirs(fd_dir)
    os.chmod(fd_dir, 0o000)  # unreadable -> PermissionError must be swallowed, not raised
    try:
        assert ds._jars_of_pid(fd_dir, root) == []
    finally:
        os.chmod(fd_dir, 0o755)


# ---------------------------------------------------------------------------
# opt-in disk scan (off by default)
# ---------------------------------------------------------------------------
def test_scanned_jars_empty_by_default(monkeypatch, tmp_path):
    monkeypatch.delenv("JAVA_PURLS_SCAN_DIRS", raising=False)
    assert ds._scanned_jars(str(tmp_path)) == {}


def test_scanned_jars_opt_in(monkeypatch, tmp_path):
    libdir = tmp_path / "opt"
    libdir.mkdir()
    _write_jar(libdir, "x.jar", {"META-INF/maven/g/a/pom.properties": _pom_props("g", "a", "1")})
    monkeypatch.setenv("JAVA_PURLS_SCAN_DIRS", str(libdir))
    found = ds._scanned_jars("/")
    assert list(found) == [os.path.realpath(str(libdir / "x.jar"))]


# ---------------------------------------------------------------------------
# datasource contract: skip-on-empty, DatasourceProvider, redaction, dedup
# ---------------------------------------------------------------------------
def test_skip_component_when_no_jars(monkeypatch):
    monkeypatch.setattr(ds, "_scanned_jars", lambda root: {})
    monkeypatch.setattr(ds, "_open_jars", lambda root: {})
    with pytest.raises(SkipComponent):
        ds.java_purls(_broker())


def test_returns_datasource_provider_with_expected_path(monkeypatch, tmp_path):
    jar = _write_jar(tmp_path, "bar.jar", {"META-INF/maven/org.foo/bar/pom.properties": _pom_props("org.foo", "bar", "1.2.3")})
    monkeypatch.setattr(ds, "_scanned_jars", lambda root: {jar: None})
    monkeypatch.setattr(ds, "_open_jars", lambda root: {})
    result = ds.java_purls(_broker())
    assert isinstance(result, DatasourceProvider)
    assert result.relative_path == "insights_datasources/java_purls.json"
    findings = json.loads(_content_str(result))
    assert findings == [{"purl": "pkg:maven/org.foo/bar@1.2.3", "jar": "bar.jar", "source": "pom.properties"}]


def test_no_pid_absolute_path_or_sha1_in_output(monkeypatch, tmp_path):
    resolved = _write_jar(tmp_path, "resolved.jar", {"META-INF/maven/g/a/pom.properties": _pom_props("g", "a", "1")})
    monkeypatch.setattr(ds, "_scanned_jars", lambda root: {})
    monkeypatch.setattr(ds, "_open_jars", lambda root: {resolved: "4242"})  # pid present internally
    result = ds.java_purls(_broker())
    findings = json.loads(_content_str(result))
    for f in findings:
        assert set(f.keys()) == {"purl", "jar", "source"}  # no 'pid', no 'sha1' key
        assert "/" not in f["jar"]                          # basename only, never an absolute path
    blob = _content_str(result)
    assert "4242" not in blob                               # the pid never leaks into the payload
    assert str(tmp_path) not in blob                        # no absolute paths leak
    assert "sha1" not in blob                               # no hash / unresolved marker


def test_dedup_collapses_duplicate_purls(monkeypatch, tmp_path):
    j1 = _write_jar(tmp_path, "one.jar", {"META-INF/maven/g/a/pom.properties": _pom_props("g", "a", "1")})
    j2 = _write_jar(tmp_path, "two.jar", {"META-INF/maven/g/a/pom.properties": _pom_props("g", "a", "1")})
    monkeypatch.setattr(ds, "_scanned_jars", lambda root: {j1: None, j2: None})
    monkeypatch.setattr(ds, "_open_jars", lambda root: {})
    findings = json.loads(_content_str(ds.java_purls(_broker())))
    assert len(findings) == 1
    assert findings[0]["purl"] == "pkg:maven/g/a@1"
