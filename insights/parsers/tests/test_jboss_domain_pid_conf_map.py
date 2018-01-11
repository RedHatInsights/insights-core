from ...parsers.jboss_domain_pid_conf_map import JbossDomainPidConfMap
from ...parsers import jboss_domain_pid_conf_map
from ...tests import context_wrap
import doctest

PID_CONF_MAP_1 = '2043|/home/jboss/jboss/machine1/domain/host-master.xml|/home/jboss/jboss/machine1/domain/domain.xml'


def test_jboss_domain_pid_conf_map():
    pid1 = JbossDomainPidConfMap(context_wrap(PID_CONF_MAP_1))
    assert pid1.get(2043) == (
        "/home/jboss/jboss/machine1/domain/host-master.xml", "/home/jboss/jboss/machine1/domain/domain.xml")


def test_jboss_domain_pid_conf_map_doc_examples():
    env = {
        'JbossDomainPidConfMap': JbossDomainPidConfMap,
        'jboss_pid_conf_map': JbossDomainPidConfMap(context_wrap(PID_CONF_MAP_1))
    }
    failed, total = doctest.testmod(jboss_domain_pid_conf_map, globs=env)
    assert failed == 0
