"""
Custom datasource to inventory installed Python distributions from site-packages and emit their purls.

This complements ``installed_rpms`` (which represents RPM-packaged Python) by capturing EVERY distribution
visible in site-packages -- including ones that arrive OUTSIDE RPM (``pip install`` into system/user
site-packages or a virtualenv) -- so they can be matched against third-party CVE data downstream.

Resolution is authoritative and entirely local: each installed distribution records its name + version in
``*.dist-info/METADATA`` (PEP 566) or legacy ``*.egg-info/PKG-INFO``; we read those headers and emit
``pkg:pypi/<normalized-name>@<version>`` (PEP 503 name normalization). No network call, no hashing.

Provenance caveat (established by on-host dogfood): on a stock RHEL host, essentially all site-packages
distributions are RPM-owned, and the per-dist ``INSTALLER`` marker is NOT a reliable RPM-vs-pip signal
(RPM rebuilds of upstream wheels can carry ``INSTALLER=pip``). Only the RPM database is authoritative.
We therefore do NOT silently drop RPM-owned entries here; we emit the complete inventory plus the cheap,
best-effort ``installer`` marker (``pip`` / ``rpm`` / ``None``) as advisory provenance, and leave
RPM-ownership reconciliation (and the backported-fix / upstream-version distinction) to the downstream
consumer, which is RPM-native. This keeps the collector honest and crash-free; it does not over-claim a
filter it cannot do reliably at collection time.

Because this runs in default collection at fleet scale it enforces a safety envelope: scanning is limited
to known/allow-listed site-packages roots (extra roots are opt-in via ``PYTHON_PURLS_SCAN_DIRS``), caps on
the number/size of metadata files read, a soft wall-clock budget, and graceful partial results (never a
crash) when a cap or the budget is hit.

Output: a JSON array of ``{purl, dist, source, installer}`` objects at
``data/insights_datasources/python_purls.json`` (``dist`` is the dist-info/egg-info basename only; no
absolute path, no pid, no hash; ``installer`` is advisory and may be ``None``).
"""
import glob
import io
import json
import logging
import os
import re
import sysconfig

try:
    from urllib.parse import quote
except ImportError:  # pragma: no cover - py2 fallback, consistent with the rest of insights-core
    from urllib import quote

try:
    from time import monotonic as _monotonic
except ImportError:  # pragma: no cover - py2 fallback (time.monotonic is py3.3+)
    from time import time as _monotonic

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider

logger = logging.getLogger(__name__)

RELATIVE_PATH = "insights_datasources/python_purls.json"


def _int_env(name, default):
    """Read a positive int cap from the environment, falling back to the default on absent/garbage."""
    try:
        return int(os.environ[name])
    except (KeyError, ValueError, TypeError):
        return default


# Fleet-scale safety caps (module constants, overridable via env). Hitting any cap stops the scan cleanly
# and emits the partial results collected so far rather than crashing.
MAX_PACKAGES = _int_env("PYTHON_PURLS_MAX_PACKAGES", 5000)             # total distributions emitted
MAX_METADATA_BYTES = _int_env("PYTHON_PURLS_MAX_METADATA_BYTES", 1024 * 1024)  # skip a huge METADATA file
MAX_SECONDS = _int_env("PYTHON_PURLS_MAX_SECONDS", 60)                 # soft wall-clock budget


def _enc(component):
    """Percent-encode a purl component per the purl spec (RFC 3986 unreserved kept)."""
    return quote(component, safe="")


