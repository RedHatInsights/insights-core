from insights.parsers.heat_log import HeatApiLog
from insights.parsers.heat_log import HeatEngineLog
from insights.tests import context_wrap

from datetime import datetime


HEAT_API_LOG = """
2016-11-09 14:39:29.223 3844 WARNING oslo_config.cfg [-] Option "rpc_backend" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
2016-11-09 14:39:30.612 3844 INFO heat.api [-] Starting Heat REST API on 172.16.2.12:8004
2016-11-09 14:39:30.612 3844 WARNING oslo_reports.guru_meditation_report [-] Guru meditation now registers SIGUSR1 and SIGUSR2 by default for backward compatibility. SIGUSR1 will no longer be registered in a future release, so please use SIGUSR2 to generate reports.
2016-11-09 14:39:30.615 3844 INFO heat.common.wsgi [-] Starting 0 workers
2016-11-09 14:39:30.625 3844 INFO heat.common.wsgi [-] Started child 4136
"""


HEAT_ENGINE_LOG = """
2016-11-09 14:32:44.157 4392 WARNING heat.engine.environment [-] OS::Neutron::PoolMember is DEPRECATED. Neutron LBaaS v1 is deprecated in the Liberty release and is planned to be removed in a future release. Going forward, the LBaaS V2 should be used.
2016-11-09 14:32:44.157 4392 WARNING heat.engine.environment [-] OS::Neutron::HealthMonitor is DEPRECATED. Neutron LBaaS v1 is deprecated in the Liberty release and is planned to be removed in a future release. Going forward, the LBaaS V2 should be used.
2016-11-09 14:32:44.158 4392 WARNING heat.engine.environment [-] OS::Neutron::RouterGateway is HIDDEN. Use the `external_gateway_info` property in the router resource to set up the gateway.
2016-11-09 14:32:44.160 4392 INFO heat.engine.environment [-] Loading /etc/heat/environment.d/default.yaml
2016-11-09 14:32:44.168 4392 INFO heat.engine.environment [-] Registered: [Plugin](User:False) AWS::EC2::Instance -> <class 'heat.engine.resources.aws.ec2.instance.Instance'>
2016-11-09 14:32:45.169 4392 INFO heat.engine.environment [-] Registered: [Plugin](User:False) OS::Heat::AccessPolicy -> <class 'heat.engine.resources.openstack.heat.access_policy.AccessPolicy'>
"""


def test_heat_api_log():
    log = HeatApiLog(context_wrap(HEAT_API_LOG))
    assert len(log.get('INFO')) == 3
    assert len(list(log.get_after(datetime(2016, 11, 9, 14, 39, 30)))) == 4


def test_heat_engine_log():
    log = HeatEngineLog(context_wrap(HEAT_ENGINE_LOG))
    assert len(log.get('INFO')) == 3
    assert len(list(log.get_after(datetime(2016, 11, 9, 14, 32, 45)))) == 1
