import pytest
import doctest
from insights.parsers.initscript import InitScript, EmptyFileException, NotInitscriptException, VMWTools
from insights.parsers import initscript
from insights.tests import context_wrap


NOTINITSCRIPT_SCRIPT = "etc/rc.d/init.d/script_notinitscript"
NOTINITSCRIPT_CONTENT = """
#! /bin/bash

echo script_notinitscript
""".strip()

CHKCONFIG_SCRIPT = "etc/rc.d/init.d/script_chkconfig"
CHKCONFIG_CONTENT = """
#!/bin/sh
#
# rhnsd:        Starts the Spacewalk Daemon
#
# chkconfig: 345 97 03
# description:  This is a daemon which handles the task of connecting \
#               periodically to the Spacewalk servers to \
#               check for updates, notifications and perform system \
#               monitoring tasks according to the service level that \
#               this server is subscribed for
#
# processname: rhnsd
# pidfile: /var/run/rhnsd.pid
#

echo script_chkconfig
""".strip()

LSB_SCRIPT = "etc/rc.d/init.d/script_lsb"
LSB_CONTENT = """
#!/bin/sh
### BEGIN INIT INFO
# Provides: rhnsd
# Required-Start: $local_fs $network $remote_fs $named $time
# Required-Stop: $local_fs $network $remote_fs $named
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Starts the Spacewalk Daemon
# Description: This is a daemon which handles the task of connecting
#               periodically to the Spacewalk servers to
#               check for updates, notifications and perform system
#               monitoring tasks according to the service level that
#               this server is subscribed for.
### END INIT INFO

echo script_lsb
""".strip()

CHKCONFIG_LSB_SCRIPT = "etc/rc.d/init.d/script_chkconfig+lsb"
CHKCONFIG_LSB_CONTENT = """
#!/bin/sh
#
# rhnsd:        Starts the Spacewalk Daemon
#
# chkconfig: 345 97 03
# description:  This is a daemon which handles the task of connecting \
#               periodically to the Spacewalk servers to \
#               check for updates, notifications and perform system \
#               monitoring tasks according to the service level that \
#               this server is subscribed for
#
# processname: rhnsd
# pidfile: /var/run/rhnsd.pid
#

### BEGIN INIT INFO
# Provides: rhnsd
# Required-Start: $local_fs $network $remote_fs $named $time
# Required-Stop: $local_fs $network $remote_fs $named
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Starts the Spacewalk Daemon
# Description: This is a daemon which handles the task of connecting
#               periodically to the Spacewalk servers to
#               check for updates, notifications and perform system
#               monitoring tasks according to the service level that
#               this server is subscribed for.
### END INIT INFO

echo script_chkconfig+lsb
""".strip()

EMPTY_SCRIPT = "etc/rc.d/init.d/script_empty"
EMPTY_CONTENT = """
""".strip()

HINTSONLY_SCRIPT = "etc/rc.d/init.d/script_hintsonly"
HINTSONLY_CONTENT = """
#!/bin/sh
#

case "$1" in
start)
        ;;
stop)
        ;;
esac
""".strip()


COMMENTS_SCRIPT = "etc/rc.d/init.d/script_comments"
COMMENTS_CONTENT = """
#! bin/broken
#
#
#case "$1" in
#start)
#        ;;
#stop)
#        ;;
#esac
""".strip()

