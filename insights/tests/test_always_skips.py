from insights.tests import InputData, archive_provider

from insights.plugins import always_skips


@archive_provider(always_skips)
def integration_tests():
        i = InputData()
        yield i, []
