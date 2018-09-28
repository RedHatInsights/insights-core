from insights.tools.specs_to_rules import main
import sys
from insights.specs import Specs

from insights.core.plugins import make_response, rule

if (sys.version_info > (3, 0)):
        from io import StringIO
else:
    from StringIO import StringIO


@rule(Specs.hostname)
def report(host):

    return make_response("HOSTNAME", echo=host)


GOOD_RULE = "insights.tests.test_specs_to_rules"
BAD_RULE = "insights.tests.test_specs_to_rule"
CORE_COMP_ERROR = "**** Error encountered loading core components"
PLUGINS_ERROR = "**** Error encountered loading plugins"


def test_report_created():
    """
    Tests specs_to_rules is reporting on the provided rule successfully.
    """
    res_str = ''
    try:
        old_stdout = sys.stdout
        res = StringIO()
        sys.stdout = res

        main([GOOD_RULE])
        res_str = res.getvalue()

        sys.stdout = old_stdout
    except:
        pass

    assert GOOD_RULE in res_str


def test_report_error():

    res_str = ''
    try:
        old_stdout = sys.stdout
        res = StringIO()
        sys.stdout = res

        main([BAD_RULE])
        res_str = res.getvalue()

        sys.stdout = old_stdout
    except:
        pass

    assert CORE_COMP_ERROR in res_str or PLUGINS_ERROR in res_str
