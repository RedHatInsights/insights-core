"""
Custom datasources to get the iris working configuration/log files.
"""
import os

from insights.core.context import HostContext
from insights.core.exceptions import ContentException, SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.parsers.iris import IrisList, IrisCpf
from insights.specs import Specs


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
    configuration_file_path_directory = broker[IrisList]['directory']
    configuration_file_path_conf_file = broker[IrisList]['conf file'].split()[0].strip()

    configuration_file_path = os.path.join(configuration_file_path_directory, configuration_file_path_conf_file)
    if os.path.isfile(configuration_file_path):
        try:
            with open(configuration_file_path, 'r') as conf:
                return DatasourceProvider(content=conf.read(), relative_path=configuration_file_path)
        except Exception as e:
            raise ContentException(e)
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
    filters = sorted((get_filters(Specs.iris_messages_log)))
    iris_cpf = broker[IrisCpf]

    if filters and iris_cpf.has_option('Databases', 'IRISSYS'):
        log_path = iris_cpf.get("Databases", "IRISSYS")
        log_path = os.path.join(log_path, 'messages.log')
        if os.path.isfile(log_path):
            try:
                with open(log_path, 'r') as log:
                    filtered_content = []
                    for line in log.readlines():
                        filtered_content.append(line) if any(_f in line for _f in filters) else None
                    return DatasourceProvider(content="".join(filtered_content), relative_path=log_path)
            except Exception as e:
                raise ContentException(e)
    raise SkipComponent
