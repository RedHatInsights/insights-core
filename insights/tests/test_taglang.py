from insights.core.taglang import parse


def test_simple():
    pred = parse("security")
    assert pred(["security"])
    assert not pred(["logging"])


def test_regex():
    """
    Regexes start with a forward slash (/). If they must contain spaces,
    enclose the regex after the forward slash in quotes.
    """
    pred = parse("/net")
    assert pred(["networking"])
    assert pred(["tenet"])
    assert not pred(["security"])

    pred = parse("/^net")
    assert pred(["networking"])
    assert not pred(["tenet"])
    assert not pred(["security"])

    pred = parse("/'net work'")
    assert pred(["net work"])
    assert not pred(["networking"])
    assert not pred(["tenet"])
    assert not pred(["security"])


def test_negation():
    pred = parse("!security")
    assert not pred(["security", "logging"])
    assert not pred(["security"])
    assert pred(["logging"])
    assert pred(["jboss"])
    assert pred([])


def test_conjunction():
    pred = parse("security & logging")
    assert pred(["security", "logging"])
    assert not pred(["security"])
    assert not pred(["logging"])


def test_disjunction():
    pred = parse("security | logging")
    assert pred(["security", "logging"])
    assert pred(["security"])
    assert pred(["logging"])
    assert not pred(["jboss"])

    # , is a synonym for |
    pred = parse("security, logging")
    assert pred(["security", "logging"])
    assert pred(["security"])
    assert pred(["logging"])
    assert not pred(["jboss"])


def test_precedence():
    """ ! binds more strongly than &, which binds more strongly than | """
    pred = parse("security | logging & !jboss")
    assert pred(["security"])
    assert pred(["logging"])
    assert not pred(["logging", "jboss"])
    assert not pred(["apache", "jboss"])


def test_grouping():
    pred = parse("(security | logging) & jboss")
    assert pred(["security", "jboss"])
    assert pred(["logging", "jboss"])
    assert not pred(["security", "logging"])
    assert not pred(["security"])
    assert not pred(["logging"])
    assert not pred(["jboss"])


def test_regex_in_group():
    """
    A regex at the end of a group must have a space before the closing paren
    or the paren will be considered part of the regex.
    """
    pred = parse("(security | /logging ) & jboss")
    assert pred(["security", "jboss"])
    assert pred(["logging", "jboss"])
    assert not pred(["security", "logging"])
    assert not pred(["security"])
    assert not pred(["logging"])
    assert not pred(["jboss"])


def test_quoted_string():
    # notice the entire string is quoted, so it's a single tag instead of
    # multiple tags connected by operators.
    pred = parse("'(security | /logging ) & jboss'")
    assert pred(['(security | /logging ) & jboss'])
    assert not pred(["security", "jboss"])
    assert not pred(["logging", "jboss"])
