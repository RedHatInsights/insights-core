"""
This module defines all datasources used by standard Red Hat Insight components.

To define data sources that override the components in this file, create a
`insights.core.spec_factory.SpecFactory` with "insights.specs" as the constructor
argument. Data sources created with that factory will override components in
this file with the same `name` keyword argument. This allows overriding the
data sources that standard Insights `Parsers` resolve against.
"""

import os

from insights.config import format_rpm

from insights.core.context import ClusterArchiveContext
from insights.core.context import DockerHostContext
from insights.core.context import DockerImageContext
from insights.core.context import HostContext
from insights.core.context import OpenShiftContext

from insights.core.plugins import datasource
from insights.core.spec_factory import CommandOutputProvider, ContentException, SpecFactory

sf = SpecFactory()

autofs_conf = sf.simple_file("/etc/autofs.conf", name="autofs_conf")
auditd_conf = sf.simple_file("/etc/audit/auditd.conf", name="auditd_conf")
blkid = sf.simple_command("/usr/sbin/blkid -c /dev/null", name="blkid")
bond = sf.glob_file("/proc/net/bonding/bond*", name="bond")
branch_info = sf.simple_file("/branch_info", name="branch_info")
brctl_show = sf.simple_command("/usr/sbin/brctl show", name="brctl_show")
candlepin_log = sf.simple_file("/var/log/candlepin/candlepin.log", name="candlepin_log")
catalina_out_var = sf.glob_file("/var/log/tomcat*/catalina.out", name="catalina_out_var")
catalina_out_tomcat = sf.glob_file("/tomcat-logs/tomcat*/catalina.out", name="catalina_out_tomcat")
catalina_out = sf.first_of([catalina_out_var, catalina_out_tomcat], name="catalina_out")
cciss = sf.glob_file("/proc/driver/cciss/cciss*", name="cciss")
ceilometer_central_log = sf.simple_file("/var/log/ceilometer/central.log", name="ceilometer_central_log")
ceilometer_collector_log = sf.simple_file("/var/log/ceilometer/collector.log", name="ceilometer_collector_log")
ceilometer_conf = sf.simple_file("/etc/ceilometer/ceilometer.conf", name="ceilometer_conf")
ceph_socket_files = sf.listdir("/var/run/ceph/ceph-*.*.asok", context=HostContext, name="ceph_socket_files")
ceph_osd_ec_profile_ls = sf.simple_command("/usr/bin/ceph osd erasure-code-profile ls", name="ceph_osd_ec_profile_ls")
ceph_config_show = sf.foreach(ceph_socket_files, "/usr/bin/ceph daemon %s config show", name="ceph_socket_show")
ceph_health_detail = sf.simple_command("/usr/bin/ceph health detail -f json-pretty", name="ceph_health_detail")
ceph_osd_dump = sf.simple_command("/usr/bin/ceph osd dump -f json-pretty", name="ceph_osd_dump")
ceph_osd_df = sf.simple_command("/usr/bin/ceph osd df -f json-pretty", name="ceph_osd_df")
ceph_osd_ec_profile_get = sf.foreach(ceph_osd_ec_profile_ls, "/usr/bin/ceph osd erasure-code-profile get %s -f json-pretty", name="ceph_osd_ec_profile_get")
ceph_osd_log = sf.glob_file(r"var/log/ceph/ceph-osd*.log", name="ceph_osd_log")
ceph_s = sf.simple_command("/usr/bin/ceph -s -f json-pretty", name="ceph_s")
ceph_v = sf.simple_command("/usr/bin/ceph -v", name="ceph_v")
chkconfig = sf.simple_command("/sbin/chkconfig --list", name="chkconfig")
chrony_conf = sf.simple_file("/etc/chrony.conf", name="chrony_conf")
chronyc_sources = sf.simple_command("/usr/bin/chronyc sources", name="chronyc_sources")
cib_xml = sf.simple_file("/var/lib/pacemaker/cib/cib.xml", name="cib_xml")
cinder_conf = sf.simple_file("/etc/cinder/cinder.conf", name="cinder_conf")
cinder_volume_log = sf.simple_file("/var/log/cinder/volume.log", name="cinder_volume_log")
cluster_conf = sf.simple_file("/etc/cluster/cluster.conf", name="cluster_conf")
cmdline = sf.simple_file("/proc/cmdline", name="cmdline")
cobbler_settings = sf.first_file(["/etc/cobbler/settings", "/conf/cobbler/settings"], name="cobbler_settings")
cobbler_modules_conf = sf.first_file(["/conf/cobbler/modules.conf", "/conf/cobbler/modules.conf"], name="cobbler_modules_conf")
corosync = sf.simple_file("/etc/sysconfig/corosync", name="corosync")
cpuinfo = sf.first_file(["/proc/cpuinfo", "/cpuinfo"], name="cpuinfo")
cpuinfo_max_freq = sf.simple_file("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", name="cpuinfo_max_freq")
current_clocksource = sf.simple_file("/sys/devices/system/clocksource/clocksource0/current_clocksource", name="current_clocksource")
date = sf.simple_command("/bin/date", name="date")
date_iso = sf.simple_command("/bin/date --iso-8601=seconds", name="date_iso")
date_utc = sf.simple_command("/bin/date --utc", name="date_utc")
df_al = sf.simple_command("/bin/df -al", name="df_al")
df_alP = sf.simple_command("/bin/df -alP", name="df_alP")
df_li = sf.simple_command("/bin/df -li", name="df_li")
dirsrv = sf.simple_file("/etc/sysconfig/dirsrv", name="dirsrv", alias="dirsrv")
display_java = sf.simple_command("/usr/sbin/alternatives --display java", name="display_java")
dmesg = sf.simple_command("/bin/dmesg", name="dmesg", alias="dmesg")
dmidecode = sf.simple_command("/usr/sbin/dmidecode", name="dmidecode", alias="dmidecode")
docker_info = sf.simple_command("/usr/bin/docker info", name="docker_info")
docker_list_containers = sf.simple_command("/usr/bin/docker ps --all --no-trunc", name="docker_list_containers")
docker_list_images = sf.simple_command("/usr/bin/docker images --all --no-trunc --digests", name="docker_list_images")


