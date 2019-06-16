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
NeutronConf - file ``/etc/neutron/neutron.conf``
================================================

This class provides parsing for the file ``/etc/neutron/neutron.conf``.

Sample input data is in the format::

    [DEFAULT]
    # debug = False
    debug = False
    # verbose = True
    verbose = False
    core_plugin =neutron.plugins.openvswitch.ovs_neutron_plugin.OVSNeutronPluginV2

    [quotas]
    default_quota = -1
    quota_network = 10
    [agent]
    report_interval = 60

    [keystone_authtoken]
    auth_host = ost-controller-lb-del.om-l.dsn.inet
    auth_port = 35357

See the ``IniConfigFile`` class for examples.
"""
from .. import IniConfigFile, parser, add_filter
from insights.specs import Specs

add_filter(Specs.neutron_conf, ["["])


@parser(Specs.neutron_conf)
class NeutronConf(IniConfigFile):
    """Class to parse file ``neutron.conf``."""
    pass
