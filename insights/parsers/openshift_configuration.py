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

"""
openshift configuration files
=============================

``/etc/origin/node/node-config.yaml`` and
``/etc/origin/master/master-config.yaml`` are configuration files of
openshift Master node and Node node. Their format are both ``yaml``.

OseNodeConfig - file ``/etc/origin/node/node-config.yaml``
----------------------------------------------------------

Reads the OpenShift node configuration

OseMasterConfig - file ``/etc/origin/master/master-config.yaml``
----------------------------------------------------------------

Reads the Openshift master configuration

Examples:
    >>> result = shared[OseMasterConfig]
    >>> result.data['assetConfig']['masterPublicURL']
    'https://master.ose.com:8443'
    >>> result.data['corsAllowedOrigins'][1]
    'localhost'
"""

from .. import YAMLParser, parser
from insights.specs import Specs


@parser(Specs.ose_node_config)
class OseNodeConfig(YAMLParser):
    """Class to parse ``/etc/origin/node/node-config.yaml``"""
    pass


@parser(Specs.ose_master_config)
class OseMasterConfig(YAMLParser):
    """Class to parse ``/etc/origin/master/master-config.yaml``"""
    pass
