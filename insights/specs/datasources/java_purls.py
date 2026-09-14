"""
Custom datasource: third-party Java library detection
=====================================================

Detects third-party Java libraries *loaded by running JVMs* on the host and emits their package
URLs (purls) into the standard insights archive, so puptoo can map them into
``system_profile.java_purls`` for downstream CVE matching.

Runs as part of the DEFAULT collection (a normal ``insights-client`` run) and is applicability-gated:
if no Java libraries are found it raises ``SkipComponent`` and contributes nothing.

Detection (cheapest first):
  * running JVMs -- jars held open via ``/proc/<pid>/fd`` (only Java processes are inspected). This
    is the default and is cheap: hosts with no JVM skip instantly.
  * OPTIONAL disk scan -- only when ``JAVA_PURLS_SCAN_DIRS`` is explicitly set (comma-separated dirs,
    e.g. ``/opt``). There is no default disk scan: a recursive walk of distro dirs (``/usr/lib``,
    ``/var/lib``) is expensive at fleet scale and those jars are already covered by ``installed_rpms``.
  * inside each jar: ``META-INF/maven/**/pom.properties`` (authoritative g:a:v) and Spring-Boot
    ``META-INF/sbom/*.cdx.json``; bounded recursion into fat/uber jar ``BOOT-INF/lib`` etc.

Because this runs in default collection at fleet scale it enforces a safety envelope: JVM-only
``/proc`` walk, caps on the number/size/nesting of jars analyzed, streaming reads, and graceful
partial results (never a crash) when a cap or the datasource timeout is hit.

Only authoritative purls resolved *locally* (pom.properties / SBOM) are emitted -- never a hash and
never a network call. Shaded / no-pom jars that cannot be resolved on-box are simply omitted; server
-side ``sha1 -> GAV`` resolution is a separate, future step and is intentionally not represented here.

Output: a JSON array of ``{purl, jar, source}`` objects at
``data/insights_datasources/java_purls.json`` (jar is a basename only; no path/pid/hash).
"""
import glob
import io
import json
import logging
import os
import zipfile

try:
    from urllib.parse import quote
except ImportError:  # pragma: no cover - py2 fallback
    from urllib import quote

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider

logger = logging.getLogger(__name__)

NESTED_PREFIXES = ("BOOT-INF/lib/", "WEB-INF/lib/", "lib/")
RELATIVE_PATH = "insights_datasources/java_purls.json"

# comm/exe basenames treated as a JVM. Bounded on purpose: this is a "loaded-library" inventory of
# ordinary JVMs, not a claim to find every possible launcher. (jsvc = Commons Daemon, used by Tomcat.)
JVM_NAMES = ("java", "jsvc")


def _int_env(name, default):
    """Read a positive int cap from the environment, falling back to the default on absent/garbage."""
    try:
        return int(os.environ[name])
    except (KeyError, ValueError, TypeError):
        return default


# Fleet-scale safety caps (module constants, overridable via env). Hitting any cap stops the scan
# cleanly and emits the partial results collected so far rather than crashing.
MAX_JARS = _int_env("JAVA_PURLS_MAX_JARS", 2000)                 # total jars analyzed (incl. nested)
MAX_JAR_BYTES = _int_env("JAVA_PURLS_MAX_JAR_BYTES", 64 * 1024 * 1024)  # skip jars larger than this
MAX_NESTED_DEPTH = _int_env("JAVA_PURLS_MAX_NESTED_DEPTH", 2)    # fat-jar recursion depth


def _enc(component):
    """Percent-encode one purl component per the purl spec (leaves unreserved chars alone)."""
    return quote(component, safe="")


def _parse_props(raw):
    """Parse ``key=value`` lines (skipping blanks/comments) into a dict."""
    props = {}
    for line in raw.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        props[k.strip()] = v.strip()
    return props


def _pom(raw):
    """Return the (groupId, artifactId, version) triple from a pom.properties body, or None."""
    props = _parse_props(raw)
    g, a, v = props.get("groupId"), props.get("artifactId"), props.get("version")
    if g and a and v:
        return g, a, v
    return None


