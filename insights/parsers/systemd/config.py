"""
Service systemd file - File
===========================
Service systemd files are in ``/usr/lib/systemd/system``, and Their content format is
``config``.
"""

from ConfigParser import RawConfigParser as cp
import StringIO
from insights.core import Parser, LegacyItemAccess
from insights.core.plugins import parser


@parser('systemd_docker')
class SystemdDocker(Parser):
    """Class for docker systemd configuration.

    The content of file ``/usr/lib/systemd/system/docker.service`` is recorded
    via INI format, ``ConfigParser`` could be used to parse the content.

    Example::

        [Unit]
        Description=Docker Application Container Engine
        Documentation=http://docs.docker.com
        After=network.target
        Wants=docker-storage-setup.service
        Requires=rhel-push-plugin.socket

        [Service]
        Type=notify
        NotifyAccess=all
        EnvironmentFile=-/etc/sysconfig/docker
        EnvironmentFile=-/etc/sysconfig/docker-storage
        EnvironmentFile=-/etc/sysconfig/docker-network
        Environment=GOTRACEBACK=crash
        ExecStart=/bin/sh -c '/usr/bin/docker-current daemon \
             --authorization-plugin=rhel-push-plugin \
             --exec-opt native.cgroupdriver=systemd \
             $OPTIONS \
             $DOCKER_STORAGE_OPTIONS \
             $DOCKER_NETWORK_OPTIONS \
             $ADD_REGISTRY \
             $BLOCK_REGISTRY \
             $INSECURE_REGISTRY \
             2>&1 | /usr/bin/forward-journald -tag docker'
        Restart=on-abnormal
        StandardOutput=null
        StandardError=null

        [Install]
        WantedBy=multi-user.target

    Parse Result::

        {
            "Unit":{
                "Description": "Docker Application Container Engine",
                "After": "network.target"
                ...
            },
            "Service": {
                "Type": "notify",
                "NotifyAccess": "all"
                ...
            }
            "Install":{
                "WantedBy": "multi-user.target"
                ...
            }
        }
    """

    def parse_content(self, content):
        self.data = parse_systemd_ini(content)


@parser('systemd_system.conf')
class SystemdSystemConf(LegacyItemAccess, Parser):
    """Class for system systemd configuration.

    Systemd configuration files are recorded via INI format as well, we can
    share the same parser ``ConfigParser`` here.

    Example::

        [Manager]
        LogLevel=info
        LogTarget=journal-or-kmsg
        ...

    Parse Result::

        {
            "Manager":{
                "LogLevel": "info",
                "LogTarget": "journal-or-kmsg",
                ...
            }
        }

    """

    def parse_content(self, content):
        self.data = parse_systemd_ini(content)

    def __contains__(self, conf):
        return conf in self.data


@parser('systemd_openshift_node')
class SystemdOpenshiftNode(Parser):
    """Class for atomic-openshift-node systemd configuration. Example is like SystemdDocker"""
    def parse_content(self, content):
        self.data = parse_systemd_ini(content)


class MultiOrderedDict(dict):
    """Class for condition that duplicate keys exist"""
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(MultiOrderedDict, self).__setitem__(key, value)


def parse_systemd_ini(content):
    """Function to parse config format file, the result format is dictionary"""
    Config = cp(dict_type=MultiOrderedDict)
    Config.optionxform = str
    Config.readfp(StringIO.StringIO('\n'.join(content)))

    dict_all = {}
    for section in Config.sections():
        dict_section = {}
        for option in Config.options(section):
            value = Config.get(section, option).splitlines()
            value = map(lambda s: s.rstrip("\\").strip(), value)
            value = filter(lambda s: bool(s), value)
            dict_section[option] = "\n".join(value)
        dict_all[section] = dict_section

    return dict_all
