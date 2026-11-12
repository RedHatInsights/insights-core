"""
JavaPurls - datasource ``java_purls``
========================================================

Parses the output of the
:py:func:`insights.specs.datasources.java_purls.java_purls` datasource.

The datasource emits **JSONL** -- one compact JSON object per line (redaction-resilient). This parser is
also tolerant of a legacy single JSON array, so a datasource/parser version skew during rollout never
breaks parsing; a line dropped or mangled by customer redaction costs a single record, not the inventory.

Each object has three keys:

* ``purl``   -- the package URL (``pkg:maven/<group>/<artifact>@<version>``)
* ``jar``    -- the jar basename the finding came from (never an absolute path)
* ``source`` -- how it was resolved (``pom.properties`` or ``spring-boot-sbom``)
"""

import json

from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.java_purls)
class JavaPurls(Parser):
    """
    Parse the ``java_purls`` datasource output (JSONL; legacy JSON array also accepted).

    Sample input::

        {"purl": "pkg:maven/org.foo/bar@1.2.3", "jar": "bar.jar", "source": "pom.properties"}
        {"purl": "pkg:maven/org.baz/qux@4.5.6", "jar": "qux.jar", "source": "spring-boot-sbom"}

    Examples:
        >>> type(java_purls)
        <class 'insights.parsers.java_purls.JavaPurls'>
        >>> len(java_purls.findings)
        2
        >>> java_purls.purls
        ['pkg:maven/org.foo/bar@1.2.3', 'pkg:maven/org.baz/qux@4.5.6']
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
