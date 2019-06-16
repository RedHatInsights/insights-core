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

from insights.configtree import first
from insights.combiners.logrotate_conf import _LogRotateConf, LogRotateConfTree
from insights.tests import context_wrap


CONF = """
# see "man logrotate" for details
# rotate log files weekly
weekly

# keep 4 weeks worth of backlogs
rotate 4

# create new (empty) log files after rotating old ones
create

# use date as a suffix of the rotated file
dateext

# uncomment this if you want your log files compressed
#compress

# RPM packages drop log rotation information into this directory
include /etc/logrotate.d

# no packages own wtmp and btmp -- we'll rotate them here
/var/log/wtmp {
    missingok
    monthly
    create 0664 root utmp
    minsize 1M
    rotate 1
    postrotate
        do some stuff to wtmp
    endscript
}

/var/log/btmp {
    missingok
    monthly
    create 0600 root utmp
    postrotate
        do some stuff to btmp
    endscript
    rotate 1
}

# system-specific logs may be also be configured here.
""".strip()


def test_logrotate_tree():
    p = _LogRotateConf(context_wrap(CONF, path="/etc/logrotate.conf"))
    conf = LogRotateConfTree([p])
    assert len(conf["weekly"]) == 1
    assert len(conf["/var/log/wtmp"]["missingok"]) == 1
    assert conf["/var/log/wtmp"]["postrotate"][first].value == "do some stuff to wtmp"

    assert len(conf["/var/log/btmp"]["rotate"]) == 1
    assert len(conf["/var/log/btmp"]["postrotate"]) == 1
    assert conf["/var/log/btmp"]["postrotate"][first].value == "do some stuff to btmp"
