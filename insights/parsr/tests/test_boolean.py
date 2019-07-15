from insights.parsr import Char


def test_and():
    p = Char("a") + Char("b")
    assert p("ab") == ["a", "b"]


def test_or():
    p = Char("a") | Char("b")
    assert p("a") == "a"
    assert p("b") == "b"
