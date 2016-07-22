from falafel.tests import context_wrap
from falafel.mappers.rhn_schema_version import rhn_schema_version

schema_content = """
5.6.0.10-2.el6sat
""".strip()


def test_rhn_schema_version():
    result = rhn_schema_version(context_wrap(schema_content))
    assert result == "5.6.0.10-2.el6sat"
