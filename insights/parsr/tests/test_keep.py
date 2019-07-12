from insights.parsr import Colon, QuotedString


def test_keepleft():
    key = QuotedString << Colon
    assert key('"key":') == "key"

    key = Colon << QuotedString
    assert key(':"key"') == ":"


def test_keepright():
    key = QuotedString >> Colon
    assert key('"key":') == ":"

    key = Colon >> QuotedString
    assert key(':"key"') == "key"


def test_middle():
    key = Colon >> QuotedString << Colon
    assert key(':"key":') == "key"
