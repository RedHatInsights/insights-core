from insights.tests import deep_compare


def test_deep_compare():
    """
    Tests that deep_compare() doesn't modify the objects it compares.
    """
    x_list = [8, 5, 3, 1, 2, 9, 5]
    x_list_backup = [8, 5, 3, 1, 2, 9, 5]
    b_tuple = (8, 5, 3, 1, 2, 9, 5)
    b_tuple_backup = (8, 5, 3, 1, 2, 9, 5)
    a = {"4d": 20, "5a": 10, "3b": 15, "7c": 5, "x": x_list,
         "b": b_tuple}
    b = {"4d": 20, "5a": 10, "3b": 15, "7c": 5, "x": [8, 5, 3, 1, 2, 9, 5],
         "b": (8, 5, 3, 1, 2, 9, 5)}
    c = {"4d": 20, "5a": 10, "3b": 15, "7c": 5, "x": [8, 5, 3, 1, 2, 9, 5],
         "b": (8, 5, 3, 1, 2, 9, 5)}
    d = {"4d": 20, "5a": 10, "3b": 15, "7c": 5, "x": [0, 8, 5, 3, 1, 2, 9, 5],
         "b": (8, 5, 3, 1, 2, 9, 5)}
    # sanity test before any manipulation
    # python can compare dicts natively to this extent
    assert c != d
    assert a == b
    assert a == c
    assert b == c
    assert x_list == x_list_backup
    assert b_tuple == b_tuple_backup
    noexception = False
    try:
        deep_compare(a, b)
        noexception = True
    except:
        pass
    # deep_compare test - the original objects should stay unchanged
    assert noexception
    assert a == b
    assert a == c
    assert b == c
    assert x_list == x_list_backup
    assert b_tuple == b_tuple_backup
