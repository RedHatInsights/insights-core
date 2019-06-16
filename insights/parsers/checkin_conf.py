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
checkin.conf - Files ``/etc/splice/checkin.conf``
=================================================

Parser for checkin.conf configuration file.

"""

from insights.specs import Specs

from .. import IniConfigFile, parser


@parser(Specs.checkin_conf)
class CheckinConf(IniConfigFile):
    """
    Class for parsing content of "/etc/splice/checkin.conf".

    Sample input::

        [logging]
        config = /etc/splice/logging/basic.cfg

        # this is used only for single-spacewalk deployments
        [spacewalk]
        # Spacewalk/Satellite server to use for syncing data.
        host=
        # Path to SSH private key used to connect to spacewalk host.
        ssh_key_path=
        login=swreport

        # these are used for multi-spacewalk deployments
        # [spacewalk_one]
        # type = ssh
        # # Spacewalk/Satellite server to use for syncing data.
        # host=
        # # Path to SSH private key used to connect to spacewalk host.
        # ssh_key_path=
        # login=swreport
        #
        # [spacewalk_two]
        # type = file
        # # Path to directory containing report output
        # path = /path/to/output

        [katello]
        hostname=localhost
        port=443
        proto=https
        api_url=/sam
        admin_user=admin
        admin_pass=admin
        #autoentitle_systems = False
        #flatten_orgs = False

    Examples:
        >>> list(checkin_conf.sections())
        [u'logging', u'spacewalk', u'katello']
        >>> checkin_conf.get('spacewalk', 'host')
        u''
    """
    pass
