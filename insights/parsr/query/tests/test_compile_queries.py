from insights.parsr.query import all_, any_, compile_queries, Entry, lt

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


def test_complex():
    t = complex_tree

    q = compile_queries("child")
    assert len(q(t.children)) == 3

    q = compile_queries(("child", 3))
    assert len(q(t.children)) == 2

    q = compile_queries(("child", all_(lt(3))))
    assert len(q(t.children)) == 1

    q = compile_queries(("child", any_(1)))
    assert len(q(t.children)) == 3

    q = compile_queries("dog", "puppy")
    assert len(q(t.children)) == 2
