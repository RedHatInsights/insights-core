from insights.parsr import Literal


def test_literal():
    p = Literal("123")
    assert p("123") == "123"


def test_literal_value():
    p = Literal("true", value=True)
    assert p("true") is True


def test_literal_ignore_case():
    p = Literal("true", ignore_case=True)
    assert p("TrUe") == "TrUe"


def test_literal_value_ignore_case():
    p = Literal("true", value=True, ignore_case=True)
    assert p("TRUE") is True
