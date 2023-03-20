from insights.parsers.transparent_hugepage import ThpEnabled, ThpUseZeroPage
from insights.tests import context_wrap

ZEROPAGE_0 = "0"
ZEROPAGE_1 = "1"
ZEROPAGE_INVALID = """
bla
ble
asdf


"""

ENABLED_INVALID = """

asdf fda asdfdsaf
"""

ENABLED_MADVISE = """
always [madvise] never
"""

ENABLED_NEVER = """
always madvise [never]
"""

# testing without newlines
ENABLED_ALWAYS = """[always] madvise never"""


def test_zeropage():
    conf = ThpUseZeroPage(context_wrap(ZEROPAGE_0))
    assert conf is not None
    assert "0" == conf.use_zero_page

    conf = ThpUseZeroPage(context_wrap(ZEROPAGE_1))
    assert conf is not None
    assert "1" == conf.use_zero_page

    conf = ThpUseZeroPage(context_wrap(ZEROPAGE_INVALID))
    assert conf is not None
    assert ZEROPAGE_INVALID.replace("\n", " ").strip() == conf.use_zero_page


def test_enabled():
    conf = ThpEnabled(context_wrap(ENABLED_INVALID))
    assert conf is not None
    assert None is conf.active_option
    assert ENABLED_INVALID.strip() == conf.line

    conf = ThpEnabled(context_wrap(ENABLED_MADVISE))
    assert conf is not None
    assert "madvise" == conf.active_option
    assert ENABLED_MADVISE.strip() == conf.line

    conf = ThpEnabled(context_wrap(ENABLED_NEVER))
    assert conf is not None
    assert "never" == conf.active_option
    assert ENABLED_NEVER.strip() == conf.line

    conf = ThpEnabled(context_wrap(ENABLED_ALWAYS))
    assert conf is not None
    assert "always" == conf.active_option
    assert ENABLED_ALWAYS.strip() == conf.line