@datasource(docker_list_images)
def docker_image_ids(broker):
    images = broker[docker_list_images]
    try:
        result = set()
        for l in images.content[1:]:
            result.add(l.split(None)[3].strip())
    except:
        raise ContentException("No docker images.")
    if result:
        return list(result)
    raise ContentException("No docker images.")


# TODO: This parsing is broken.
@datasource(docker_list_containers)
def docker_container_ids(broker):
    containers = broker[docker_list_containers]
    try:
        result = set()
        for l in containers.content[1:]:
            result.add(l.split(None)[3].strip())
    except:
        raise ContentException("No docker containers.")
    if result:
        return list(result)
    raise ContentException("No docker containers.")


docker_host_machine_id = sf.simple_file("/etc/redhat-access-insights/machine-id", name="docker_host_machine_id", context=DockerHostContext)
docker_image_inspect = sf.foreach(docker_image_ids, "/usr/bin/docker inspect --type=image %s", name="docker_image_inspect", context=DockerHostContext)
docker_container_inspect = sf.foreach(docker_container_ids, "/usr/bin/docker inspect --type=container %s", name="docker_container_inspect", context=DockerHostContext)
docker_network = sf.simple_file("/etc/sysconfig/docker-network", name="docker_network", context=DockerHostContext)
docker_storage = sf.simple_file("/etc/sysconfig/docker-storage", name="docker_storage", context=DockerHostContext)
docker_storage_setup = sf.simple_file("/etc/sysconfig/docker-storage-setup", name="docker_storage_setup", context=DockerHostContext)
docker_sysconfig = sf.simple_file("/etc/sysconfig/docker", name="docker_sysconfig", context=DockerHostContext)
# dumpe2fs_h = sf.foreach(, "/sbin/dumpe2fs -h %s")
engine_log = sf.simple_file("/var/log/ovirt-engine/engine.log", name="engine_log")

