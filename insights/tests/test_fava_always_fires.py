from insights.core.plugins import make_response
from insights.tests import InputData, archive_provider

from insights.core.fava import load_fava_plugin
fava_always_fires = load_fava_plugin('insights.plugins.fava_always_fires')


@archive_provider(fava_always_fires.report)
def integration_tests():
        i = InputData()
        expected = make_response("FAVA_ALWAYS_FIRES", kernel="this is junk")
        yield i, [expected]
