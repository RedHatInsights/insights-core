from insights.parsr import Char


def boom(_):
    raise Exception("Boom")


def test_error():
    p = Char("a").map(boom)
    try:
        p("a")
    except Exception as ex:
        assert "boom" in str(ex)
