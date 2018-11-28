# -*- coding: UTF-8 -*-

from pytest import fixture


class IsinstanceMatcher(object):
    """
    Matches whether a call argument is an instance of the given type.
    """
    def __init__(self, expected_type):
        self.expected_type = expected_type

    def __eq__(self, other):
        return isinstance(other, self.expected_type)


@fixture
def isinstance_matcher():
    """
    Matches whether a call argument is an instance of the given type.
    """
    return IsinstanceMatcher
