import doctest
import pytest

from insights.parsers import du_candlepin_activemq_artemis
from insights.tests import context_wrap
from insights.core.plugins import ContentException

DU_ACTIVEMQ = """
725320	/var/lib/candlepin/activemq-artemis
""".strip()

DU_MISSING = """
/bin/du: cannot access '/var/lib/candlepin/activemq-artemis': No such file or directory
""".strip()


def test_du_candlepin_activemq_artemis():
    du_candlepin_activemq = du_candlepin_activemq_artemis.DuVarLibCandlepinActivemqArtemis(context_wrap(DU_ACTIVEMQ))
    assert du_candlepin_activemq == {'/var/lib/candlepin/activemq-artemis': 725320}
    assert '/var/lib/candlepin/activemq-artemis' in du_candlepin_activemq
    assert du_candlepin_activemq.get('/var/lib/candlepin/activemq-artemis') == 725320

    with pytest.raises(ContentException) as exc:
        du_candlepin_activemq_artemis.DiskUsage(context_wrap(DU_MISSING))
    assert 'No such file or directory' in str(exc)

def test_du_candlepin_activemq_artemis_doc_examples():
    env = {'du_candlepin_activemq': du_candlepin_activemq_artemis.DuVarLibCandlepinActivemqArtemis(context_wrap(DU_ACTIVEMQ))}
    failed, total = doctest.testmod(du_candlepin_activemq_artemis, globs=env)
    assert failed == 0