def _purls_from_pom(zf, entry, name):
    """Authoritative purl(s) from a ``META-INF/maven/**/pom.properties`` entry (may be empty)."""
    gav = _pom(zf.read(entry))
    if not gav:
        return []
    g, a, v = gav
    purl = "pkg:maven/%s/%s@%s" % (_enc(g), _enc(a), _enc(v))
    return [{"purl": purl, "jar": name, "source": "pom.properties"}]


def _purls_from_sbom(zf, entry, name):
    """purl(s) from a Spring-Boot ``META-INF/sbom/*.cdx.json`` entry (best-effort, may be empty)."""
    found = []
    try:
        for c in json.loads(zf.read(entry)).get("components", []):
            if c.get("purl", "").startswith("pkg:maven/"):
                found.append({"purl": c["purl"], "jar": name, "source": "spring-boot-sbom"})
    except Exception as e:
        logger.debug("java_purls: SBOM parse failed for %s in %s: %s", entry, name, e)
    return found


def _collect_purls(zf, names, name, out):
    """Append authoritative purls (pom.properties + Spring-Boot SBOM) found in one jar."""
    for n in names:
        if n.startswith("META-INF/maven/") and n.endswith("pom.properties"):
            out.extend(_purls_from_pom(zf, n, name))
        elif n.startswith("META-INF/sbom/") and n.endswith(".cdx.json"):
            out.extend(_purls_from_sbom(zf, n, name))


def _recurse_nested(zf, names, depth, out, counter):
    """Recurse into fat/uber-jar nested jars (``BOOT-INF/lib`` etc.), respecting caps."""
    for n in names:
        if counter["n"] >= MAX_JARS:
            break
        if not (n.endswith(".jar") and any(n.startswith(p) for p in NESTED_PREFIXES)):
            continue
        try:
            # Skip oversized nested jars without reading them into memory.
            if zf.getinfo(n).file_size > MAX_JAR_BYTES:
                continue
            _analyze(n.split("/")[-1], data=zf.read(n), depth=depth - 1,
                     out=out, counter=counter)
        except Exception as e:
            logger.debug("java_purls: nested jar %s skipped: %s", n, e)
            continue


def _analyze(name, data=None, path=None, depth=MAX_NESTED_DEPTH, out=None, counter=None):
    if out is None:
        out = []
    if counter is None:
        counter = {"n": 0}
    # Stop cleanly once the total-jars cap is reached (partial results, not a crash).
    if counter["n"] >= MAX_JARS:
        return out
    counter["n"] += 1
    try:
        # Passing ``path`` (not raw bytes) lets zipfile read the central directory without slurping
        # the whole jar into memory. Only nested jars are read as bytes (already bounded above).
        # Context manager guarantees the handle is closed even if reading an entry raises.
        with zipfile.ZipFile(io.BytesIO(data) if data is not None else path) as zf:
            names = zf.namelist()
            _collect_purls(zf, names, name, out)
            if depth > 0:
                _recurse_nested(zf, names, depth, out, counter)
    except Exception as e:
        logger.debug("java_purls: could not analyze %s: %s", name, e)
    return out


def _is_jvm(pid, root):
    """True only if /proc/<pid> is a JVM (comm or exe basename in ``JVM_NAMES``)."""
    proc = os.path.join(root, "proc", str(pid))
    try:
        with open(os.path.join(proc, "comm")) as fh:
            if fh.read().strip() in JVM_NAMES:
                return True
    except (PermissionError, FileNotFoundError, ProcessLookupError, OSError):
        pass
    try:
        exe = os.readlink(os.path.join(proc, "exe"))
        if os.path.basename(exe) in JVM_NAMES or "/jre/" in exe or "/jdk" in exe:
            return True
    except (PermissionError, FileNotFoundError, ProcessLookupError, OSError):
        pass
    return False


def _under_root(root, tgt):
    """Resolve a /proc fd link target against the context root (identity when root is '/')."""
    if root in ("/", "", None):
        return tgt
    return os.path.join(root, tgt.lstrip("/"))


