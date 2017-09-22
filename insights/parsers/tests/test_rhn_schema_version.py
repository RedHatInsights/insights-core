from insights.tests import context_wrap
from insights.parsers.rhn_schema_version import rhn_schema_version

schema_content_ok = """
5.6.0.10-2.el6sat
""".strip()

schema_content_no = """
-bash: /usr/bin/rhn-schema-version: No such file or directory
""".strip()


def test_rhn_schema_version():
    result = rhn_schema_version(context_wrap(schema_content_ok))
    assert result == "5.6.0.10-2.el6sat"
    result = rhn_schema_version(context_wrap(schema_content_no))
    assert result is None
