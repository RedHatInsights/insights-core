from functools import partial
from insights.specs import Specs
from insights.core.plugins import datasource
from insights.core.context import JDRContext
from insights.core.spec_factory import simple_file, foreach_collect, first_file, glob_file, listdir

first_file = partial(first_file, context=JDRContext)
glob_file = partial(glob_file, context=JDRContext)
simple_file = partial(simple_file, context=JDRContext)


class JDRSpecs(Specs):
    # Here use glob_file is to return list type result to keep same with  jboss specs default.py
    # jdr just collect files under one jboss home,
    # For insights-client, we will collect files under different jboss home, return list is necessary.
    jboss_standalone_server_log = glob_file("JBOSS_HOME/standalone/log/server.log")

    @datasource(jboss_standalone_server_log, context=JDRContext, multi_output=True)
    def jboss_standlone_conf_file(broker):
        # read the server.log to detect if specific xml is using in the startup command
        # the server.log maybe overwrite,  so just return []
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
                return config_xml
        return []

    # use foreach is to return list type result as jboss sepcs in defaults.py
    jboss_standalone_main_config = foreach_collect(jboss_standlone_conf_file,
                                                   "JBOSS_HOME/standalone/configuration/%s",
                                                   context=JDRContext)

    jboss_domain_servers = listdir("JBOSS_HOME/domain/servers/", context=JDRContext)
    jboss_domain_server_log = foreach_collect(jboss_domain_servers,
                                              "JBOSS_HOME/domain/servers/%s/log/server.log",
                                              context=JDRContext)