def _jars_of_pid(fd_dir, root):
    """Absolute paths of .jar files held open by one process, via its ``/proc/<pid>/fd`` dir."""
    jars = []
    try:
        for fd in os.listdir(fd_dir):
            try:
                tgt = _under_root(root, os.readlink(os.path.join(fd_dir, fd)))
            except OSError:
                continue
            if tgt.endswith(".jar") and os.path.exists(tgt):
                jars.append(tgt)
    except (PermissionError, FileNotFoundError, ProcessLookupError) as e:
        logger.debug("java_purls: cannot read %s: %s", fd_dir, e)
    return jars


def _open_jars(root):
    """jars held open by running JVMs, via /proc/<pid>/fd. Only Java processes are inspected."""
    seen = {}
    for fd_dir in glob.glob(os.path.join(root, "proc", "[0-9]*", "fd")):
        pid = os.path.basename(os.path.dirname(fd_dir))
        # Restrict the /proc walk to JVMs: skip non-Java processes entirely.
        if not _is_jvm(pid, root):
            continue
        for tgt in _jars_of_pid(fd_dir, root):
            seen.setdefault(tgt, pid)
    return seen


def _scanned_jars(root):
    """jars on disk under the dirs in ``JAVA_PURLS_SCAN_DIRS`` (opt-in; empty by default).

    There is deliberately no default: a recursive walk of distro dirs is expensive at fleet scale
    and their jars are already reported by ``installed_rpms``. Operators with app jars outside a
    running JVM's open FDs can opt in by setting the env var to a short, specific list (e.g. ``/opt``).
    """
    raw = os.environ.get("JAVA_PURLS_SCAN_DIRS", "").strip()
    if not raw:
        return {}
    found = {}
    for d in raw.split(","):
        d = d.strip()
        if not d:
            continue
        base = _under_root(root, d)
        for jar in glob.glob(os.path.join(base, "**", "*.jar"), recursive=True):
            found.setdefault(os.path.realpath(jar), None)
    return found


def _scan_all(jars, findings, counter):
    """Analyze each jar on disk into ``findings``, respecting the total-jars and size caps.

    Graceful degradation: if the datasource hard timeout (or any unexpected error) fires mid-scan,
    return whatever purls were found so far rather than losing the whole run.
    """
    try:
        for jar_path in jars:
            if counter["n"] >= MAX_JARS:
                break
            try:
                # Skip oversized jars on disk cheaply (stat, no read).
                if os.path.getsize(jar_path) > MAX_JAR_BYTES:
                    continue
            except OSError:
                continue
            try:
                _analyze(os.path.basename(jar_path), path=jar_path, out=findings, counter=counter)
            except Exception as e:
                logger.debug("java_purls: analyze failed for %s: %s", jar_path, e)
                continue
    except Exception as e:
        logger.debug("java_purls: scan aborted early: %s", e)


def _dedup(findings):
    """De-duplicate resolved purls, preserving first-seen order."""
    seen, uniq = set(), []
    for f in findings:
        key = f.get("purl")
        if key and key not in seen:
            seen.add(key)
            uniq.append(f)
    return uniq


@datasource(HostContext, timeout=120)
def java_purls(broker):
    """Detect Java libraries on the host and emit their purls (default collection, gated by presence)."""
    root = broker[HostContext].root or "/"
    jars = {}
    jars.update(_scanned_jars(root))  # opt-in disk scan (empty unless JAVA_PURLS_SCAN_DIRS is set)
    jars.update(_open_jars(root))     # the default source: jars held open by running JVMs

    findings = []
    counter = {"n": 0}
    _scan_all(jars, findings, counter)

    uniq = _dedup(findings)
    if not uniq:
        raise SkipComponent("No Java libraries detected")

    # Compact JSON (no indent) to minimize archive size at fleet scale. Only jar basenames are
    # emitted -- never absolute paths -- and no pid/sha1, per data governance.
    return DatasourceProvider(content=json.dumps(uniq), relative_path=RELATIVE_PATH)
