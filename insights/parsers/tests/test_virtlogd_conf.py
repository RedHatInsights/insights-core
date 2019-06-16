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

import doctest

from insights.parsers import virtlogd_conf
from insights.tests import context_wrap


VIRTLOGD_CONF = '''
# Master virtlogd daemon configuration file
#

#################################################################
#
# Logging controls
#

# Logging level: 4 errors, 3 warnings, 2 information, 1 debug
# basically 1 will log everything possible
#log_level = 3

# Logging filters:
# A filter allows to select a different logging level for a given category
# of logs
# The format for a filter is one of:
#    x:name
#    x:+name
#      where name is a string which is matched against source file name,
#      e.g., "remote", "qemu", or "util/json", the optional "+" prefix
#      tells libvirt to log stack trace for each message matching name,
#      and x is the minimal level where matching messages should be logged:
#    1: DEBUG
#    2: INFO
#    3: WARNING
#    4: ERROR
#
# Multiple filter can be defined in a single @filters, they just need to be
# separated by spaces.
#
# e.g. to only get warning or errors from the remote layer and only errors
# from the event layer:
#log_filters="3:remote 4:event"

# Logging outputs:
# An output is one of the places to save logging information
# The format for an output can be:
#    x:stderr
#      output goes to stderr
#    x:syslog:name
#      use syslog for the output and use the given name as the ident
#    x:file:file_path
#      output to a file, with the given filepath
#    x:journald
#      ouput to the systemd journal
# In all case the x prefix is the minimal level, acting as a filter
#    1: DEBUG
#    2: INFO
#    3: WARNING
#    4: ERROR
#
# Multiple output can be defined, they just need to be separated by spaces.
# e.g. to log all warnings and errors to syslog under the virtlogd ident:
#log_outputs="3:syslog:virtlogd"
#

# The maximum number of concurrent client connections to allow
# over all sockets combined.
#max_clients = 1024


# Maximum file size before rolling over. Defaults to 2 MB
#max_size = 2097152

# Maximum number of backup files to keep. Defaults to 3,
# not including the primary active file
max_backups = 3
'''


def test_virtlogd_conf():
    conf = virtlogd_conf.VirtlogdConf(context_wrap(VIRTLOGD_CONF, path='/etc/libvirt/virtlogd.conf'))
    assert conf.get('max_backups') == '3'

    conf = virtlogd_conf.VirtlogdConf(context_wrap(VIRTLOGD_CONF.replace("#max_size = 2097152", "max_size = 12582912")))
    max_size = conf.get('max_size', None)
    assert int(max_size) == 12582912


def test_virtlogd_conf_documentation():
    failed_count, tests = doctest.testmod(
        virtlogd_conf,
        globs={'conf': virtlogd_conf.VirtlogdConf(context_wrap(VIRTLOGD_CONF))}
    )
    assert failed_count == 0
