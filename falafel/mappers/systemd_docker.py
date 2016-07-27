import ConfigParser as cp
import StringIO
from falafel.core.plugins import mapper


@mapper('docker.service')
def systemd_docker_service_parser(context):
    """
    The content of file "/usr/lib/systemd/system/docker.service" is recorded via INI format,
    ConfigParser could be used to parse the content.

    Example:
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
    "Unit":{"Description":"Docker Application Container Engine", "After":"network.target"...}
    "Service":{"Type":"notify", "NotifyAccess":"all"...}
    "Install":{"WantedBy":"multi-user.target"...}
    }
    """

    Config = cp.ConfigParser()

    Config.optionxform = str
    buf = StringIO.StringIO('\n'.join(context.content))
    Config.readfp(buf)

    sections = Config.sections()
    dict_all = {}
    dict_section = {}

    for section in sections:
        options = Config.options(section)
        for option in options:
            dict_section[option] = Config.get(section, option)
        dict_all[section] = dict_section

    return dict_all
