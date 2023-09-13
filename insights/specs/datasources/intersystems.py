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
        list: the file path of the ``iris.cpf`` files

    Raises:
        SkipComponent: there is no `iris.cpf` file
    """
    all_paths = []
    for item in broker[IrisList]:
        conf_directory = item['directory']
        conf_file = item['conf file'].split()[0].strip()

        file_path = os.path.join(conf_directory, conf_file)
        if os.path.isfile(file_path):
            all_paths.append(file_path)
    if all_paths:
        return all_paths
    raise SkipComponent


@datasource(IrisCpf, HostContext)
def iris_working_messages_log(broker):
    """
    This datasource get information from ``messages.log`` file.

    Returns:
        list: the file path of the ``messages.log`` files

    Raises:
        SkipComponent: there is no `messages.log` file
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