ethernet_interfaces = sf.listdir("/sys/class/net", name="ethernet_interfaces", context=HostContext)
ethtool = sf.foreach(ethernet_interfaces, "/sbin/ethtool %s", name="ethtool")
ethtool_S = sf.foreach(ethernet_interfaces, "/sbin/ethtool -S %s", name="ethtool_S")
ethtool_a = sf.foreach(ethernet_interfaces, "/sbin/ethtool -a %s", name="ethtool_a")
ethtool_c = sf.foreach(ethernet_interfaces, "/sbin/ethtool -c %s", name="ethtool_c")
ethtool_g = sf.foreach(ethernet_interfaces, "/sbin/ethtool -g %s", name="ethtool_g")
ethtool_i = sf.foreach(ethernet_interfaces, "/sbin/ethtool -i %s", name="ethtool_i")
ethtool_k = sf.foreach(ethernet_interfaces, "/sbin/ethtool -k %s", name="ethtool_k")
facter = sf.simple_command("/usr/bin/facter", name="facter")
fc_match = sf.simple_command("/usr/bin/fc-match -sv 'sans:regular:roman' family fontformat", name="fc_match")
fdisk_l = sf.simple_command("/sbin/fdisk -l", name="fdisk_l")
foreman_satellite_log = sf.simple_file("/var/log/foreman-installer/satellite.log", name="foreman_satellite_log")
foreman_production_log = sf.simple_file("/var/log/foreman/production.log", name="foreman_production_log")
foreman_proxy_conf = sf.simple_file("/etc/foreman-proxy/settings.yml", name="foreman_proxy_conf")
foreman_proxy_log = sf.simple_file("/var/log/foreman-proxy/proxy.log", name="foreman_proxy_log")
fstab = sf.simple_file("/etc/fstab", name="fstab")
galera_cnf = sf.simple_file("/etc/my.cnf.d/galera.cnf", name="galera_cnf")
getenforce = sf.simple_command("/usr/sbin/getenforce", name="getenforce")
getsebool = sf.simple_command("/usr/sbin/getsebool -a", name="getsebool")
glance_api_conf = sf.simple_file("/etc/glance/glance-api.conf", name="glance_api_conf")
glance_api_log = sf.simple_file("/var/log/glance/api.log", name="glance_api_log")
glance_cache_conf = sf.simple_file("/etc/glance/glance-cache.conf", name="glance_cache_conf")
glance_registry_conf = sf.simple_file("/etc/glance/glance-registry.conf", name="glance_registry_conf")
grub_conf = sf.simple_file("/boot/grub/grub.conf", name="grub_conf")
grub2_cfg = sf.simple_file("/boot/grub2/grub.cfg", name="grub2_cfg")
grub_config_perms = sf.simple_command("/bin/ls -l /boot/grub2/grub.cfg", name="grub_config_perms")  # only RHEL7 and updwards
grub1_config_perms = sf.simple_command("/bin/ls -l /boot/grub/grub.conf", name="grub1_config_perms")  # RHEL6
hammer_ping = sf.simple_command("/usr/bin/hammer ping", name="hammer_ping")
haproxy_cfg = sf.simple_file("/etc/haproxy/haproxy.cfg", name="haproxy_cfg")
heat_api_log = sf.simple_file("/var/log/heat/heat-api.log", name="heat_api_log")
heat_conf = sf.simple_file("/etc/heat/heat.conf", name="heat_conf")
heat_crontab = sf.simple_command("/usr/bin/crontab -l -u heat", name="heat_crontab")
heat_engine_log = sf.simple_file("/var/log/heat/heat-engine.log", name="heat_engine_log")
hostname = sf.simple_command("/usr/bin/hostname -f", name="hostname", alias="hostname")
hosts = sf.simple_file("/etc/hosts", name="hosts", alias="hosts")
hponcfg_g = sf.simple_command("/sbin/hponcfg -g", name="hponcfg_g")
httpd_access_log = sf.simple_file("/var/log/httpd/access_log", name="httpd_access_log")
httpd_conf = sf.first_file(["/etc/httpd/conf/httpd.conf", "/conf/httpd/conf/httpd.conf"], name="httpd_conf")
httpd_conf_d = sf.first_of([sf.glob_file("/etc/httpd/conf.d/*.conf", name="httpd_conf_d_etc"),
                            sf.glob_file("/conf/httpd/conf.d/*.conf", name="httpd_conf_d_conf")],
                            name="httpd_conf_d")
httpd_error_log = sf.simple_file("var/log/httpd/error_log", name="httpd_error_log")
httpd_pid = sf.simple_command("/bin/ps aux | grep /usr/sbin/httpd | grep -v grep | head -1 | awk '{print $2}'", name="httpd_pid")
httpd_limits = sf.foreach(httpd_pid, "/bin/cat /proc/%s/limits", name="httpd_limits")
httpd_ssl_access_log = sf.simple_file("/var/log/httpd/ssl_access_log", name="httpd_ssl_access_log")
httpd_ssl_error_log = sf.simple_file("/var/log/httpd/ssl_error_log", name="httpd_ssl_error_log")
httpd_V = sf.simple_command("/usr/sbin/httpd -V", name="http_V")
ifcfg = sf.glob_file("/etc/sysconfig/network-scripts/ifcfg-*", name="ifcfg")
ifconfig = sf.simple_command("/sbin/ifconfig -a", name="ifconfig")
imagemagick_policy = sf.glob_file(["/etc/ImageMagick/policy.xml",
                                   "/usr/lib*/ImageMagick-6.5.4/config/policy.xml"],
                                   name="imagemagick_policy")
