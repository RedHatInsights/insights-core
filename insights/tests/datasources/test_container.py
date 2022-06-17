from mock.mock import Mock
from insights.parsers.docker_list import DockerListContainers
from insights.specs.datasources.container import (
    docker_running_container_ids, docker_running_container_nginx_conf, LocalSpecs
)
from insights.tests import context_wrap


DOCKER_PS = """
CONTAINER ID                                                       IMAGE               COMMAND                                          CREATED             STATUS                    PORTS                              NAMES
947c8fd31e140b1ab243880594d6260530cd3a76fb60ef6ef7ce6a4c4ea9f104   4fb75d56564b        "container-entrypoint nginx -g 'daemon off;'"    49 minutes ago      Up 49 minutes             0.0.0.0:8080->8080/tcp, 8443/tcp   nginx
cb81e60ef8a29212476e560cc5149b04dc06de54eb5e25011b7d700317ec543a   nginx               "/docker-entrypoint.sh nginx -g 'daemon off;'"   2 days ago          Exited (0) 16 hours ago                                      mynginx1
""".strip()


DOCKER_FIND = """
/etc/libssh/libssh_client.config
/etc/libssh/libssh_server.config
/etc/libuser.conf
/etc/krb5.conf.d
/etc/dnf/protected.d/setup.conf
/etc/dnf/protected.d/redhat-release.conf
/etc/dnf/protected.d/systemd.conf
/etc/dnf/protected.d/dnf.conf
/etc/dnf/protected.d/yum.conf
/etc/dnf/plugins/subscription-manager.conf
/etc/dnf/plugins/product-id.conf
/etc/dnf/plugins/debuginfo-install.conf
/etc/dnf/plugins/copr.conf
/etc/dnf/dnf.conf
/etc/openldap/ldap.conf
/etc/selinux/semanage.conf
/etc/pki/ca-trust/ca-legacy.conf
/etc/xattr.conf
/etc/rhsm/logging.conf
/etc/rhsm/rhsm.conf
/etc/crypto-policies/back-ends/bind.config
/etc/crypto-policies/back-ends/nss.config
/etc/crypto-policies/back-ends/opensshserver.config
/etc/crypto-policies/back-ends/libssh.config
/etc/crypto-policies/back-ends/java.config
/etc/crypto-policies/back-ends/libreswan.config
/etc/crypto-policies/back-ends/openssl.config
/etc/crypto-policies/back-ends/krb5.config
/etc/crypto-policies/back-ends/.config
/etc/crypto-policies/back-ends/opensslcnf.config
/etc/crypto-policies/back-ends/gnutls.config
/etc/crypto-policies/back-ends/openssh.config
/etc/host.conf
/etc/sysctl.d/99-sysctl.conf
/etc/locale.conf
/etc/dbus-1/system.conf
/etc/dbus-1/session.conf
/etc/dbus-1/system.d/com.redhat.RHSM1.Facts.conf
/etc/dbus-1/system.d/com.redhat.RHSM1.conf
/etc/nsswitch.conf
/etc/nsswitch.conf.bak
/etc/security/access.conf
/etc/security/faillock.conf
/etc/security/namespace.conf
/etc/security/chroot.conf
/etc/security/time.conf
/etc/security/pwquality.conf.d
/etc/security/limits.conf
/etc/security/pam_env.conf
/etc/security/sepermit.conf
/etc/security/group.conf
/etc/security/pwquality.conf
/etc/libaudit.conf
/etc/systemd/resolved.conf
/etc/systemd/coredump.conf
/etc/systemd/system.conf
/etc/systemd/journald.conf
/etc/systemd/logind.conf
/etc/systemd/user.conf
/etc/vconsole.conf
/etc/ld.so.conf.d
/etc/X11/xorg.conf.d
/etc/X11/xorg.conf.d/00-keyboard.conf
/etc/krb5.conf
/etc/ld.so.conf
/etc/sysctl.conf
/etc/libreport/events.d/collect_dnf.conf
/etc/yum.conf
/etc/resolv.conf
/etc/gcrypt/random.conf
/etc/nginx/nginx.conf
/etc/nginx/fastcgi.conf
/etc/man_db.conf
""".strip()


def test_docker_running_container_ids():
    dockerlistcontainers = DockerListContainers(context_wrap(DOCKER_PS, path='/etc/httpd/conf/httpd.conf'))
    broker = {
        DockerListContainers: dockerlistcontainers
    }
    result = docker_running_container_ids(broker)
    assert result == ['947c8fd31e140b1ab243880594d6260530cd3a76fb60ef6ef7ce6a4c4ea9f104']


def test_docker_running_container_nginx_conf():
    docker_find1 = Mock()
    docker_find2 = Mock()
    docker_find1.content = DOCKER_FIND.splitlines()
    docker_find1.file_path = '/insights_commands/docker_exec_947c8fd31e140b1ab243880594d6260530cd3a76fb60ef6ef7ce6a4c4ea9f104_find_.etc_.opt_-name_.conf'
    docker_find2.content = DOCKER_FIND.splitlines()
    docker_find2.file_path = '/insights_commands/docker_exec_847c8fd31e140b1ab243880594d6260530cd3a76fb60ef6ef7ce6a4c4ea9f104_find_.etc_.opt_-name_.conf'
    broker = {LocalSpecs.docker_find_etc: [docker_find1, docker_find2]}
    result = docker_running_container_nginx_conf(broker)
    assert result == [('947c8fd31e140b1ab243880594d6260530cd3a76fb60ef6ef7ce6a4c4ea9f104', '/etc/nginx/nginx.conf'), ('947c8fd31e140b1ab243880594d6260530cd3a76fb60ef6ef7ce6a4c4ea9f104', '/etc/nginx/fastcgi.conf'), ('847c8fd31e140b1ab243880594d6260530cd3a76fb60ef6ef7ce6a4c4ea9f104', '/etc/nginx/nginx.conf'), ('847c8fd31e140b1ab243880594d6260530cd3a76fb60ef6ef7ce6a4c4ea9f104', '/etc/nginx/fastcgi.conf')]
