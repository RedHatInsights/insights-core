from insights.parsers import getenforce
from insights.tests import context_wrap

GETENFORCE1 = "Enforcing"
GETENFORCE2 = "Permissive"
GETENFORCE3 = "Disabled"


class Testgetenforce():
    def test_getenforce(self):
        result = getenforce.getenforcevalue(context_wrap(GETENFORCE1))
        assert result.get("status") == 'Enforcing'

        result = getenforce.getenforcevalue(context_wrap(GETENFORCE2))
        assert result.get("status") == 'Permissive'

        result = getenforce.getenforcevalue(context_wrap(GETENFORCE3))
        assert result.get("status") == 'Disabled'
