"""
SystemD service configuration
=============================

Service systemd files are in ``/usr/lib/systemd/system``, and their content
format is similar to a '.ini' file.

Parsers included in this module are:

SystemdDocker - file ``/usr/lib/systemd/system/docker.service``
---------------------------------------------------------------

SystemdOpenshiftNode - file ``/usr/lib/systemd/system/atomic-openshift-node.service``
-------------------------------------------------------------------------------------

SystemdSystemConf - file ``/etc/systemd/system.conf``
-----------------------------------------------------

"""

from insights.configtree.iniconfig import parse_doc
from insights.core import Parser, LegacyItemAccess
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.systemd_docker)
class SystemdDocker(Parser):
    """Class for docker systemd configuration.

    The content of file ``/usr/lib/systemd/system/docker.service`` is recorded
    in INI format, ``ConfigParser`` could be used to parse the content.

    Sample file content is::

        [Service]
        Type=notify
        EnvironmentFile=-/etc/sysconfig/docker
        EnvironmentFile=-/etc/sysconfig/docker-storage
        EnvironmentFile=-/etc/sysconfig/docker-network
        Environment=GOTRACEBACK=crash
        ExecStart=/bin/sh -c '/usr/bin/docker-current daemon \\
        --authorization-plugin=rhel-push-plugin \\
        --exec-opt native.cgroupdriver=systemd \\
        $OPTIONS \\
        $DOCKER_STORAGE_OPTIONS \\
        $DOCKER_NETWORK_OPTIONS \\
        $ADD_REGISTRY \\
        $BLOCK_REGISTRY \\
        $INSECURE_REGISTRY \\
        2>&1 | /usr/bin/forward-journald -tag docker'
        LimitNOFILE=1048576

    Example:
        >>> docker_content = '''
        [Service]
        Type=notify
        EnvironmentFile=-/etc/sysconfig/docker
        EnvironmentFile=-/etc/sysconfig/docker-storage
        EnvironmentFile=-/etc/sysconfig/docker-network
        Environment=GOTRACEBACK=crash
        ExecStart=/bin/sh -c '/usr/bin/docker-current daemon \\
                  --authorization-plugin=rhel-push-plugin \\
                  --exec-opt native.cgroupdriver=systemd \\
                  $OPTIONS \\
                  $DOCKER_STORAGE_OPTIONS \\
                  $DOCKER_NETWORK_OPTIONS \\
                  $ADD_REGISTRY \\
                  $BLOCK_REGISTRY \\
                  $INSECURE_REGISTRY \\
                  2>&1 | /usr/bin/forward-journald -tag docker'
        LimitNOFILE=1048576
        '''.strip()

        >>> from insights.tests import context_wrap
        >>> shared = {SystemdDocker: SystemdDocker(context_wrap(docker_content))}
        >>> docker_config_info = shared[SystemdDocker]
        >>> docker_config_info["Service"]["ExecStart"]
        "/bin/sh -c '/usr/bin/docker-current daemon --authorization-plugin=rhel-push-plugin --exec-opt native.cgroupdriver=systemd $OPTIONS $DOCKER_STORAGE_OPTIONS $DOCKER_NETWORK_OPTIONS $ADD_REGISTRY $BLOCK_REGISTRY $INSECURE_REGISTRY 2>&1 | /usr/bin/forward-journald -tag docker'"
        >>> len(docker_config_info["Service"]["EnvironmentFile"])
        3
    """

    def parse_content(self, content):
        self.data = parse_systemd_ini(content)


@parser(Specs.systemd_system_conf)
class SystemdSystemConf(LegacyItemAccess, Parser):
    """Class for systemd master configuration in the
    ``/etc/systemd/system.conf`` file.

    Systemd configuration files are recorded via INI format as well, we can
    share the same parser ``ConfigParser`` here.

    Typical output of the ``systemd_system.conf`` command is::

        [Manager]
        RuntimeWatchdogSec=0
        ShutdownWatchdogSec=10min

    Example:
        >>> systemd_content = '''
        [Manager]
        RuntimeWatchdogSec=0
        ShutdownWatchdogSec=10min
        ...
        '''.strip()

        >>> from insights.tests import context_wrap
        >>> shared = {SystemdSystemConf: SystemdSystemConf(context_wrap(systemd_content))}
        >>> systemd_config_info = shared[SystemdSystemConf]
        >>> systemd_config_info["Manager"]["RuntimeWatchdogSec"]
        "0"
    """

    def parse_content(self, content):
        self.data = parse_systemd_ini(content)

    def __contains__(self, conf):
        return conf in self.data


@parser(Specs.systemd_openshift_node)
class SystemdOpenshiftNode(Parser):
    """Class for atomic-openshift-node systemd configuration.

    The content of file ``/usr/lib/systemd/system/atomic-openshift-node.service``
    is recorded via INI format, ``ConfigParser`` could be used to parse the content.

    Typical output of the ``systemd_openshift_node`` command is::

        [Service]
        Type=notify
        RestartSec=5s
        OOMScoreAdjust=-999
        ExecStartPost=/usr/bin/sleep 10
        ExecStartPost=/usr/sbin/sysctl --system

    Example:
        >>> openshift_content = '''
        [Service]
        Type=notify
        RestartSec=5s
        OOMScoreAdjust=-999
        ExecStartPost=/usr/bin/sleep 10
        ExecStartPost=/usr/sbin/sysctl --system
        ...
        '''.strip()

        >>> from insights.tests import context_wrap
        >>> shared = {SystemdOpenshiftNode: SystemdOpenshiftNode(context_wrap(openshift_content))}
        >>> openshift_config_info = shared[SystemdOpenshiftNode]
        >>> openshift_config_info["Service"]["RestartSec"]
        "5s"
        >>> len(openshift_config_info["Service"]["ExecStartPost"])
        2
    """

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

    doc = parse_doc(content)

    dict_all = {}
    for section in doc:
        section_dict = {}
        option_names = set(o.name for o in section)
        for name in option_names:
            options = [str(o.value) for o in section[name]]
            section_dict[name] = options[0] if len(options) == 1 else options
        dict_all[section.name] = section_dict

    return dict_all
