from insights.core.plugins import make_response
from insights.tests import InputData, archive_provider
import insights
from insights.plugins import basic_one as rule

UNAME_TEMPLATE = "Linux testhost1 %s #1 SMP Tue Jan 29 11:47:41 EST 2013 x86_64 x86_64 x86_64 GNU/Linux"

VULNERABLE = [UNAME_TEMPLATE % ("%s.el%s.x86_64" % (kernel, release.split(".")[0])) for kernel, release in insights.parsers.uname.release_to_kernel_map.items()]


@archive_provider(rule.report)
def integration_tests():
        i = InputData()
        i.add('uname', VULNERABLE[0])
        expected = make_response("BASIC_ONE", kernel="this is junk")
        yield i, [expected]