init_ora = sf.simple_file("${ORACLE_HOME}/dbs/init.ora", name="init_ora")
interrupts = sf.simple_file("/proc/interrupts", name="interrupts")
ip_addr = sf.simple_command("/sbin/ip addr", name="ip_addr")
ip_route_show_table_all = sf.simple_command("/sbin/ip route show table all", name="ip_route_show_table_all")
ipcs_s = sf.simple_command("/usr/bin/ipcs -s", name="ipcs_s")
semid = sf.simple_command("/usr/bin/ipcs -s | awk '{if (NF == 5 && $NF ~ /^[0-9]+$/) print $NF}'", name="semid")
ipcs_s_i = sf.foreach(semid, "/usr/bin/ipcs -s -i %s", name="ipcs_s_i")
iptables = sf.simple_command("/sbin/iptables-save", name="iptables")
iptables_permanent = sf.simple_file("etc/sysconfig/iptables", name="iptables_permanent")
ip6tables = sf.simple_command("/sbin/ip6tables-save", name="ip6tables")
ip6tables_permanent = sf.simple_file("etc/sysconfig/ip6tables", name="ip6tables_permanent")
ipv4_neigh = sf.simple_command("/sbin/ip -4 neighbor show nud all", name="ipv4_neigh")
ipv6_neigh = sf.simple_command("/sbin/ip -6 neighbor show nud all", name="ipv6_neigh")
kdump = sf.simple_file("/etc/sysconfig/kdump", name="kdump")
kdump_conf = sf.simple_file("/etc/kdump.conf", name="kdump_conf")
kexec_crash_loaded = sf.simple_file("/sys/kernel/kexec_crash_loaded", name="kexec_crash_loaded")
kexec_crash_size = sf.simple_file("/sys/kernel/kexec_crash_size", name="kexec_crash_size")
keystone_conf = sf.simple_file("/etc/keystone/keystone.conf", name="keystone_conf")
keystone_crontab = sf.simple_command("/usr/bin/crontab -l -u keystone", name="keystone_crontab")
keystone_log = sf.simple_file("/var/log/keystone/keystone.log", name="keystone_log")
ksmstate = sf.simple_file("/sys/kernel/mm/ksm/run", name="ksmstate")
last_upload_globs = ["/etc/redhat-access-insights/.lastupload", "/etc/insights-client/.lastupload"]
last_upload = sf.glob_file(last_upload_globs, name="last_upload")
libvirtd_log = sf.simple_file("/var/log/libvirt/libvirtd.log", name="libvirtd_log")
limits_conf = sf.simple_file("/etc/security/limits.conf", name="limits_conf")
limits_d = sf.glob_file("/etc/security/limits.d/*", name="limits_d")
locale = sf.simple_command("/usr/bin/locale", name="locale")
localtime = sf.simple_command("/usr/bin/file -L /etc/localtime", name="localtime")
lpstat_p = sf.simple_command("/usr/bin/lpstat -p", name="lpstat_p")
lsblk = sf.simple_command("/bin/lsblk", name="lsblk")
lsblk_pairs = sf.simple_command("/bin/lsblk -P -o NAME,KNAME,MAJ:MIN,FSTYPE,MOUNTPOINT,LABEL,UUID,RA,RO,RM,MODEL,SIZE,STATE,OWNER,GROUP,MODE,ALIGNMENT,MIN-IO,OPT-IO,PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,TYPE,DISC-ALN,DISC-GRAN,DISC-MAX,DISC-ZERO", name="lsblk_pairs")
lscpu = sf.simple_command("/usr/bin/lscpu", name="lscpu")
lsinitrd_lvm_conf = sf.first_of([sf.simple_command("/sbin/lsinitrd -f /etc/lvm/lvm.conf", name="lsinitrd_sbin"),
                                 sf.simple_command("/usr/bin/lsinitrd -f /etc/lvm/lvm.conf", name="lsinitrd_usrbin")],
                                 name="lsinitrd_lvm_conf")
