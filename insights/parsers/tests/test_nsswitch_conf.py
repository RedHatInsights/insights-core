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

from insights.parsers.nsswitch_conf import NSSwitchConf
from insights.tests import context_wrap

NSSWITCH = """
# To use db, put the "db" in front of "files" for entries you want to be
# looked up first in the databases
#
# Example:
#passwd:    db files nisplus nis
#shadow:    db files nisplus nis
#group:     db files nisplus nis

passwd:     files sss
shadow:     files sss
group:      files sss
#initgroups: files

#hosts:     db files nisplus nis dns
hosts:      files dns myhostname

# Example - obey only what nisplus tells us...
#services:   nisplus [NOTFOUND=return] files
#networks:   nisplus [NOTFOUND=return] files
#protocols:  nisplus [NOTFOUND=return] files
#rpc:        nisplus [NOTFOUND=return] files
#ethers:     nisplus [NOTFOUND=return] files
#netmasks:   nisplus [NOTFOUND=return] files

bootparams: nisplus [NOTFOUND=return] files

"""

NSSWITCH_ERROR = """
passwd      files sss DNS
GROUP:      Files SSS
"""


def test_nsswitch_conf():
    nss = NSSwitchConf(context_wrap(NSSWITCH, path='/etc/nsswitch.conf'))
    assert hasattr(nss, 'data')
    assert hasattr(nss, 'errors')
    assert hasattr(nss, 'sources')

    assert sorted(nss.data.keys()) == sorted([
        'passwd', 'shadow', 'group', 'hosts', 'bootparams'
    ])
    assert nss.errors == []
    assert nss.sources == set([
        'files', 'sss', 'dns', 'myhostname', 'nisplus', '[notfound=return]'
    ])

    assert 'passwd' in nss
    assert 'initgroups' not in nss
    assert nss['passwd'] == 'files sss'
    assert nss['bootparams'] == 'nisplus [notfound=return] files'


def test_nsswitch_errors():
    nss = NSSwitchConf(context_wrap(NSSWITCH_ERROR, path='/etc/nsswitch.conf'))
    assert hasattr(nss, 'data')
    assert hasattr(nss, 'errors')
    assert hasattr(nss, 'sources')

    # Test that valid contents are stored in lower case
    assert nss.data == {'group': 'files sss'}
    # Invalid lines are stored as is
    assert nss.errors == [
        'passwd      files sss DNS'
    ]
    assert nss.sources == set(['files', 'sss'])
