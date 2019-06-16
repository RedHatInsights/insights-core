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

"""
ClusterConf - file ``/etc/cluster/cluster.conf``
================================================

Stores a filtered set of lines from the cluster config file.  Because of the
filtering, the content as a whole will not parse as XML.  We use a
:class:`insights.core.LogFileOutput` parser class because, sadly, it's
easiest.
"""
from .. import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.cluster_conf)
class ClusterConf(LogFileOutput):
    """
    Parse the ``/etc/cluster/cluster.conf`` file as a list of lines.  ``get``
    can be used to find lines containing one or more keywords.  Because of
    filters used on this file, we cannot parse this as XML.
    """
    pass