lsmod = sf.simple_command("/sbin/lsmod", name="lsmod")
lspci = sf.simple_command("/sbin/lspci", name="lspci")
lsof = sf.simple_command("/usr/sbin/lsof", name="lsof")
ls_boot = sf.simple_command("/bin/ls -lanR /boot", name="ls_boot")
ls_docker_volumes = sf.simple_command("/bin/ls -lanR /var/lib/docker/volumes", name="ls_docker_volumes")
ls_dev = sf.simple_command("/bin/ls -lanR /dev", name="ls_dev")
ls_disk = sf.simple_command("/bin/ls -lanR /dev/disk/by-*", name="ls_disk")
ls_etc = sf.simple_command("/bin/ls -lanR /etc", name="ls_etc")
ls_sys_firmware = sf.simple_command("/bin/ls -lanR /sys/firmware", name="ls_sys_firmware")
ls_var_log = sf.simple_command("/bin/ls -la /var/log /var/log/audit", name="ls_var_log")
lvdisplay = sf.simple_command("/sbin/lvdisplay", name="lvdisplay")
lvm_conf = sf.simple_file("/etc/lvm/lvm.conf", name="lvm_conf")
lvs = None  # sf.simple_command('/sbin/lvs -a -o +lv_tags,devices --config="global{locking_type=0}"', name="lvs")
lvs_noheadings = sf.simple_command("/sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,vg_name,lv_size,region_size,mirror_log,lv_attr,devices,region_size --config=\"global{locking_type=0}\"", name="lvs_noheadings")
machine_id = sf.simple_file("etc/redhat-access-insights/machine-id", name="machine_id")
mariadb_log = sf.simple_file("/var/log/mariadb/mariadb.log", name="mariadb_log")
mdstat = sf.simple_file("/proc/mdstat", name="mdstat")
meminfo = sf.first_file(["/proc/meminfo", "/meminfo"], name="meminfo")
messages = sf.simple_file("/var/log/messages", name="messages")
metadata_json = sf.simple_file("metadata.json", name="metadata_json", context=ClusterArchiveContext)
module = sf.listdir("/sys/module", name="module")
modinfo = sf.foreach(module, "/usr/sbin/modinfo %s", name="modinfo")
modprobe_conf = sf.simple_file("/etc/modprobe.conf", name="modprobe_conf")
modprobe_d = sf.glob_file("/etc/modprobe.d/*.conf", name="modprobe_d")
mount = sf.simple_command("/bin/mount", name="mount")
multicast_querier = sf.simple_command("/usr/bin/find /sys/devices/virtual/net/ -name multicast_querier -print -exec cat {} \;", name="multicast_querier")
multipath_conf = sf.simple_file("/etc/multipath.conf", name="multipath_conf")
multipath_v4_ll = sf.simple_command("/sbin/multipath -v4 -ll", name="multipath_v4_ll")
named_checkconf_p = sf.simple_command("/usr/sbin/named-checkconf -p", name="named_checkconf_p")
netconsole = sf.simple_file("/etc/sysconfig/netconsole", name="netconsole")
netstat = sf.simple_command("/bin/netstat -neopa", name="netstat")
netstat_agn = sf.simple_command("/bin/netstat -agn", name="netstat_agn")
netstat_i = sf.simple_command("/bin/netstat -i", name="netstat_i")
netstat_s = sf.simple_command("/bin/netstat -s", name="netstat_s")
neutron_conf = sf.simple_file("/etc/neutron/neutron.conf", name="neutron_conf")
neutron_ovs_agent_log = sf.simple_file("/var/log/neutron/openvswitch-agent.log", name="neutron_ovs_agent_log")
neutron_plugin_ini = sf.simple_file("/etc/neutron/plugin.ini", name="neutron_plugin_ini")
neutron_server_log = sf.simple_file("/var/log/neutron/server.log", name="neutron_server_log")
nfnetlink_queue = sf.simple_file("/proc/net/netfilter/nfnetlink_queue", name="nfnetlink_queue")
nfs_exports = sf.simple_file("/etc/exports", name="nfs_exports")
nfs_exports_d = sf.glob_file("/etc/exports.d/*.exports", name="nfs_exports_d")
nova_api_log = sf.simple_file("/var/log/nova/nova-api.log", name="nova_api_log")
nova_compute_log = sf.simple_file("/var/log/nova/nova-compute.log", name="nova_compute_log")
nova_conf = sf.simple_file("/etc/nova/nova.conf", name="nova_conf")
nproc_conf = sf.glob_file("/etc/security/limits.d/*-nproc.conf", name="nproc_conf")
nova_crontab = sf.simple_command("/usr/bin/crontab -l -u nova", name="nova_crontab")
nscd_conf = sf.simple_file("/etc/nscd.conf", name="nscd_conf")
nsswitch_conf = sf.simple_file("/etc/nsswitch.conf", name="nsswitch_conf")
ntp_conf = sf.simple_file("/etc/ntp.conf", name="ntp_conf")
ntpq_leap = sf.simple_command("/usr/sbin/ntpq -c 'rv 0 leap'", name="ntpq_leap")
ntpq_pn = sf.simple_command("/usr/sbin/ntpq -pn", name="ntpq_pn")
ntptime = sf.simple_command("/usr/sbin/ntptime", name="ntptime")
crt = sf.simple_command("/usr/bin/find /etc/origin/node /etc/origin/master -type f -path '*.crt'", name="crt")
oc_get_pod = sf.simple_command("/usr/bin/oc get pod -o yaml --all-namespaces", name="oc_get_pod", context=OpenShiftContext)
oc_get_dc = sf.simple_command("/usr/bin/oc get dc -o yaml --all-namespaces", name="oc_get_dc", context=OpenShiftContext)
oc_get_service = sf.simple_command("/usr/bin/oc get service -o yaml --all-namespaces", name="oc_get_service", context=OpenShiftContext)
oc_get_rolebinding = sf.simple_command("/usr/bin/oc get rolebinding -o yaml --all-namespaces", name="oc_get_rolebinding", context=OpenShiftContext)
oc_get_project = sf.simple_command("/usr/bin/oc get project -o yaml --all-namespaces", name="oc_get_project", context=OpenShiftContext)
oc_get_role = sf.simple_command("/usr/bin/oc get role -o yaml --all-namespaces", name="oc_get_role", context=OpenShiftContext)
oc_get_pv = sf.simple_command("/usr/bin/oc get pv -o yaml --all-namespaces", name="oc_get_pv", context=OpenShiftContext)
oc_get_pvc = sf.simple_command("/usr/bin/oc get pvc -o yaml --all-namespaces", name="oc_get_pvc", context=OpenShiftContext)
openshift_certificates = sf.foreach(crt, "/usr/bin/openssl x509 -noout -enddate -in %s", name="openshift_certificates")
openvswitch_server_log = sf.simple_file('/var/log/openvswitch/ovsdb-server.log', name="openvswitch_server_log")
openvswitch_daemon_log = sf.simple_file('/var/log/openvswitch/ovs-vswitchd.log', name="openvswitch_daemon_log")
os_release = sf.simple_file("etc/os-release", name="os_release")
osa_dispatcher_log = sf.first_file(["/var/log/rhn/osa-dispatcher.log",
                                    "/rhn-logs/rhn/osa-dispatcher.log"],
                                    name="osa_dispatcher_log")
