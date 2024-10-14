import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import localectl
from insights.parsers.localectl import Localectl
from insights.tests import context_wrap

LOCALECTL_CONTENT = """
   System Locale: LANG=en_US.UTF-8
       VC Keymap: us
      X11 Layout: us
""".strip()

LOCALECTL_CONTENT_EMPTY = """

""".strip()


def test_localectl():
    ret = Localectl(context_wrap(LOCALECTL_CONTENT))
    assert ret['System Locale'] == 'LANG=en_US.UTF-8'
    assert ret['VC Keymap'] == 'us'
    assert ret['X11 Layout'] == 'us'


def test_localectl_ng():
    with pytest.raises(SkipComponent):
        Localectl(context_wrap(LOCALECTL_CONTENT_EMPTY))


def test_doc_examples():
    env = {
            'localectl': Localectl(context_wrap(LOCALECTL_CONTENT)),
          }
    failed, total = doctest.testmod(localectl, globs=env)
    assert failed == 0
