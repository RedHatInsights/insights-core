from insights.parsr import Char, Until


def test_until():
    a = Char("a")
    b = Char("b")
    u = Until(a, b)
    res = u("aaaab")
    assert len(res) == 4
