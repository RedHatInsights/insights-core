import doctest
import pytest
import re
import sys

from doctest import (DebugRunner, DocTestFinder, DocTestRunner,
                     OutputChecker)


class Py23DocChecker(OutputChecker):
    def check_output(self, want, got, optionflags):
        if sys.version_info[0] > 2:
            want = re.sub("u'(.*?)'", "'\\1'", want)
            want = re.sub("u'(.*?)'", "'\\1'", want)
        return OutputChecker.check_output(self, want, got, optionflags)


def ic_testmod(m, name=None, globs=None, verbose=None,
               report=True, optionflags=0, extraglobs=None,
               raise_on_error=False, exclude_empty=False):
    """See original code in doctest.testmod."""
    if name is None:
        name = m.__name__
    finder = DocTestFinder(exclude_empty=exclude_empty)
    if raise_on_error:
        runner = DebugRunner(checker=Py23DocChecker(),
                             verbose=verbose,
                             optionflags=optionflags)
    else:
        runner = DocTestRunner(checker=Py23DocChecker(),
                               verbose=verbose,
                               optionflags=optionflags)
    for test in finder.find(m, name, globs=globs, extraglobs=extraglobs):
        runner.run(test)

    if report:
        runner.summarize()

    return doctest.TestResults(runner.failures, runner.tries)


def skip_component_check(parser_obj, output_str=""):
    from insights.core.exceptions import SkipComponent
    from insights.tests import context_wrap

    with pytest.raises(SkipComponent) as ex:
        parser_obj(context_wrap(output_str))
    return str(ex)