VMTOOLS_CONTENT = """
vmware_auto_kmods() {
   # Check if mods are confed, but not installed.
   vmware_exec_selinux "$vmdb_answer_LIBDIR/sbin/vmware-modconfig-console \
                           --configured-mods-installed" && exit 0

   # Check that we have PBMs, of if not, then kernel headers and gcc.  Otherwise don't waste time
   # check for vmhgfs because that is in all PBM sets
   if ! vmware_exec_selinux "$vmdb_answer_LIBDIR/sbin/vmware-modconfig-console --pbm-available vmhgfs"; then
       vmware_exec_selinux "$vmdb_answer_LIBDIR/sbin/vmware-modconfig-console \
                           --get-kernel-headers" || (echo "No kernel headers" && exit 1)
       vmware_exec_selinux "$vmdb_answer_LIBDIR/sbin/vmware-modconfig-console \
                           --get-gcc" || (echo "No gcc" && exit 1)
   fi

   # We assume config.pl has already been run since our init script is at this point.
   # If so, then lets build whatever mods are configured.
   vmware_exec_selinux "$vmdb_answer_BINDIR/vmware-config-tools.pl --default --modules-only --skip-stop-start"
}

main()
{
   # See how we were called.
   case "$1" in
      start)

         # If the service has already been started exit right away
         [ -f /var/lock/subsys/"$subsys" ] && exit 0

         exitcode='0'
         if [ "`is_acpi_hotplug_needed`" = 'yes' ]; then
            vmware_exec "Checking acpi hot plug" vmware_start_acpi_hotplug
         fi
         if vmware_inVM; then
            if ! is_dsp && [ -e "$vmware_etc_dir"/not_configured ]; then
               echo "`vmware_product_name`"' is installed, but it has not been '
               echo '(correctly) configured for the running kernel.'
               echo 'To (re-)configure it, invoke the following command: '
               echo "$vmdb_answer_BINDIR"'/vmware-config-tools.pl.'
               echo
               exit 1
            fi

            echo 'Starting VMware Tools services in the virtual machine:'
            vmware_exec 'Switching to guest configuration:' vmware_switch
            exitcode=$(($exitcode + $?))

            if [ "`vmware_auto_kmods_enabled`" = 'yes' ] &&
                ! grep -q "vmw_no_akmod" /proc/cmdline; then
                vmware_exec 'VMware Automatic Kmods:' vmware_auto_kmods

                # After doing this reload the database as its contents will have changed
                db_load 'vmdb' "$vmware_db"
            fi

            if [ "`is_pvscsi_needed`" = 'yes' ]; then
                vmware_exec 'Paravirtual SCSI module:' vmware_start_pvscsi
                exitcode=$(($exitcode + $?))
            fi

            if [ "`is_vmmemctl_needed`" = 'yes' ]; then
               vmware_exec 'Guest memory manager:' vmware_start_vmmemctl
               exitcode=$(($exitcode + $?))
            fi

            if [ "`is_vmxnet_needed`" = 'yes' ]; then
               vmware_exec 'Guest vmxnet fast network device:' vmware_start_vmxnet
               exitcode=$(($exitcode + $?))
            fi

            if [ "`is_vmxnet3_needed`" = 'yes' ]; then
               vmware_exec 'Driver for the VMXNET 3 virtual network card:' vmware_start_vmxnet3
               exitcode=$(($exitcode + $?))
            fi

            if [ "`is_vmci_needed`" = 'yes' ]; then
               vmware_exec 'VM communication interface:' vmware_start_vmci
            fi

         # vsock needs vmci started first
            if [ "`is_vsock_needed`" = 'yes' ]; then
               vmware_exec 'VM communication interface socket family:' vmware_start_vsock
               exitcode=$(($exitcode + $?))
            fi

            if [ "`is_vmhgfs_needed`" = 'yes' -a "`is_ESX_running`" = 'no' ]; then
               vmware_exec 'Guest filesystem driver:' vmware_start_vmhgfs
               exitcode=$(($exitcode + $?))
               vmware_exec 'Mounting HGFS shares:' vmware_mount_vmhgfs
        # Ignore the exitcode. The mount may fail if HGFS is disabled
        # in the host, in which case requiring a rerun of the Tools
        # configurator is useless.
            fi

            if [ "`is_vmblock_needed`" = 'yes' ] ; then
               vmware_exec 'Blocking file system:' vmware_start_vmblock
               exitcode=$(($exitcode + $?))
            fi

               # Signal vmware-user to relaunch itself and maybe restore
               # contact with the blocking file system.
            if [ "`is_vmware_user_running`" = 'yes' ]; then
               vmware_exec 'VMware User Agent:' vmware_restart_vmware_user
            fi

            if [ "`is_vmsync_needed`" = 'yes' ] ; then
               vmware_exec 'File system sync driver:' vmware_start_vmsync
               exitcode=$(($exitcode + $?))
            fi

            if [ "`is_vmtoolsd_needed`" = 'yes' ] ; then
              vmware_exec 'Guest operating system daemon:' vmware_start_daemon $SYSTEM_DAEMON
            fi

            if [ "$have_vgauth" = "yes" -a "`vmware_vgauth_enabled`" = "yes" ]; then
              vmware_exec "$VGAUTHSVC:" vmware_start_vgauth
              exitcode=$(($exitcode + $?))
            fi

            if [ "$have_caf" = "yes" -a "`vmware_caf_enabled`" = "yes" ]; then
              vmware_exec 'Common Agent:' vmware_start_caf
              exitcode=$(($exitcode + $?))
            fi

         else
            echo 'Starting VMware Tools services on the host:'
            vmware_exec 'Switching to host config:' vmware_switch
            exitcode=$(($exitcode + $?))
         fi

         if ! is_dsp && [ "$exitcode" -gt 0 ]; then
            exit 1
         fi

         [ -d /var/lock/subsys ] || mkdir -p /var/lock/subsys
         touch /var/lock/subsys/"$subsys"
         ;;

      stop)
         exitcode='0'

         if vmware_inVM; then

            echo 'Stopping VMware Tools services in the virtual machine:'

            if [ "`is_vmtoolsd_needed`" = 'yes' ] ; then
              vmware_exec 'Guest operating system daemon:' vmware_stop_daemon $SYSTEM_DAEMON
              exitcode=$(($exitcode + $?))
            fi

            if [  "$have_caf" = "yes" -a "`vmware_caf_enabled`" = "yes" ]; then
              vmware_exec 'Common Agent:' vmware_stop_caf
            fi

            if [  "$have_vgauth" = "yes" -a "`vmware_vgauth_enabled`" = "yes" ]; then
              vmware_exec "$VGAUTHSVC:" vmware_stop_vgauth
              exitcode=$(($exitcode + $?))
            fi

            # Signal vmware-user to release any contact with the blocking fs, closing rpc connections etc.
            vmware_exec 'VMware User Agent (vmware-user):' vmware_user_request_release_resources
            rv=$?
            exitcode=$(($exitcode + $rv))

            if [ "`is_vmblock_needed`" = 'yes' ] ; then
               # If unblocking vmware-user fails then stopping and unloading vmblock
               # probably will also fail.
               if [ $rv -eq 0 ]; then
                  vmware_exec 'Blocking file system:' vmware_stop_vmblock
                  exitcode=$(($exitcode + $?))
               fi
            fi

            vmware_exec 'Unmounting HGFS shares:' vmware_unmount_vmhgfs
            rv=$?
            vmware_exec 'Guest filesystem driver:' vmware_stop_vmhgfs
            rv=$(($rv + $?))
            if [ "`is_vmhgfs_needed`" = 'yes' ]; then
               exitcode=$(($exitcode + $rv))
            fi

            if [ "`is_vmmemctl_needed`" = 'yes' ]; then
               vmware_exec 'Guest memory manager:' vmware_stop_vmmemctl
               exitcode=$(($exitcode + $?))
            fi

         # vsock requires vmci to work so it must be unloaded before vmci
            if [ "`is_vsock_needed`" = 'yes' ]; then
               vmware_exec 'VM communication interface socket family:' vmware_stop_vsock
               exitcode=$(($exitcode + $?))
            fi

            if [ "`is_vmci_needed`" = 'yes' ]; then
               vmware_exec 'VM communication interface:' vmware_stop_vmci
               exitcode=$(($exitcode + $?))
            fi

            if [ "`is_vmsync_needed`" = 'yes' ] ; then
               vmware_exec 'File system sync driver:' vmware_stop_vmsync
               exitcode=$(($exitcode + $?))
            fi

         else
            echo -n 'Skipping VMware Tools services shutdown on the host:'
            vmware_success
            echo
         fi
         if [ "$exitcode" -gt 0 ]; then
            exit 1
         fi

         rm -f /var/lock/subsys/"$subsys"
         ;;

      status)
         exitcode='0'

         vmware_daemon_status $SYSTEM_DAEMON
         exitcode=$(($exitcode + $?))

         if [ "$exitcode" -ne 0 ]; then
            exit 1
         fi
         ;;

      restart | force-reload)
         "$0" stop && "$0" start
         ;;
      source)
         # Used to source the script so that functions can be
         # selectively overriden.
         return 0
         ;;
      *)
         echo "Usage: `basename "$0"` {start|stop|status|restart|force-reload}"
         exit 1
   esac

   exit 0
}

main "$@"
""".strip()
VMTOOLS_SCRIPT = "etc/rc.d/init.d/vmware-tools"


