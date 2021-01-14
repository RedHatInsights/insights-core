import pytest
import doctest
from insights.tests import context_wrap
from insights.parsers.proc_environ import ProcEnviron
from insights.parsers.ps import PsAuxcww
from insights.combiners.ps import Ps
from insights.combiners.proc_environ import ProcEnvironAll
from insights.combiners import proc_environ

PS_AUXCWW = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.1  0.0 195712  7756 ?        Ss    2019 477:10 systemd
root         2  0.0  0.0      0     0 ?        S     2019   1:04 kthreadd
root         3  0.0  0.0      0     0 ?        S     2019  36:41 ksoftirqd/0
root         8  0.0  0.0      0     0 ?        S     2019  31:50 migration/0
root         9  0.1  0.0      0     0 ?        S     2019   0:00 rcu_bh
root       131  0.1  0.0      0     0 ?        S     2019  05:00 openshift-route
"""

PROC_ENVIRON_EMPTY = """
""".strip()

PROC_ENVIRON_ERR = """
REGISTRIES
""".strip()

PROC_ENVIRON = """
REGISTRIES=--add-registry registry.access.redhat.com \x00OPTIONS= --selinux-enabled       --signature-verification=False\x00DOCKER_HTTP_HOST_COMPAT=1\x00ADD_REGISTRY=--add-registry registry.access.redhat.com\x00PATH=/usr/libexec/docker:/usr/bin:/usr/sbin\x00PWD=/run/docker/libcontainerd/containerd/135240dbd15a834acb21d68867930917afcc84c5f006ba65004acd88dccab756/init\x00LANG=en_US.UTF-8\x00GOTRACEBACK=crash\x00DOCKER_NETWORK_OPTIONS= --mtu=1450\x00DOCKER_CERT_PATH=/etc/docker\x00SHLVL=0\x00DOCKER_STORAGE_OPTIONS=--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/docker--vg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true \x00
""".strip()

OPENSHIFT_ROUTE_ENVIRON = """
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\x00HOSTNAME=node1\x00ROUTER_EXTERNAL_HOST_HOSTNAME=\x00ROUTER_METRICS_TLS_CERT_FILE=/etc/pki/tls/metrics/tls.crt\x00ROUTER_METRICS_TLS_KEY_FILE=/etc/pki/tls/metrics/tls.key\x00STATS_PASSWORD=9cBJqkmTE6\x00ROUTER_MAX_CONNECTIONS=25000\x00DEFAULT_CERTIFICATE_DIR=/etc/pki/tls/private\x00ROUTER_EXTERNAL_HOST_INSECURE=false\x00ROUTER_EXTERNAL_HOST_PASSWORD=\x00ROUTER_SERVICE_HTTP_PORT=80\x00ROUTER_CIPHERS=\x00ROUTER_EXTERNAL_HOST_INTERNAL_ADDRESS=\x00ROUTER_LISTEN_ADDR=0.0.0.0:1936\x00ROUTER_METRICS_TYPE=haproxy\x00ROUTER_SERVICE_NAME=router\x00ROUTER_EXTERNAL_HOST_USERNAME=\x00DEFAULT_CERTIFICATE_PATH=/etc/pki/tls/private/tls.crt\x00ROUTER_EXTERNAL_HOST_HTTPS_VSERVER=\x00ROUTER_EXTERNAL_HOST_PARTITION_PATH=\x00ROUTER_SERVICE_NAMESPACE=default\x00STATS_USERNAME=admin\x00ROUTER_EXTERNAL_HOST_PRIVKEY=/etc/secret-volume/router.pem\x00RELOAD_INTERVAL=10s\x00ROUTER_EXTERNAL_HOST_HTTP_VSERVER=\x00ROUTER_EXTERNAL_HOST_VXLAN_GW_CIDR=\x00ROUTER_SERVICE_HTTPS_PORT=443\x00ROUTER_SUBDOMAIN=\x00STATS_PORT=1936\x00ROUTER_SERVICE_PORT_443_TCP=443\x00ROUTER_PORT_80_TCP_PORT=80\x00KUBERNETES_PORT_443_TCP_PROTO=tcp\x00KUBERNETES_PORT_443_TCP_ADDR=172.30.0.1\x00KUBERNETES_PORT_53_UDP_PROTO=udp\x00KUBERNETES_PORT_53_UDP_PORT=53\x00REGISTRY_CONSOLE_SERVICE_HOST=172.30.207.124\x00REGISTRY_CONSOLE_PORT=tcp://172.30.207.124:9000\x00ROUTER_PORT_1936_TCP=tcp://172.30.106.114:1936\x00DOCKER_REGISTRY_SERVICE_HOST=172.30.43.64\x00DOCKER_REGISTRY_PORT=tcp://172.30.43.64:5000\x00KUBERNETES_PORT=tcp://172.30.0.1:443\x00ROUTER_PORT_80_TCP_ADDR=172.30.106.114\x00ROUTER_PORT_443_TCP_PORT=443\x00DOCKER_REGISTRY_SERVICE_PORT_5000_TCP=5000\x00DOCKER_REGISTRY_PORT_5000_TCP_ADDR=172.30.43.64\x00KUBERNETES_SERVICE_PORT=443\x00ROUTER_SERVICE_PORT_1936_TCP=1936\x00KUBERNETES_PORT_53_TCP=tcp://172.30.0.1:53\x00KUBERNETES_PORT_53_TCP_ADDR=172.30.0.1\x00KUBERNETES_SERVICE_PORT_HTTPS=443\x00KUBERNETES_SERVICE_PORT_DNS=53\x00REGISTRY_CONSOLE_PORT_9000_TCP_PROTO=tcp\x00REGISTRY_CONSOLE_PORT_9000_TCP_PORT=9000\x00ROUTER_PORT_80_TCP=tcp://172.30.106.114:80\x00ROUTER_PORT_443_TCP=tcp://172.30.106.114:443\x00ROUTER_PORT_443_TCP_PROTO=tcp\x00DOCKER_REGISTRY_PORT_5000_TCP_PROTO=tcp\x00KUBERNETES_SERVICE_PORT_DNS_TCP=53\x00KUBERNETES_PORT_443_TCP_PORT=443\x00KUBERNETES_PORT_53_UDP=udp://172.30.0.1:53\x00KUBERNETES_PORT_53_TCP_PORT=53\x00REGISTRY_CONSOLE_SERVICE_PORT_REGISTRY_CONSOLE=9000\x00REGISTRY_CONSOLE_PORT_9000_TCP_ADDR=172.30.207.124\x00ROUTER_PORT_80_TCP_PROTO=tcp\x00ROUTER_PORT_1936_TCP_PORT=1936\x00DOCKER_REGISTRY_PORT_5000_TCP=tcp://172.30.43.64:5000\x00KUBERNETES_PORT_53_UDP_ADDR=172.30.0.1\x00ROUTER_SERVICE_PORT_80_TCP=80\x00ROUTER_PORT_443_TCP_ADDR=172.30.106.114\x00DOCKER_REGISTRY_PORT_5000_TCP_PORT=5000\x00KUBERNETES_SERVICE_HOST=172.30.0.1\x00ROUTER_PORT_1936_TCP_ADDR=172.30.106.114\x00DOCKER_REGISTRY_SERVICE_PORT=5000\x00REGISTRY_CONSOLE_SERVICE_PORT=9000\x00REGISTRY_CONSOLE_PORT_9000_TCP=tcp://172.30.207.124:9000\x00ROUTER_SERVICE_HOST=172.30.106.114\x00ROUTER_SERVICE_PORT=80\x00ROUTER_PORT=tcp://172.30.106.114:80\x00ROUTER_PORT_1936_TCP_PROTO=tcp\x00KUBERNETES_PORT_443_TCP=tcp://172.30.0.1:443\x00KUBERNETES_PORT_53_TCP_PROTO=tcp\x00container=oci\x00HOME=/root\x00KUBECONFIG=/var/lib/origin/openshift.local.config/master/admin.kubeconfig\x00TEMPLATE_FILE=/var/lib/haproxy/conf/haproxy-config.template\x00RELOAD_SCRIPT=/var/lib/haproxy/reload-haproxy\x00
"""

OPENSHIFT_FLUENTD_ENVIRON = """
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\x00container=oci\x00LOGGING_FILE_SIZE=1024000\x00LOGGING_FILE_AGE=10\x00LOGGING_FILE_PATH=/var/log/fluentd/fluentd.log\x00
"""


def test_proc_environ_all():
    ret1 = ProcEnviron(context_wrap(PROC_ENVIRON, path='/proc/8/environ'))
    ret2 = ProcEnviron(context_wrap(OPENSHIFT_ROUTE_ENVIRON, path='/proc/9/environ'))
    ret3 = ProcEnviron(context_wrap(OPENSHIFT_FLUENTD_ENVIRON, path='/proc/131/environ'))
    ps = Ps(None, None, None, None, PsAuxcww(context_wrap(PS_AUXCWW)), None)
    pes = ProcEnvironAll([ret1, ret2, ret3], ps)
    assert pes[0]['REGISTRIES'] == '--add-registry registry.access.redhat.com'
    assert 'OPTIONS' in pes[0]
    assert pes[0].pid == 8
    assert pes[1]['RELOAD_INTERVAL'] == '10s'
    assert pes[2]['LOGGING_FILE_SIZE'] == '1024000'
    assert pes.get_environ_of_proc('openshift-route').pid == 131


def test_proc_environ_doc_examples():
    ret1 = ProcEnviron(context_wrap(PROC_ENVIRON, path='/proc/8/environ'))
    ret2 = ProcEnviron(context_wrap(OPENSHIFT_ROUTE_ENVIRON, path='/proc/9/environ'))
    ret3 = ProcEnviron(context_wrap(OPENSHIFT_FLUENTD_ENVIRON, path='/proc/131/environ'))
    ps = Ps(None, None, None, None, PsAuxcww(context_wrap(PS_AUXCWW)), None)
    env = {
        'proc_envs': ProcEnvironAll([ret1, ret2, ret3], ps)
    }
    failed, total = doctest.testmod(proc_environ, globs=env)
    assert failed == 0
