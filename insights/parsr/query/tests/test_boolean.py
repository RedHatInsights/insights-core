from insights.parsr.query.boolean import TRUE, FALSE


def test_and():
    q = TRUE & TRUE
    assert q(None)

    q = TRUE & FALSE
    assert not q(None)

    q = FALSE & TRUE
    assert not q(None)

    q = FALSE & FALSE
    assert not q(None)


def test_or():
    q = TRUE | TRUE
    assert q(None)

    q = TRUE | FALSE
    assert q(None)

    q = FALSE | TRUE
    assert q(None)

    q = FALSE | FALSE
    assert not q(None)


def test_not():
    q = ~FALSE
    assert q(None)
    q = ~TRUE
    assert not q(None)
