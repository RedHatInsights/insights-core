"""
SystemctlShow - command ``systemctl show``
==========================================

Parsers included in this module are:

SystemctlShowServiceAll - command ``systemctl show *.service``
--------------------------------------------------------------
SystemctlShowTarget - command ``systemctl show *.target``
---------------------------------------------------------
SystemctlShowAllServiceWithLimitedProperties - command ``systemctl show *.service --all --property=<...>``
----------------------------------------------------------------------------------------------------------
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsers import split_kv_pairs
from insights.specs import Specs


@parser(Specs.systemctl_show_all_services)
class SystemctlShowServiceAll(CommandParser, dict):
    """
    Class for parsing ``systemctl show *.service`` command output.
    Empty properties are suppressed.

    Sample Input::

        Id=postfix.service
        Names=postfix.service
        TimeoutStartUSec=1min 30s
        LimitNOFILE=65536
        LimitMEMLOCK=
        LimitLOCKS=18446744073709551615

        Id=postgresql.service
        Names=postgresql.service
        Requires=basic.target
        LimitMSGQUEUE=819200
        LimitNICE=0

    Sample Output::

        {
            "postfix.service": {
                "Id"               : "postfix.service",
                "Names"            : "postfix.service",
                "LimitNOFILE"      : "65536",
                "TimeoutStartUSec" : "1min 30s",
                "LimitLOCKS"       : "18446744073709551615",
            },
            "postgresql.service": {
                "Id"               : "postgresql.service",
                "Names"            : "postgresql.service",
                "Requires"         : "basic.target",
                "LimitMSGQUEUE"    : "819200",
                "LimitNICE"        : "0",
            }
        }

    Examples:
        >>> 'postfix' in systemctl_show_all  # ".service" is needed
        False
        >>> 'postfix.service' in systemctl_show_all
        True
        >>> systemctl_show_all['postfix.service']['Id']
        'postfix.service'
        >>> 'LimitMEMLOCK' in systemctl_show_all['postfix.service']
        False
        >>> systemctl_show_all['postfix.service']['LimitLOCKS']
        '18446744073709551615'
        >>> 'postgresql.service' in systemctl_show_all
        True
        >>> systemctl_show_all['postgresql.service']['LimitNICE']
        '0'

    Raises:
        SkipComponent: When nothing needs to parse
        ParseException: When something cannot be parsed
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent

        sidx = 0
        idx_list = []
        for i, l in enumerate(content):
            if l.strip() == '':
                idx_list.append((sidx, i))
                sidx = i + 1
        idx_list.append((sidx, len(content)))
        for s, e in idx_list:
            data = split_kv_pairs(content[s:e], use_partition=False)
            name = data.get('Names', data.get('Id'))
            if not name:
                raise ParseException('"Names" or "Id" not found!')
            self[name] = dict((k, v) for k, v in data.items() if v)

        if len(self) == 0:
            raise SkipComponent


