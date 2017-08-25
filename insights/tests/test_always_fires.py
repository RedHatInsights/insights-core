from insights.core.plugins import make_response
from insights.tests import InputData, archive_provider

from insights.plugins import always_fires


@archive_provider(always_fires)
def integration_tests():
        i = InputData()
        expected = make_response("ALWAYS_FIRES", kernel="this is junk")
        yield i, [expected]
