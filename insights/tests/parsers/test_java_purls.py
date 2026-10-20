import doctest

from insights.parsers import java_purls
from insights.parsers.java_purls import JavaPurls
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check


# The datasource emits JSONL (one object per line); the parser is also tolerant of a legacy JSON array.
PURLS_JSONL = (
    '{"purl": "pkg:maven/org.foo/bar@1.2.3", "jar": "bar.jar", "source": "pom.properties"}\n'
    '{"purl": "pkg:maven/org.baz/qux@4.5.6", "jar": "qux.jar", "source": "spring-boot-sbom"}'
)

PURLS_JSON = (
    '[{"purl": "pkg:maven/org.foo/bar@1.2.3", "jar": "bar.jar", "source": "pom.properties"}, '
    '{"purl": "pkg:maven/org.baz/qux@4.5.6", "jar": "qux.jar", "source": "spring-boot-sbom"}]'
)


def test_java_purls():
    # JSONL (the current datasource format).
    parsed = JavaPurls(context_wrap(PURLS_JSONL))
    assert len(parsed.findings) == 2
    assert parsed.purls == ["pkg:maven/org.foo/bar@1.2.3", "pkg:maven/org.baz/qux@4.5.6"]
    assert parsed.data[0]["source"] == "pom.properties"


def test_java_purls_legacy_json_array():
    # Backward compatibility: a legacy single JSON array still parses (version-skew tolerant).
    parsed = JavaPurls(context_wrap(PURLS_JSON))
    assert len(parsed.findings) == 2
    assert parsed.purls == ["pkg:maven/org.foo/bar@1.2.3", "pkg:maven/org.baz/qux@4.5.6"]


def test_java_purls_skips_mangled_line():
    # The point of JSONL: a line dropped/mangled by customer redaction costs ONE record, not the inventory.
    mangled = (
        '{"purl": "pkg:maven/org.foo/bar@1.2.3", "jar": "bar.jar", "source": "pom.properties"}\n'
        '{"purl": "pkg:maven/org.REDACTED  <- not valid json\n'
        '{"purl": "pkg:maven/org.baz/qux@4.5.6", "jar": "qux.jar", "source": "spring-boot-sbom"}'
    )
    parsed = JavaPurls(context_wrap(mangled))
    assert parsed.purls == ["pkg:maven/org.foo/bar@1.2.3", "pkg:maven/org.baz/qux@4.5.6"]


def test_java_purls_empty():
    assert "Empty output." in skip_component_check(JavaPurls)


def test_java_purls_doc_examples():
    env = {
        "java_purls": JavaPurls(context_wrap(PURLS_JSONL)),
    }
    failed, total = doctest.testmod(java_purls, globs=env)
    assert failed == 0
    assert total > 0  # guard: ensure doctest examples actually exist (0 examples would pass vacuously)