def test_initscript1():
    context = context_wrap(NOTINITSCRIPT_CONTENT, path=NOTINITSCRIPT_SCRIPT)
    with pytest.raises(NotInitscriptException) as e_info:
        InitScript(context)
    assert context.path in str(e_info.value)
    assert "confidence: 1" in str(e_info.value)


def test_initscript2():
    context = context_wrap(CHKCONFIG_CONTENT, path=CHKCONFIG_SCRIPT)
    r = InitScript(context)
    assert r.file_name == "script_chkconfig"


def test_initscript3():
    context = context_wrap(LSB_CONTENT, path=LSB_SCRIPT)
    r = InitScript(context)
    assert r.file_name == "script_lsb"


def test_initscript4():
    context = context_wrap(CHKCONFIG_LSB_CONTENT, path=CHKCONFIG_LSB_SCRIPT)
    r = InitScript(context)
    assert r.file_name == "script_chkconfig+lsb"


def test_initscript5():
    context = context_wrap(HINTSONLY_CONTENT, path=HINTSONLY_SCRIPT)
    r = InitScript(context)
    assert r.file_name == "script_hintsonly"


def test_initscript6():
    context = context_wrap(EMPTY_CONTENT, path=EMPTY_SCRIPT)
    with pytest.raises(EmptyFileException) as e_info:
        InitScript(context)
    assert context.path in str(e_info.value)


def test_initscript7():
    context = context_wrap(COMMENTS_CONTENT, path=COMMENTS_SCRIPT)
    with pytest.raises(NotInitscriptException) as e_info:
        InitScript(context)
    assert context.path in str(e_info.value)
    assert "confidence: 0" in str(e_info.value)


def test_vmwtools():
    context = context_wrap(VMTOOLS_CONTENT, path=VMTOOLS_SCRIPT)
    ret = VMWTools(context)
    assert 'vmware-tools' in ret.file_path
    assert ret.file_name == 'vmware-tools'

    context = context_wrap(NOTINITSCRIPT_CONTENT, path=VMTOOLS_SCRIPT)
    with pytest.raises(NotInitscriptException) as e_info:
        VMWTools(context)
    assert context.path in str(e_info.value)
    assert "confidence: 1" in str(e_info.value)


def test_vmwtools_doc_examples():
    env = {
            'initobj': InitScript(context_wrap(VMTOOLS_CONTENT, path=VMTOOLS_SCRIPT)),
            'vmwtools': VMWTools(context_wrap(VMTOOLS_CONTENT, path=VMTOOLS_SCRIPT))
    }
    failed, total = doctest.testmod(initscript, globs=env)
    assert failed == 0