def _normalize_name(name):
    """PEP 503 normalization: lowercase, collapse runs of [-_.] to a single '-'."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _read_headers(path):
    """Return the (Name, Version) from a METADATA / PKG-INFO file, or (None, None).

    Only the leading RFC-822-style header block is needed; stop at the first blank line (the body is the
    long description and can be large). Bounded by MAX_METADATA_BYTES.
    """
    try:
        if os.path.getsize(path) > MAX_METADATA_BYTES:
            return None, None
    except OSError:
        return None, None
    name = version = None
    try:
        with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line == "\n" or line == "\r\n":
                    break  # end of headers; don't read the (potentially huge) body
                if name is None and line.startswith("Name:"):
                    name = line.split(":", 1)[1].strip()
                elif version is None and line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                if name and version:
                    break
    except (OSError, UnicodeError) as e:
        logger.debug("python_purls: could not read %s: %s", path, e)
        return None, None
    return name, version


def _read_installer(dist_dir):
    """Best-effort advisory provenance from the dist-info ``INSTALLER`` marker (``pip``/``rpm``/None).

    Cheap (a tiny sibling file, no subprocess) but NOT authoritative: RPM rebuilds of upstream wheels can
    carry ``INSTALLER=pip``. Only the RPM database truly settles ownership -- that is a downstream concern.
    """
    path = os.path.join(dist_dir, "INSTALLER")
    try:
        if os.path.getsize(path) > 256:
            return None
        with io.open(path, "r", encoding="utf-8", errors="replace") as fh:
            val = fh.read().strip()
        return val or None
    except OSError:
        return None


def _default_site_dirs(root):
    """Standard site-packages roots from sysconfig, resolved against the context root."""
    dirs = set()
    for key in ("purelib", "platlib"):
        try:
            p = sysconfig.get_paths().get(key)
        except Exception:  # noqa: BLE001 - sysconfig should not fail, but never crash collection
            p = None
        if p:
            dirs.add(p)
    # Common extra locations not always covered by the running interpreter's sysconfig.
    dirs.update(["/usr/lib/python3*/site-packages", "/usr/lib64/python3*/site-packages",
                 "/usr/local/lib/python3*/site-packages"])
    resolved = []
    for d in dirs:
        if root in ("/", "", None):
            resolved.append(d)
        else:
            resolved.append(os.path.join(root, d.lstrip("/")))
    return resolved


def _scan_dirs(root):
    """All site-packages roots to scan: the defaults plus any opt-in PYTHON_PURLS_SCAN_DIRS."""
    dirs = list(_default_site_dirs(root))
    extra = os.environ.get("PYTHON_PURLS_SCAN_DIRS", "").strip()
    for d in extra.split(","):
        d = d.strip()
        if not d:
            continue
        dirs.append(d if root in ("/", "", None) else os.path.join(root, d.lstrip("/")))
    return dirs


def _metadata_files(scan_dirs, deadline=None):
    """De-duplicated set of dist-info/METADATA + egg-info/PKG-INFO files under the scan roots.

    Discovery itself is bounded by the soft ``deadline`` (checked per scan root): on a pathological
    site-packages layout (many roots / deep recursive globs) we stop globbing and return what we have so
    far rather than letting discovery run past the wall-clock budget.
    """
    found = {}
    for base in scan_dirs:
        if deadline is not None and _monotonic() > deadline:
            break
        for pattern in ("*.dist-info/METADATA", "*.egg-info/PKG-INFO"):
            for path in glob.glob(os.path.join(base, pattern)):
                found.setdefault(os.path.realpath(path), None)
    return found


def _collect(scan_dirs):
    """Walk the metadata files into [{purl, dist, source}], honoring the caps + soft deadline."""
    out = []
    deadline = _monotonic() + MAX_SECONDS
    # Sorted for deterministic output order run-to-run (glob/readdir order is not stable).
    # The deadline bounds discovery too (not just the per-file scan below).
    for path in sorted(_metadata_files(scan_dirs, deadline)):
        if len(out) >= MAX_PACKAGES or _monotonic() > deadline:
            break
        name, version = _read_headers(path)
        if not name or not version:
            continue
        purl = "pkg:pypi/%s@%s" % (_enc(_normalize_name(name)), _enc(version))
        dist_dir = os.path.dirname(path)
        source = "dist-info" if path.endswith("METADATA") else "egg-info"
        # INSTALLER only exists alongside dist-info; egg-info (legacy) has no such marker.
        installer = _read_installer(dist_dir) if source == "dist-info" else None
        out.append({
            "purl": purl,
            "dist": os.path.basename(dist_dir),
            "source": source,
            "installer": installer,
        })
    return out


def _dedup(found):
    """De-duplicate resolved purls, preserving first-seen (sorted) order."""
    seen, uniq = set(), []
    for f in found:
        key = f.get("purl")
        if key and key not in seen:
            seen.add(key)
            uniq.append(f)
    return uniq


@datasource(HostContext, timeout=120)
def python_purls(broker):
    """Detect installed third-party Python libraries and emit their purls (default collection)."""
    root = broker[HostContext].root or "/"
    uniq = _dedup(_collect(_scan_dirs(root)))
    if not uniq:
        raise SkipComponent("No Python libraries detected")
    # Compact JSON (no indent) to minimize archive size. Only dist-info basenames are emitted -- never
    # absolute paths -- and no pid/hash, per data governance.
    return DatasourceProvider(content=json.dumps(uniq), relative_path=RELATIVE_PATH)
