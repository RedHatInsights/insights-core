# -*- coding: UTF-8 -*-

from insights.parsers import abrt_status_bare
from insights.parsers.abrt_status_bare import AbrtStatusBare
from insights.tests import context_wrap

import doctest

OUTPUT = """
420
""".strip()

OUTPUT_MULTILINE = """
1997
This line will never exist in real output, but it is ignored.
""".strip()


def test():
    result = AbrtStatusBare(context_wrap(OUTPUT))
    assert result.problem_count == 420

    result = AbrtStatusBare(context_wrap(OUTPUT_MULTILINE))
    assert result.problem_count == 1997


def test_docs():
    env = {
        'abrt_status_bare': AbrtStatusBare(context_wrap(OUTPUT_MULTILINE)),
        'AbrtStatusBare': AbrtStatusBare,
    }
    failed, total = doctest.testmod(abrt_status_bare, globs=env)
    assert failed == 0
