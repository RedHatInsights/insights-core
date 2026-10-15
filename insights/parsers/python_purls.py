"""
PythonPurls - datasource ``python_purls``
========================================================

Parses the output of the
:py:func:`insights.specs.datasources.python_purls.python_purls` datasource.

The datasource emits **JSONL** -- one compact JSON object per line (redaction-resilient). This parser is
also tolerant of a legacy single JSON array, so a datasource/parser version skew during rollout never
breaks parsing; a line dropped or mangled by customer redaction costs a single record, not the inventory.

Each object has these keys:

* ``purl``      -- the package URL (``pkg:pypi/<normalized-name>@<version>``)
* ``dist``      -- the dist-info/egg-info directory basename (never an absolute path)
* ``source``    -- how it was resolved (``dist-info`` or ``egg-info``)
* ``installer`` -- advisory provenance from the ``INSTALLER`` marker (``pip``/``rpm``/``None``);
  NOT authoritative for RPM ownership (see the datasource docstring)
"""

import json

from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.python_purls)
class PythonPurls(Parser):
    """
    Parse the ``python_purls`` datasource output (JSONL; legacy JSON array also accepted).

    Sample input::

        {"purl": "pkg:pypi/jinja2@2.11.3", "dist": "Jinja2-2.11.3.dist-info", "source": "dist-info", "installer": "rpm"}
        {"purl": "pkg:pypi/babel@2.9.1", "dist": "Babel-2.9.1.egg-info", "source": "egg-info", "installer": null}

    Examples:
        >>> type(python_purls)
        <class 'insights.parsers.python_purls.PythonPurls'>
        >>> len(python_purls.findings)
        2
        >>> python_purls.purls
        ['pkg:pypi/jinja2@2.11.3', 'pkg:pypi/babel@2.9.1']
        >>> python_purls.non_rpm_purls
        ['pkg:pypi/babel@2.9.1']
    """

    def parse_content(self, content):
        text = ("\n".join(content) if isinstance(content, list) else (content or "")).strip()
        self.data = []
        if not text:
            raise SkipComponent("Empty output.")
        if text[0] == "[":
            # Legacy single JSON array.
            self.data = json.loads(text)
            return
        # JSONL: one object per line. Skip blank or redaction-mangled lines (cost one record, not all).
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                self.data.append(json.loads(line))
            except ValueError:
                continue

    @property
    def findings(self):
        """list: all finding objects as emitted by the datasource."""
        return self.data

    @property
    def purls(self):
        """list: the resolved package URLs."""
        return [f["purl"] for f in self.data if f.get("purl")]

    @property
    def non_rpm_purls(self):
        """list: purls whose advisory ``installer`` marker is not ``rpm``.

        A best-effort view of likely-third-party (non-distro) packages. Advisory only -- authoritative
        RPM-ownership reconciliation belongs downstream (see the datasource docstring).
        """
        return [f["purl"] for f in self.data if f.get("purl") and f.get("installer") != "rpm"]
