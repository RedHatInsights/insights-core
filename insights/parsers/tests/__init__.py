#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import doctest
from doctest import (DebugRunner, DocTestFinder, DocTestRunner,
                     OutputChecker)
import re
import sys


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
