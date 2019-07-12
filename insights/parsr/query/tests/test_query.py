from insights.parsr.query import all_, any_, lt, Entry, from_dict, startswith, endswith


simple_data = {
    "a": 3,
    "b": ["four", "five"],
    "c": [9, 15],
    "d": {"e": 9.7}
}


complex_tree = Entry(name="root",
                    attrs=[1, 2, 3, 4],
                    children=[
                        Entry(name="child", attrs=[1, 1, 2]),
                        Entry(name="child", attrs=[1, 1, 2, 3, 5]),
                        Entry(name="child", attrs=[1, 1, 3, 5, 9]),
                        Entry(name="dog", attrs=["woof"], children=[
                            Entry(name="puppy", attrs=["smol"]),
                            Entry(name="puppy", attrs=["fluffy"]),
                            Entry(name="kitten", attrs=["wut"]),
                        ])
                    ])


def test_from_dict():
    n = from_dict(simple_data)
    assert n
    assert len(n) == 4


def test_values():
    n = from_dict(simple_data)
    assert n["a"].value == 3

    assert n["b"].value == "four five"
    assert n["b"].string_value == "four five"

    assert n["c"].value == "9 15"
    assert n["c"].string_value == "9 15"

    assert n["d"]["e"].value == 9.7


def test_complex():
    t = complex_tree
    assert len(t["child"]) == 3
    assert len(t["child", 3]) == 2
    assert len(t["child", all_(lt(3))]) == 1
    assert len(t["child", any_(1)]) == 3
    assert len(t["child", any_(9)]) == 1
    assert len(t["child", any_(2)]) == 2
    assert len(t["dog"]["puppy"]) == 2
    assert len(t[startswith("chi") & endswith("ld")]) == 3
    assert len(t[startswith("chi") | startswith("do")]) == 4
