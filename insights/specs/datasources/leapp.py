"""
Custom datasources for leapp
"""
import json

from insights.core.context import HostContext
from insights.core.exceptions import ContentException
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider


@datasource(HostContext)
def leapp_report(broker):
    """
    This datasource get useful information from ``leapp-report.json``.

    .. note::
        Since this file may contain sensitive information, this datasource does
        filter and only keep required data.

    Returns:
        str: JSON string after get the required data.

    Raises:
        ContentException: When the path does not exist, nothing is collected,
                          or any exception occurs.
    """
    leapp_report_path = "/var/log/leapp/leapp-report.json"
    try:
        relative_path = 'insights_commands/leapp_report'
        valid_keys = {
            'inhibitor': ['title', 'summary', ('detail', 'remediations')]
        }
        with open(leapp_report_path, 'r') as fp:
            json_report = json.load(fp)
            if isinstance(json_report, dict):
                results = []
                for entry in json_report.get('entries', []):
                    groups = entry.get('groups', entry.get('flags', []))
                    for flag, keys in valid_keys.items():
                        if flag in groups:
                            ret = dict(groups=groups)
                            for key in keys:
                                if isinstance(key, tuple):
                                    tmp = entry
                                    for k in key:
                                        tmp = tmp[k]
                                    ret[key[-1]] = tmp
                                else:
                                    ret[key] = entry[key]
                            results.append(ret)
                if results:
                    print('results=', results)
                    return DatasourceProvider(content=json.dumps(results), relative_path=relative_path)
    except Exception as e:
        raise ContentException(e)
    raise ContentException("Invalid JSON format")
