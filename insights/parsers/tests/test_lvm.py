from __future__ import print_function
from insights.parsers import lvm

WARNINGS_CONTENT = """
WARNING
valid data 1
Checksum Error
valid data 2
  Failed to write
  Attempt To Close Device
valid data 3
""".strip()

WARNINGS_FOUND = """
WARNING
Checksum Error
  Failed to write
  Attempt To Close Device
""".strip()


def test_find_warnings():
    data = [l for l in lvm.find_warnings(WARNINGS_CONTENT.splitlines())]
    assert len(data) == len(WARNINGS_FOUND.splitlines())
    assert data == WARNINGS_FOUND.splitlines()


def compare_partial_dicts(result, expected):
    """
    Make sure all the keys in expected are matched by keys in result, and
    that the values stored in those keys match.  Result can contain more
    items than expected - those are ignored.

    Used in the test_lvs, test_pvs and test_vgs tests.
    """
    # return all(result[k] == expected[k] for k in expected.keys())
    mismatches = 0
    for k in expected.keys():
        if not result[k] == expected[k]:
            print("Failed for key {k}, {r} != {e}".format(k=k, r=result[k], e=expected[k]))
            mismatches += 1
    return mismatches == 0
