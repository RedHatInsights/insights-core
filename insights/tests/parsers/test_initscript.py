import pytest

from insights.parsers.initscript import InitScript, EmptyFileException, NotInitscriptException
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
