"""
Py2/Py3 compatible doctest checker and runner for parser documentation tests.
"""

import doctest
import re

DOCTEST_ALLOW_TYPE_CLASS = doctest.register_optionflag('ALLOW_TYPE_CLASS')
INSIGHTS_DOCTEST_OPTIONFLAGS = DOCTEST_ALLOW_TYPE_CLASS

_TYPE_CLASS_RE = re.compile(r"<type '([^']+)'>")


def _normalize_type_class_repr(text):
    return _TYPE_CLASS_RE.sub(r"<class '\1'>", text)


_StandardOutputChecker = doctest.OutputChecker


class InsightsDoctestChecker(_StandardOutputChecker):
    def check_output(self, want, got, optionflags):
        if _StandardOutputChecker.check_output(self, want, got, optionflags):
            return True

        if not optionflags & DOCTEST_ALLOW_TYPE_CLASS:
            return False

        want = _normalize_type_class_repr(want)
        got = _normalize_type_class_repr(got)

        return _StandardOutputChecker.check_output(self, want, got, optionflags)


INSIGHTS_DOCTEST_CHECKER = InsightsDoctestChecker()

_StandardDocTestRunner = doctest.DocTestRunner


class InsightsDocTestRunner(_StandardDocTestRunner):
    def __init__(self, checker=None, verbose=None, optionflags=0):
        if checker is None:
            checker = INSIGHTS_DOCTEST_CHECKER
        optionflags |= INSIGHTS_DOCTEST_OPTIONFLAGS
        _StandardDocTestRunner.__init__(self, checker, verbose, optionflags)