ose_master_config = sf.simple_file("/etc/origin/master/master-config.yaml", name="ose_master_config")
ose_node_config = sf.simple_file("/etc/origin/node/node-config.yaml", name="ose_node_config")
ovirt_engine_confd = sf.glob_file("/etc/ovirt-engine/engine.conf.d/*", name="ovirt_engine_confd")
ovirt_engine_server_log = sf.simple_file("/var/log/ovirt-engine/server.log", name="ovirt_engine_server_log")
ovs_vsctl_show = sf.simple_command("/usr/bin/ovs-vsctl show", name="ovs_vsctl_show")
pacemaker_log = sf.simple_file("/var/log/pacemaker.log", name="pacemaker_log")
pam_conf = sf.simple_file("/etc/pam.conf", name="pam_conf")
parted_l = sf.simple_command("/sbin/parted -l -s", name="parted_l")
password_auth = sf.simple_file("/etc/pam.d/password-auth", name="password_auth")
pcs_status = sf.simple_command("/usr/sbin/pcs status", name="pcs_status")
pluginconf_d = sf.glob_file("/etc/yum/pluginconf.d/*.conf", name="pluginconf_d")
postgresql_conf = sf.first_file(["/var/lib/pgsql/data/postgresql.conf",
                                 "/opt/rh/postgresql92/root/var/lib/pgsql/data/postgresql.conf",
                                 "database/postgresql.conf"],
                                 name="postgresql_conf")
postgresql_log = sf.first_of([sf.glob_file("/var/lib/pgsql/data/pg_log/postgresql-*.log", name="postgresql_var"),
                              sf.glob_file("/opt/rh/postgresql92/root/var/lib/pgsql/data/pg_log/postgresql-*.log", name="postgresql_opt"),
                              sf.glob_file("/database/postgresql-*.log", name="postgresql_database")], name="postgresql_log")
md5chk_files = sf.simple_command("/bin/ls -H /usr/lib*/{libfreeblpriv3.so,libsoftokn3.so} /etc/pki/product*/69.pem /etc/fonts/fonts.conf /dev/null 2>/dev/null", name="md5chk_files")
prelink_orig_md5 = None
prev_uploader_log = sf.simple_file("var/log/redhat-access-insights/redhat-access-insights.log.1", "prev_uploader_log")
ps_aux = sf.simple_command("/bin/ps aux", name="ps_aux")
ps_auxcww = sf.simple_command("/bin/ps auxcww", name="ps_auxcww", alias="ps_auxcww")
ps_auxwww = sf.simple_file("/sos_commands/process/ps_auxwww", name="ps_auxwww")
ps_axcwwo = sf.simple_command("/bin/ps axcwwo ucomm,%cpu,lstart", name="ps_axcwwo")
puppet_ssl_cert_ca_pem = None
pvs = sf.simple_command('/sbin/pvs -a -v -o +pv_mda_free,pv_mda_size,pv_mda_count,pv_mda_used_count,pe_count --config="global{locking_type=0}"', name="pvs")
pvs_noheadings = sf.simple_command("/sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all,vg_name --config=\"global{locking_type=0}\"", name="pvs_noheadings")
qemu_conf = sf.simple_file("/etc/libvirt/qemu.conf", name="qemu_conf")
qpid_stat_q = sf.simple_command("/usr/bin/qpid-stat -q --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671", name="qpid_stat_q")
qpid_stat_u = sf.simple_command("/usr/bin/qpid-stat -u --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671", name="qpid_stat_u")
rabbitmq_logs = sf.glob_file("/var/log/rabbitmq/rabbit@*.log", ignore=".*rabbit@.*(?<!-sasl).log$", name="rabbitmq_logs")
rabbitmq_policies = sf.simple_command("/usr/sbin/rabbitmqctl list_policies", name="rabbitmq_policies")
rabbitmq_queues = sf.simple_command("/usr/sbin/rabbitmqctl list_queues name messages consumers auto_delete", name="rabbitmq_queues")
rabbitmq_report = sf.simple_command("/usr/sbin/rabbitmqctl report", name="rabbitmq_report")
rabbitmq_startup_err = sf.simple_file("/var/log/rabbitmq/startup_err", name="rabbitmq_startup_err")
rabbitmq_startup_log = sf.simple_file("/var/log/rabbitmq/startup_log", name="rabbitmq_startup_log")
rabbitmq_users = sf.simple_command("/usr/sbin/rabbitmqctl list_users", name="rabbitmq_users")
rc_local = sf.simple_file("/etc/rc.d/rc.local", name="rc_local")
redhat_release = sf.simple_file("/etc/redhat-release", name="redhat_release")
resolv_conf = sf.simple_file("/etc/resolv.conf", name="resolve_conf")
rhn_charsets = sf.simple_command("/usr/bin/rhn-charsets", name="rhn_charsets")
rhn_conf = sf.first_file(["/etc/rhn/rhn.conf", "/conf/rhn/rhn/rhn.conf"], name="rhn_conf")
rhn_entitlement_cert_xml = sf.first_of([sf.glob_file("/etc/sysconfig/rhn/rhn-entitlement-cert.xml*", name="rhn_entitlement_cert_xml_etc"),
                               sf.glob_file("/conf/rhn/sysconfig/rhn/rhn-entitlement-cert.xml*", name="rhn_entitlement_cert_xml_conf")],
                               name="rhn_entitlement_cert_xml")
