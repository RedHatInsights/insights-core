"""
Custom datasources to get the iris working configuration/log files.
"""
import os

from insights.core.context import HostContext
from insights.core.exceptions import ContentException, SkipComponent
from insights.parsers.iris import IrisList
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs


@datasource(IrisList, HostContext)
def iris_working_configuration(broker):
    """
    This datasource get information from ``iris.cpf`` file.

    Returns:
        str: the raw content of the ``iris.cpf`` file .

    Raises:
        SkipComponent: When the `iris.cpf` does not exist or nothing need to collect
        ContentException: When any exception occurs.
    """
    configuration_file_path_directory = broker[IrisList]['directory']
    configuration_file_path_conf_file = broker[IrisList]['conf file'].split()[0].strip()

    configuration_file_path = configuration_file_path_directory + '/' + configuration_file_path_conf_file

    if not os.path.isfile(configuration_file_path):
        raise SkipComponent("No such file")
    try:
        relative_path = 'insights_commands/iris_cpf'
        with open(configuration_file_path, 'r') as conf:
            return DatasourceProvider(content=conf.read(), relative_path=relative_path)
    except Exception as e:
        raise ContentException(e)


# def get_filter_log_messages(log_path, filters):
#     print ("20202020")
#     print (log_path)
#     print (filters)
#     with open(log_path, 'r') as log_file:
#         filtered_content = []
#         if filters:
#             for line in log_file.readlines():
#                 for filter in filters:
#                     if filter in line:
#                         filtered_content.append(line)
#                         break
#             if filtered_content:
#                 return filtered_content


@datasource(IrisList, HostContext)
def iris_working_messages_log(broker):
    """
    This datasource get information from ``messages.log`` file.

    Returns:
        str: the raw content of the ``messages.log`` file .

    Raises:
        SkipComponent: When the files do not exist
        ContentException: When any exception occurs.
    """
    filters = sorted((get_filters(Specs.intersystems_iris_messages_log_filter)))
    configuration_file_path_directory = broker[IrisList]['directory']
    configuration_file_path_conf_file = broker[IrisList]['conf file'].split()[0].strip()

    configuration_file_path = configuration_file_path_directory + '/' + configuration_file_path_conf_file

    if not os.path.isfile(configuration_file_path):
        raise SkipComponent("No such configuration file")

    log_path = ""
    with open(configuration_file_path, 'r') as conf:
        for line in conf.readlines():
            if "IRISSYS=" in line:
                log_directory = line.split("=")[1].strip()
                if not log_directory.endswith("/"):
                    log_directory = log_directory + "/"
                log_path = log_directory + "messages.log"
                break
        if not os.path.isfile(log_path):
            raise SkipComponent("No such log file")

    try:
        relative_path = 'insights_commands/iris_messages_log'
        with open(log_path, 'r') as log_file:
            filtered_content = []
            if filters:
                for line in log_file.readlines():
                    for filter in filters:
                        if filter in line:
                            filtered_content.append(line)
                            break
            return DatasourceProvider(content="".join(filtered_content), relative_path=relative_path)
    except Exception as e:
        raise ContentException(e)
