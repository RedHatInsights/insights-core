import doctest

from insights.parsers import java_purls
from insights.parsers.java_purls import JavaPurls
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check


PURLS_JSON = (
    '[{"purl": "pkg:maven/org.foo/bar@1.2.3", "jar": "bar.jar", "source": "pom.properties"}, '
    '{"purl": "pkg:maven/org.baz/qux@4.5.6", "jar": "qux.jar", "source": "spring-boot-sbom"}]'
)


def test_java_purls():
    parsed = JavaPurls(context_wrap(PURLS_JSON))
    assert len(parsed.findings) == 2
    assert parsed.purls == ["pkg:maven/org.foo/bar@1.2.3", "pkg:maven/org.baz/qux@4.5.6"]
    # LegacyItemAccess exposes the raw list via .data
    assert parsed.data[0]["source"] == "pom.properties"


def test_java_purls_empty():
    assert "Empty output." in skip_component_check(JavaPurls)


def test_java_purls_doc_examples():
    env = {
        "java_purls": JavaPurls(context_wrap(PURLS_JSON)),
    }
    failed, total = doctest.testmod(java_purls, globs=env)
    assert failed == 0
