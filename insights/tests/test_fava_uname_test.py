from insights.core.plugins import make_response
from insights.core.fava import load_fava_plugin
from insights.tests import InputData, archive_provider
import insights
rule = load_fava_plugin('insights.plugins.uname_test')

ERROR_KEY = 'UNAME_TEST'

UNAME_TEMPLATE = "Linux testhost1 %s #1 SMP Tue Jan 29 11:47:41 EST 2013 x86_64 x86_64 x86_64 GNU/Linux"

NOT_VULNERABLE = [UNAME_TEMPLATE % ("%s.el%s.x86_64" % (kernel, release.split(".")[0])) for kernel, release in insights.parsers.uname.release_to_kernel_map.items()]

VULNERABLE = []


@archive_provider(rule)
def integration_tests():
    for uname_line in VULNERABLE:
        i = InputData()
        i.add('uname', uname_line)
        expected = make_response(ERROR_KEY)
        yield i, [expected]

    for uname_line in NOT_VULNERABLE:
        i = InputData()
        i.add('uname', uname_line)
        yield i, []
