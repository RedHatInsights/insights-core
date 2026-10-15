import doctest

from insights.parsers import python_purls
from insights.parsers.python_purls import PythonPurls
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check


# The datasource emits JSONL (one object per line); the parser is also tolerant of a legacy JSON array.
PURLS_JSONL = (
    '{"purl": "pkg:pypi/jinja2@2.11.3", "dist": "Jinja2-2.11.3.dist-info", "source": "dist-info", "installer": "rpm"}\n'
    '{"purl": "pkg:pypi/babel@2.9.1", "dist": "Babel-2.9.1.egg-info", "source": "egg-info", "installer": null}'
)

PURLS_JSON = (
    '[{"purl": "pkg:pypi/jinja2@2.11.3", "dist": "Jinja2-2.11.3.dist-info", "source": "dist-info", "installer": "rpm"}, '
    '{"purl": "pkg:pypi/babel@2.9.1", "dist": "Babel-2.9.1.egg-info", "source": "egg-info", "installer": null}]'
)


def test_python_purls():
    # JSONL (the current datasource format).
    parsed = PythonPurls(context_wrap(PURLS_JSONL))
    assert len(parsed.findings) == 2
    assert parsed.purls == ["pkg:pypi/jinja2@2.11.3", "pkg:pypi/babel@2.9.1"]
    # non_rpm_purls drops the RPM-marked entry, keeps the unmarked one
    assert parsed.non_rpm_purls == ["pkg:pypi/babel@2.9.1"]
    assert parsed.data[0]["source"] == "dist-info"
    assert parsed.data[1]["dist"] == "Babel-2.9.1.egg-info"


def test_python_purls_legacy_json_array():
    # Backward compatibility: a legacy single JSON array still parses (version-skew tolerant).
    parsed = PythonPurls(context_wrap(PURLS_JSON))
    assert len(parsed.findings) == 2
    assert parsed.purls == ["pkg:pypi/jinja2@2.11.3", "pkg:pypi/babel@2.9.1"]


def test_python_purls_skips_mangled_line():
    # The point of JSONL: a line dropped/mangled by customer redaction costs ONE record, not the inventory.
    mangled = (
        '{"purl": "pkg:pypi/jinja2@2.11.3", "dist": "Jinja2-2.11.3.dist-info", "source": "dist-info"}\n'
        '{"purl": "pkg:pypi/REDACTED  <- not valid json\n'
        '{"purl": "pkg:pypi/babel@2.9.1", "dist": "Babel-2.9.1.egg-info", "source": "egg-info"}'
    )
    parsed = PythonPurls(context_wrap(mangled))
    assert parsed.purls == ["pkg:pypi/jinja2@2.11.3", "pkg:pypi/babel@2.9.1"]


def test_python_purls_empty():
    assert "Empty output." in skip_component_check(PythonPurls)


def test_python_purls_doc_examples():
    env = {
        "python_purls": PythonPurls(context_wrap(PURLS_JSONL)),
    }
    failed, total = doctest.testmod(python_purls, globs=env)
    assert failed == 0
    assert total > 0  # guard: 0 examples would pass vacuously
