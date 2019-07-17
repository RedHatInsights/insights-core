from insights.parsr.examples.arith import evaluate


def test_single_ops():
    assert evaluate("2+3") == 5
    assert evaluate("1-3") == -2
    assert evaluate("2*3") == 6
    assert evaluate("4/2") == 2


def test_multiple_ops():
    assert evaluate("2+3+4") == 9
    assert evaluate("1-3+2") == 0
    assert evaluate("2*3*4") == 24
    assert evaluate("3*4/2") == 6


def test_nested():
    assert evaluate("24-2*(3+4)") == 10


def test_spaces():
    assert evaluate("24 - 2 * ( 3 + 4 )") == 10
