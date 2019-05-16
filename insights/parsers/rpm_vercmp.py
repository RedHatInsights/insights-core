"""
Nearly direct translation of rpm comparison code in the rpm project at
https://github.com/rpm-software-management/rpm/blob/master/lib/rpmvercmp.c

Handles all of the cases in the rpm test file, including the "buggy" tests
and non-ascii characters.

https://raw.githubusercontent.com/rpm-software-management/rpm/master/tests/rpmvercmp.at
"""

from collections import deque
from itertools import takewhile


def _rpm_vercmp(a, b):
    if a == b:
        return 0

    # ord check required for consistent unicode handling
    # empty string appended to simplify other checks below
    a = deque([c if ord(c) < 128 else "." for c in a])
    a.append("")

    b = deque([c if ord(c) < 128 else "." for c in b])
    b.append("")

    while a[0] or b[0]:
        for x in [a, b]:
            while x[0] and not x[0].isalnum() and x[0] not in "~^":
                x.popleft()

        # handle the tilde separator, it sorts before everything else
        if a[0] == "~" or b[0] == "~":
            if a[0] != "~":
                return 1
            if b[0] != "~":
                return -1
            a.popleft()
            b.popleft()
            continue

        # Handle caret separator. Concept is the same as tilde,
        # except that if one of the strings ends (base version),
        # the other is considered as higher version.
        if a[0] == "^" or b[0] == "^":
            if not a[0]:
                return -1
            if not b[0]:
                return 1
            if a[0] != "^":
                return 1
            if b[0] != "^":
                return -1
            a.popleft()
            b.popleft()
            continue

        # If we ran to the end of either, we are finished with the loop
        if not a[0] or not b[0]:
            break

        # grab first completely alpha or completely numeric segment
        if a[0].isdigit():
            l = deque(takewhile(lambda v: v.isdigit(), a))
            r = deque(takewhile(lambda v: v.isdigit(), b))
            isnum = True
        else:
            l = deque(takewhile(lambda v: v.isalpha(), a))
            r = deque(takewhile(lambda v: v.isalpha(), b))
            isnum = False

        # this cannot happen, as we previously tested to make sure that
        # the first string has a non-null segment
        if not l:
            return -1

        # take care of the case where the two version segments are
        # different types: one numeric, the other alpha (i.e. empty)
        # numeric segments are always newer than alpha segments
        # XXX See details from bugzilla #50977.
        if not r:
            return 1 if isnum else -1

        ll = len(l)
        lr = len(r)
        if isnum:
            # throw away any leading zeros - it's a number, right?
            for x in [l, r]:
                while x and x[0] == '0':
                    x.popleft()

            # whichever number has more digits wins
            lenl = len(l)
            lenr = len(r)
            if lenl > lenr:
                return 1

            if lenr > lenl:
                return -1

        if l > r:
            return 1

        if l < r:
            return -1

        for _ in range(ll):
            a.popleft()

        for _ in range(lr):
            b.popleft()

    # this catches the case where all numeric and alpha segments have
    # compared identically but the segment separating characters were
    # different
    if not a[0] and not b[0]:
        return 0

    # whichever version still has characters left over wins
    if not a[0]:
        return -1
    return 1


def rpm_version_compare(left, right):
    if left is right:
        return 0

    le, re = int(left.epoch), int(right.epoch)
    if le < re:
        return -1
    elif le > re:
        return 1

    rc = _rpm_vercmp(left.version, right.version)
    if rc != 0:
        return rc

    return _rpm_vercmp(left.release, right.release)
