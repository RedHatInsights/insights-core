"""
JavaPurls - datasource ``java_purls``
========================================================

Parses the JSON array emitted by the
:py:func:`insights.specs.datasources.java_purls.java_purls` datasource.

Each element is an object with three keys:

* ``purl``   -- the package URL (``pkg:maven/<group>/<artifact>@<version>``)
* ``jar``    -- the jar basename the finding came from (never an absolute path)
* ``source`` -- how it was resolved (``pom.properties`` or ``spring-boot-sbom``)
"""

from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.java_purls)
class JavaPurls(JSONParser):
    """
    Parse the ``java_purls`` datasource output (a JSON array of findings).

    Sample input::

        [{"purl": "pkg:maven/org.foo/bar@1.2.3", "jar": "bar.jar", "source": "pom.properties"},
         {"purl": "pkg:maven/org.baz/qux@4.5.6", "jar": "qux.jar", "source": "spring-boot-sbom"}]

    Examples:
        >>> type(java_purls)
        <class 'insights.parsers.java_purls.JavaPurls'>
        >>> len(java_purls.findings)
        2
        >>> java_purls.purls
        ['pkg:maven/org.foo/bar@1.2.3', 'pkg:maven/org.baz/qux@4.5.6']
    """

    @property
    def findings(self):
        """list: all finding objects as emitted by the datasource."""
        return self.data

    @property
    def purls(self):
        """list: the resolved package URLs."""
        return [f["purl"] for f in self.data if f.get("purl")]