@parser(Specs.systemctl_show_target)
class SystemctlShowTarget(SystemctlShowServiceAll):
    """
    Class for parsing ``systemctl show *.target`` command output.
    Empty properties are suppressed.

    This class is inherited from :py:class:`SystemctlShowServiceAll`.

    Sample Input::

        Id=network.target
        Names=network.target
        WantedBy=NetworkManager.service
        Conflicts=shutdown.target
        Before=tuned.service network-online.target rhsmcertd.service kdump.service httpd.service rsyslog.service rc-local.service insights-client.timer insights-client.service sshd.service postfix.service
        After=firewalld.service network-pre.target network.service NetworkManager.service
        Documentation=man:systemd.special(7) http://www.freedesktop.org/wiki/Software/systemd/NetworkTarget
        Description=Network
        LoadState=loaded
        ActiveState=active
        SubState=active
        FragmentPath=/usr/lib/systemd/system/network.target
        UnitFileState=static
        UnitFilePreset=disabled
        InactiveExitTimestamp=Tue 2020-02-25 10:39:46 GMT
        InactiveExitTimestampMonotonic=15332468
        ActiveEnterTimestamp=Tue 2020-02-25 10:39:46 GMT
        ActiveEnterTimestampMonotonic=15332468
        ActiveExitTimestampMonotonic=0
        InactiveEnterTimestampMonotonic=0
        CanStart=no

    Sample Output::

        {'network.target': {'ActiveEnterTimestamp': 'Tue 2020-02-25 10:39:46 GMT',
                            'ActiveEnterTimestampMonotonic': '15332468',
                            'ActiveExitTimestampMonotonic': '0',
                            'ActiveState': 'active',
                            'After': 'firewalld.service network-pre.target '
                                     'network.service NetworkManager.service',
                            'Before': 'tuned.service network-online.target '
                                      'rhsmcertd.service kdump.service httpd.service '
                                      'rsyslog.service rc-local.service '
                                      'insights-client.timer insights-client.service '
                                      'sshd.service postfix.service',
                            'CanStart': 'no',
                            'Conflicts': 'shutdown.target',
                            'Description': 'Network',
                            'Documentation': 'man:systemd.special(7) '
                                             'http://www.freedesktop.org/wiki/Software/systemd/NetworkTarget',
                            'FragmentPath': '/usr/lib/systemd/system/network.target',
                            'Id': 'network.target',
                            'InactiveEnterTimestampMonotonic': '0',
                            'InactiveExitTimestamp': 'Tue 2020-02-25 10:39:46 GMT',
                            'InactiveExitTimestampMonotonic': '15332468',
                            'LoadState': 'loaded',
                            'Names': 'network.target',
                            'SubState': 'active',
                            'UnitFilePreset': 'disabled',
                            'UnitFileState': 'static',
                            'WantedBy': 'NetworkManager.service'})

    Examples:
        >>> 'network.target' in systemctl_show_target
        True
        >>> systemctl_show_target.get('network.target').get('WantedBy', None)
        'NetworkManager.service'
        >>> systemctl_show_target.get('network.target').get('RequiredBy', None)

    Raises:
        SkipComponent: When nothing needs to parse
        ParseException: When something cannot be parsed
    """
    pass


@parser(Specs.systemctl_show_all_services_with_limited_properties)
class SystemctlShowAllServiceWithLimitedProperties(SystemctlShowServiceAll):
    """
    Class for parsing the output of command ``systemctl show *.service --all --property=<...>``.

    Sample Input::

        CPUAccounting=no
        CPUShares=18446744073709551615
        StartupCPUShares=18446744073709551615
        CPUQuotaPerSecUSec=infinity
        Names=test1.service
        SubState=dead
        UnitFileState=static

        CPUAccounting=yes
        CPUShares=18446744073709551615
        StartupCPUShares=18446744073709551615
        CPUQuotaPerSecUSec=infinity
        Names=test2.service
        SubState=dead
        UnitFileState=enabled

    Sample Output::

        {'test1.service': {
            'Names': 'test1.service',
            'SubState': 'dead',
            'UnitFileState': 'static',
            'CPUQuotaPerSecUSec': 'infinity',
            'CPUShares': '18446744073709551615',
            'StartupCPUShares': '18446744073709551615',
            'CPUAccounting': 'no'
            },
        'test2.service': {
            'Names': 'test2.service',
            'SubState': 'dead',
            'UnitFileState': 'enabled',
            'CPUQuotaPerSecUSec': 'infinity',
            'CPUShares': '18446744073709551615',
            'StartupCPUShares': '18446744073709551615',
            'CPUAccounting': 'yes'
            }
        }

    Examples:
        >>> 'test1.service' in all_services_with_limited_info
        True
        >>> all_services_with_limited_info.get('test1.service').get('CPUAccounting', None)
        'no'
        >>> 'test2.service' in all_services_with_limited_info.get_services_with_cpuaccouting_enabled()
        True
    """

    def get_services_with_cpuaccouting_enabled(self):
        """Return a list of service names which enables the CPUAccounting."""
        services_with_cpuaccouting_enabled = []
        for service_name, service_info in self.items():
            service_enabled_or_stared = (
                service_info.get('UnitFileState') in ['static', 'enabled'] or
                service_info.get('SubState') in ['running', 'failed', 'dead', 'exited'])
            cpuaccounting_enabled = (
                service_info.get('CPUAccounting', '').lower() == 'yes' or
                service_info.get('CPUQuotaPerSecUSec', '').lower() != 'infinity')
            val1 = service_info.get('CPUShares')
            val2 = service_info.get('StartupCPUShares')
            # From the man page of systemctl, the value of CPUShares is the range 2 and 262144
            if any(v.isdigit() and 2 <= int(v) <= 262144 for v in (val1, val2)):
                cpuaccounting_enabled = True
            if service_enabled_or_stared and cpuaccounting_enabled:
                services_with_cpuaccouting_enabled.append(service_name)
        return services_with_cpuaccouting_enabled
