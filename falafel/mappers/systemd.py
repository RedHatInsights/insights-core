import ConfigParser as cp
import StringIO
from falafel.core.plugins import mapper


@mapper('systemd_docker')
def docker(context):
    """
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
    return parse_systemd_ini(context.content)


def parse_systemd_ini(content):
    Config = cp.ConfigParser()
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
