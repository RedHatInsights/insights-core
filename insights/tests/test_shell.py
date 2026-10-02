from unittest.mock import patch

import pytest

from insights import make_pass, rule


@rule()
def report():
    return make_pass("SHOW_RULE_REPORT_PASS")


def test_show_rule_report_pages_the_report():
    pytest.importorskip("IPython")
    from insights.shell import Models

    broker = {report: report()}
    models = Models(broker, {}, "", "", False)
    with patch("insights.shell.render", return_value="rule body"), \
            patch("insights.shell.render_links", return_value=""), \
            patch("insights.shell.IPython.core.page.page") as page:
        models.show_rule_report()
    output = page.call_args[0][0]
    assert "test_shell.report" in output
    assert "rule body" in output