rhn_hibernate_conf = sf.first_file(["/usr/share/rhn/config-defaults/rhn_hibernate.conf", "/config-defaults/rhn_hibernate.conf"], name="rhn_hibernate_conf")
rhn_schema_stats = sf.simple_command("/usr/bin/rhn-schema-stats -", name="rhn_schema_stats")
rhn_schema_version = sf.simple_command("/usr/bin/rhn-schema-version", name="rhn_schema_version")
rhn_server_xmlrpc_log = sf.first_file(["/var/log/rhn/rhn_server_xmlrpc.log",
                                       "/rhn-logs/rhn/rhn_server_xmlrpc.log"],
                                       name="rhn_server_xmlrpc_log")
rhn_search_daemon_log = sf.first_file(["/var/log/rhn/search/rhn_search_daemon.log",
                                       "/rhn-logs/rhn/search/rhn_search_daemon.log"],
                                       name="rhn_search_daemon_log")
rhn_taskomatic_daemon_log = sf.first_file(["/var/log/rhn/rhn_taskomatic_daemon.log",
                                           "rhn-logs/rhn/rhn_taskomatic_daemon.log"],
                                           name="rhn_taskomatic_daemon_log")
rhsm_conf = sf.simple_file("/etc/rhsm/rhsm.conf", name="rhsm_conf")
rhsm_log = sf.simple_file("/var/log/rhsm/rhsm.log", name="rhsm_log")
root_crontab = sf.simple_command("/usr/bin/crontab -l -u root", name="root_crontab")
route = sf.simple_command("/sbin/route -n", name="route")
rpm_V_packages = sf.simple_command("/usr/bin/rpm -V coreutils procps procps-ng shadow-utils passwd sudo", name="rpm_V_packages")
rsyslog_conf = sf.simple_file("/etc/rsyslog.conf", name="rsyslog_conf")
samba = sf.simple_file("/etc/samba/smb.conf", name="samba")
satellite_version_rb = sf.simple_file("/usr/share/foreman/lib/satellite/version.rb", name="satellite_version_rb")
block_devices = sf.listdir("/sys/block", name="block_devices")
scheduler = sf.foreach(block_devices, "/bin/cat /sys/block/%s/queue/scheduler", name="scheduler")
scsi = sf.simple_file("/proc/scsi/scsi", name="scsi")
secure = sf.simple_file("/var/log/secure", name="secure")
selinux_config = sf.simple_file("/etc/selinux/config", name="selinux_config")
sestatus = sf.simple_command("/usr/sbin/sestatus -b", name="sestatus")
# block = sf.simple_command("/bin/ls /sys/block | awk '!/^ram|^\\.+$/ {print \"/dev/\" $1 \" unit s print\"}'", name="block")


@datasource(HostContext)
def block(broker):
    remove = (".", "ram", "dm-", "loop")
    tmp = "/dev/%s"
    return[(tmp % f) for f in os.listdir("/sys/block") if not f.startswith(remove)]


smartctl = sf.foreach(block, "/sbin/smartctl -a %s", name="smartctl", keep_rc=True)
smbstatus_p = sf.simple_command("/usr/bin/smbstatus -p", name="smbstatus_p")
smbstatus_S = sf.simple_command("/usr/bin/smbstatus -S", name="smbstatus_S")
smartctl = sf.foreach(block, "/sbin/smartctl -a %s", name="smartctl", keep_rc=True)
spfile_ora = sf.glob_file("${ORACLE_HOME}/dbs/spfile*.ora", name="spfile_ora")
ss = sf.simple_command("/usr/sbin/ss -tulpn", name="ss")
ssh_config = sf.simple_file("/etc/ssh/ssh_config", name="ssh_config")
sshd_config = sf.simple_file("/etc/ssh/sshd_config", name="sshd_config")
sshd_config_perms = sf.simple_command("/bin/ls -l /etc/ssh/sshd_config", name="sshd_config_perms")
sssd_config = sf.simple_file("/etc/sssd/sssd.conf", name="sssd_config")
sssd_logs = sf.glob_file("/var/log/sssd/*.log", name="sssd_logs")
sysconfig_chronyd = sf.simple_file("/etc/sysconfig/chronyd", name="sysconfig_chronyd")
sysconfig_httpd = sf.simple_file("/etc/sysconfig/httpd", name="sysconfig_httpd")
sysconfig_ntpd = sf.simple_file("/etc/sysconfig/ntpd", name="sysconfig_ntpd")
sysconfig_virt_who = sf.simple_file("/etc/sysconfig/virt-who", name="sysconfig_virt_who")
sysctl = sf.simple_command("/sbin/sysctl -a", name="sysctl")
sysctl_conf = sf.simple_file("/etc/sysctl.conf", name="sysctl_conf")
sysctl_conf_initramfs = sf.simple_command("/bin/lsinitrd /boot/initramfs-*kdump.img -f /etc/sysctl.conf /etc/sysctl.d/*.conf", name="sysctl_conf_initramfs")
systemctl_cinder_volume = sf.simple_command("/bin/systemctl show openstack-cinder-volume", name="systemctl_cinder_volume")
systemctl_list_unit_files = sf.simple_command("/bin/systemctl list-unit-files", name="systemctl_list_unit_files")
systemd_docker = sf.simple_file("/usr/lib/systemd/system/docker.service", name="docker_service")
systemd_openshift_node = sf.simple_file("/usr/lib/systemd/system/atomic-openshift-node.service", name="systemd_openshift_node")
systemd_system_conf = sf.simple_file("/etc/systemd/system.conf", name="system_conf")
systemid = sf.first_of([sf.simple_file("/etc/sysconfig/rhn/systemid", name="system_id_etc"),
                        sf.simple_file("/conf/rhn/sysconfig/rhn/systemid", name="system_id_conf")],
                        name="systemid")
