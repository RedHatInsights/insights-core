#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
    cib = CIB(context_wrap(CIB_CONFIG))
    assert cib is not None
    assert cib.nodes == ['foo', 'bar', 'baz']
