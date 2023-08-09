"""
Custom datasources for leapp
"""
import json
import os

from insights.core.context import HostContext
from insights.core.exceptions import ContentException, SkipComponent
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
        SkipComponent: When the `leapp_report.json` does not exist or nothing need to collect
        ContentException: When any exception occurs.
    """
    leapp_report_path = "/var/log/leapp/leapp-report.json"
    if not os.path.isfile(leapp_report_path):
        raise SkipComponent("No such file")
    try:
        relative_path = 'insights_commands/leapp_report'
        valid_keys = {
            'inhibitor': ['title', 'summary', 'detail']
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
                                detail = entry.get(key)
                                ret.update(detail if isinstance(detail, dict) else {key: detail}) if detail else None
                            results.append(ret)
                if results:
                    return DatasourceProvider(content=json.dumps(results), relative_path=relative_path)
                raise SkipComponent("Nothing")
    except Exception as e:
        raise ContentException(e)
