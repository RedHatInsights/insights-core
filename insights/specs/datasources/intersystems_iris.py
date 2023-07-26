"""
Custom datasources to get the iris working configuration file.
"""
import os

from insights.core.context import HostContext
from insights.core.exceptions import ContentException, SkipComponent
from insights.parsers.iris import IrisList
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


# @datasource(IrisList, HostContext)
# def iris_working_configuration(broker):
#     """
#     This datasource get information from ``iris.cpf`` file.
#
#     Returns:
#         str: the raw content of the ``iris.cpf`` file .
#
#     Raises:
#         SkipComponent: When the `iris.cpf` does not exist or nothing need to collect
#         ContentException: When any exception occurs.
#     """
#     configuration_file_path = broker[IrisList]['directory'] + "/iris.cpf"
#     if not os.path.isfile(configuration_file_path):
#         raise SkipComponent("No such file")
#     try:
#         relative_path = 'insights_commands/iris_cpf'
#         with open(configuration_file_path, 'r') as conf:
#             return DatasourceProvider(content=conf.read(), relative_path=relative_path)
#     except Exception as e:
#         raise ContentException(e)

class LocalSpecs(Specs):
    """ Local specs used only by awx_manage datasources """

    iris_list_local = simple_command("/usr/bin/iris list")


@datasource(LocalSpecs.iris_list_local, HostContext)
def iris_working_configuration(broker):
    """
    This datasource get information from ``iris.cpf`` file.

    Returns:
        str: the raw content of the ``iris.cpf`` file .

    Raises:
        SkipComponent: When the `iris.cpf` does not exist or nothing need to collect
        ContentException: When any exception occurs.
    """
    # iris_list_content = broker[Specs.iris_list].content
    iris_list_content = broker[LocalSpecs.iris_list_local].content
    iris_working_directory = ""
    iris_working_cpf_name = ""
    for line in iris_list_content:
        if "directory:" in line:
            iris_working_directory = line.split(":", 1)[-1].strip()
        if "conf file:" in line:
            iris_working_cpf_name = line.split(":", 1)[-1].strip().split()[0].strip()
    if iris_working_directory and iris_working_cpf_name:
        configuration_file_path = iris_working_directory + "/" + iris_working_cpf_name
    else:
        raise SkipComponent("Can not find the configuration file path")
    if not os.path.isfile(configuration_file_path):
        raise SkipComponent("No such file")
    try:
        relative_path = 'insights_commands/iris_cpf'
        with open(configuration_file_path, 'r') as conf:
            return DatasourceProvider(content=conf.read(), relative_path=relative_path)
    except Exception as e:
        raise ContentException(e)


@datasource(LocalSpecs.iris_list_local, HostContext)
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
    iris_list_content = broker[LocalSpecs.iris_list_local].content
    iris_working_directory = ""
    iris_working_cpf_name = ""
    for line in iris_list_content:
        if "directory:" in line:
            iris_working_directory = line.split(":", 1)[-1].strip()
        if "conf file:" in line:
            iris_working_cpf_name = line.split(":", 1)[-1].strip().split()[0].strip()
    if iris_working_directory and iris_working_cpf_name:
        configuration_file_path = iris_working_directory + "/" + iris_working_cpf_name
    else:
        raise SkipComponent("Can not find the configuration file path")
    if not os.path.isfile(configuration_file_path):
        raise SkipComponent("No such configuration file")

    with open(configuration_file_path, 'r') as conf:
        log_directory = ""
        for line in conf.readlines():
            if "IRISSYS=" in line:
                log_directory = line.split("=")[1].strip()
                if not log_directory.endswith("/"):
                    log_directory = log_directory + "/"
            log_path = log_directory + "messages.log"
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