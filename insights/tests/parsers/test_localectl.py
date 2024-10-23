import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import localectl
from insights.parsers.localectl import LocaleCtlStatus
from insights.tests import context_wrap

LOCALECTL_STATUS_CONTENT = """
   System Locale: LANG=en_US.UTF-8
       VC Keymap: us
      X11 Layout: us
""".strip()

LOCALECTL_STATUS_CONTENT_ERROR = """
   command not fond
""".strip()

LOCALECTL_STATUS_CONTENT_EMPTY = """

""".strip()


def test_localectl_status():
    ret = LocaleCtlStatus(context_wrap(LOCALECTL_STATUS_CONTENT))
    assert ret['System Locale'] == 'LANG=en_US.UTF-8'
    assert ret['VC Keymap'] == 'us'
    assert ret['X11 Layout'] == 'us'


def test_localectl_status_error():
    with pytest.raises(SkipComponent):
        LocaleCtlStatus(context_wrap(LOCALECTL_STATUS_CONTENT_ERROR))


def test_localectl_status_ng():
    with pytest.raises(SkipComponent):
        LocaleCtlStatus(context_wrap(LOCALECTL_STATUS_CONTENT_EMPTY))


def test_doc_examples():
    env = {
            'localectl_status': LocaleCtlStatus(context_wrap(LOCALECTL_STATUS_CONTENT)),
          }
    failed, total = doctest.testmod(localectl, globs=env)
    assert failed == 0
