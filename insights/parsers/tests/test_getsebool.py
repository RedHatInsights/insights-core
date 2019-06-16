#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pytest
from insights.parsers import getsebool, SkipException
from insights.tests import context_wrap


GETSEBOOL = """
varnishd_connect_any --> off
virt_read_qemu_ga_data --> off
virt_rw_qemu_ga_data --> off
virt_sandbox_use_all_caps --> on
virt_sandbox_use_audit --> on
virt_sandbox_use_fusefs --> off
virt_sandbox_use_mknod --> off
virt_sandbox_use_netlink --> off
virt_sandbox_use_sys_admin --> off
virt_transition_userdomain --> off
virt_use_comm --> off
virt_use_execmem --> off
virt_use_fusefs --> off
virt_use_glusterd --> off
virt_use_nfs --> on
virt_use_rawip --> off
virt_use_samba --> off
virt_use_sanlock --> off
virt_use_usb --> on
virt_use_xserver --> off
""".strip()

SELINUX_DISABLED = '/usr/sbin/getsebool:  SELinux is disabled'


def test_getsebool():
    result = getsebool.Getsebool(context_wrap(GETSEBOOL))
    assert result["varnishd_connect_any"] == 'off'
    assert result["virt_use_nfs"] == 'on'
    assert "virt_use_xserver" in result
    assert "not_exist_key" not in result


def test_getsebool_disabled():
    with pytest.raises(SkipException) as excinfo:
        getsebool.Getsebool(context_wrap(SELINUX_DISABLED))
    assert 'SELinux is disabled' in str(excinfo.value)
