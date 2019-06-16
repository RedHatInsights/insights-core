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
This module defines all datasources for JDR report
"""

from functools import partial
from insights.specs import Specs
from insights.core.plugins import datasource
from insights.core.context import JDRContext
from insights.core.spec_factory import simple_file, foreach_collect, first_file, glob_file, listdir

first_file = partial(first_file, context=JDRContext)
glob_file = partial(glob_file, context=JDRContext)
simple_file = partial(simple_file, context=JDRContext)
foreach_collect = partial(foreach_collect, context=JDRContext)


class JDRSpecs(Specs):
    """A class for all the JDR report datasources"""

    jboss_standalone_server_log = glob_file("JBOSS_HOME/standalone/log/server.log")

    @datasource(jboss_standalone_server_log, context=JDRContext, multi_output=True)
    def jboss_standalone_conf_file(broker):
        """Get which jboss standalone conf file is using from server log"""
        log_files = broker[JDRSpecs.jboss_standalone_server_log]
        if log_files:
            log_content = log_files[-1].content
            results = []
            for line in log_content:
                if "sun.java.command =" in line and ".jdr" not in line and "-Djboss.server.base.dir" in line:
                    results.append(line)
            if results:
                # default is standalone.xml
                config_xml = 'standalone.xml'
                java_command = results[-1]
                if '--server-config' in java_command:
                    config_xml = java_command.split('--server-config=')[1].split()[0]
                elif '-c ' in java_command:
                    config_xml = java_command.split('-c ')[1].split()[0]
                return [config_xml]
        return []

    # Get file content according the file name from server.log
    jboss_standalone_main_config = foreach_collect(jboss_standalone_conf_file, "JBOSS_HOME/standalone/configuration/%s")

    jboss_domain_servers = listdir("JBOSS_HOME/domain/servers/", context=JDRContext)
    jboss_domain_server_log = foreach_collect(jboss_domain_servers, "JBOSS_HOME/domain/servers/%s/log/server.log")
