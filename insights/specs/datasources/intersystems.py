"""
Custom datasources to get the iris working configuration/log files.
"""
import os

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.iris import IrisList, IrisCpf


@datasource(IrisList, HostContext)
def iris_working_configuration(broker):
    """
    This datasource get information from ``iris.cpf`` file.

    Returns:
        str: the raw content of the ``iris.cpf`` file .

    Raises:
        SkipComponent: When the `iris.cpf` does not exist
        ContentException: When any exception occurs.
    """
    all_paths = []
    for key, value in broker[IrisList].items():
        configuration_file_path_directory = value['directory']
        configuration_file_path_conf_file = value['conf file'].split()[0].strip()

        configuration_file_path = os.path.join(configuration_file_path_directory, configuration_file_path_conf_file)
        if os.path.isfile(configuration_file_path):
            all_paths.append(configuration_file_path)
    if all_paths:
        return all_paths
    raise SkipComponent


@datasource(IrisCpf, HostContext)
def iris_working_messages_log(broker):
    """
    This datasource get information from ``messages.log`` file.

    Returns:
        str: the filtered content of the ``messages.log`` file .

    Raises:
        SkipComponent: When the log file/option/filters do not exist
        ContentException: When any exception occurs.
    """
    iris_cpf = broker[IrisCpf]
    all_paths = []
    for item in iris_cpf:
        if item.has_option('config', 'console') and item.has_option('Databases', 'IRISSYS'):
            primary_log_path = item.get("config", "console").split(",")[-1]
            if primary_log_path:
                log_path = primary_log_path
            else:
                secondary_log_path = item.get("Databases", "IRISSYS")
                log_path = os.path.join(secondary_log_path, 'messages.log')
            if os.path.isfile(log_path):
                all_paths.append(log_path)
    if all_paths:
        return all_paths
    raise SkipComponent
