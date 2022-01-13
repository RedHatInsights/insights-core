"""
checkin.conf - Files ``/etc/splice/checkin.conf``
=================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


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
        >>> type(checkin_conf)
        <class 'insights.parsers.checkin_conf.CheckinConf'>
        >>> checkin_conf.sections()
        ['logging', 'spacewalk', 'katello']
        >>> checkin_conf.get('spacewalk', 'host')
        ''
        >>> checkin_conf.get('katello', 'hostname')
        'localhost'
        >>> checkin_conf.getint('katello', 'port')
        443
    """
    pass
