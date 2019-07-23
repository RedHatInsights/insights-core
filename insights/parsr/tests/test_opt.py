from insights.parsr import Char, Opt


def test_opt():
    a = Opt(Char("a"))
    assert a("a") == "a"
    assert a("b") is None


def test_opt_default():
    a = Opt(Char("a"), "Default")
    assert a("b") == "Default"