tomcat_web_xml = sf.first_of([sf.glob_file("/etc/tomcat*/web.xml", name="tomcat_web_xml_etc"),
                              sf.glob_file("/conf/tomcat/tomcat*/web.xml", name="tomcat_web_xml_conf")],
                              name="tomcat_web_xml")
tuned_adm = sf.simple_command("/sbin/tuned-adm list", name="tuned_adm")
udev_persistent_net_rules = sf.simple_file("/etc/udev/rules.d/70-persistent-net.rules", name="udev_persistent_net_rules")
uname = sf.simple_command("/usr/bin/uname -a", name="uname", alias="uname")
up2date = sf.simple_file("/etc/sysconfig/rhn/up2date", name="up2date")
uploader_log = sf.simple_file("/var/log/redhat-access-insights/redhat-access-insights.log", name="uploader_log")
uptime = sf.simple_command("/usr/bin/uptime", name="uptime", alias="uptime")
vgdisplay = sf.simple_command("/sbin/vgdisplay", name="vgdisplay")
vdsm_conf = sf.simple_file("etc/vdsm/vdsm.conf", name="vdsm_conf")
vdsm_id = sf.simple_file("etc/vdsm/vdsm.id", name="vdsm_id")
vdsm_log = sf.simple_file("var/log/vdsm/vdsm.log", name="vdsm_log")
vgs = None  # sf.simple_command('/sbin/vgs -v -o +vg_mda_count,vg_mda_free,vg_mda_size,vg_mda_used_count,vg_tags --config="global{locking_type=0}"', name="vgs")
vgs_noheadings = sf.simple_command("/sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all --config=\"global{locking_type=0}\"", name="vgs_noheadings")
virt_what = sf.simple_command("/usr/sbin/virt-what", "virt_what")
vmcore_dmesg = sf.glob_file("/var/crash/*/vmcore-dmesg.txt", name="vmcore_dmesg")
vsftpd = sf.simple_file("/etc/pam.d/vsftpd", name="vsftpd")
vsftpd_conf = sf.simple_file("/etc/vsftpd/vsftpd.conf", name="vsftpd_conf")
woopsie = sf.simple_command(r"/usr/bin/find /var/crash /var/tmp -path '*.reports-*/whoopsie-report'", name="woopsie")
xfs_info = None
xinetd_conf = sf.simple_file("/etc/xinetd.conf", name="xinetd_conf")
xinetd_d = sf.glob_file("/etc/xinetd.d/*", name="xinetd_d")
yum_conf = sf.simple_file("/etc/yum.conf", name="yum_conf")
yum_log = sf.simple_file("/var/log/yum.log", name="yum_log")
yum_repolist = sf.simple_command("/usr/bin/yum -C repolist", name="yum_repolist")
yum_repos_d = sf.glob_file("/etc/yum.repos.d/*", name="yum_repos")

rpm_format = format_rpm()

host_installed_rpms = sf.simple_command("/usr/bin/rpm -qa --qf '%s'" % rpm_format, name="host_installed_rpms", context=HostContext)


@datasource(DockerImageContext)
def docker_installed_rpms(broker):
    ctx = broker[DockerImageContext]
    root = ctx.root
    fmt = rpm_format
    cmd = "/usr/bin/rpm -qa --root %s --qf '%s'" % (root, fmt)
    result = ctx.shell_out(cmd)
    return CommandOutputProvider(cmd, ctx, content=result)


# unify the different installed rpm provider types
installed_rpms = sf.first_of([host_installed_rpms, docker_installed_rpms], name="installed_rpms", alias="installed-rpms")
