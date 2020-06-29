from insights.parsers.cib import CIB
from insights.tests import context_wrap

CIB_CONFIG = """
    <cib crm_feature_set="3.0.9" validate-with="pacemaker-2.3" have-quorum="1" dc-uuid="4">
      <configuration>
        <crm_config>
          <cluster_property_set id="cib-bootstrap-options">
            <nvpair id="cib-bootstrap-options-have-watchdog" name="have-watchdog" value="false"/>
            <nvpair id="cib-bootstrap-options-no-quorum-policy" name="no-quorum-policy" value="freeze"/>
          </cluster_property_set>
        </crm_config>
        <nodes>
          <node id="1" uname="foo"/>
          <node id="2" uname="bar"/>
          <node id="3" uname="baz"/>
        </nodes>
        <resources>
          <clone id="dlm-clone">
          </clone>
        </resources>
        <constraints>
          <rsc_order first="dlm-clone" first-action="start" id="order-dlm-clone-clvmd-clone-mandatory" then="clvmd-clone" then-action="start"/>
          <rsc_colocation id="colocation-clvmd-clone-dlm-clone-INFINITY" rsc="clvmd-clone" score="INFINITY" with-rsc="dlm-clone"/>
        </constraints>
      </configuration>
    </cib>
"""


def test_cib():
    cib = CIB(context_wrap(CIB_CONFIG, path="/var/lib/pacemaker/cib/cib.xml"))
    assert cib is not None
    assert cib.nodes == ['foo', 'bar', 'baz']


def test_cib_in_sosreport():
    cib = CIB(context_wrap(CIB_CONFIG, path="sos_commands/pacemaker/crm_report/abc/cib.xml"))
    assert cib is not None
    assert cib.nodes == ['foo', 'bar', 'baz']
