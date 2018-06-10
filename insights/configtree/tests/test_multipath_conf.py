from insights.configtree import first, last
from insights.configtree.multipath_conf import MultipathConf
from insights.tests import context_wrap


CONF = """
blacklist {
       device {
               vendor  "IBM"
               product "3S42"       #DS4200 Product 10
       }
       device {
               vendor  "HP"
               product "*"
       }
}""".strip()


def test_multipath_conf():
    conf = MultipathConf(context_wrap(CONF))
    assert len(conf["blacklist"]) == 1
    assert len(conf["blacklist"]["device"]) == 2

    assert len(conf["blacklist"]["device"]["vendor"]) == 2
    assert len(conf["blacklist"]["device"]["product"]) == 2

    assert conf["blacklist"]["device"]["vendor"][first].value == "IBM"
    assert conf["blacklist"]["device"]["vendor"][last].value == "HP"

    assert conf["blacklist"]["device"]["product"][first].value == "3S42"
    assert conf["blacklist"]["device"]["product"][last].value == "*"
