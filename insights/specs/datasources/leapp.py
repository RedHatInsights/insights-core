"""
Custom datasources for leapp
"""
import json

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_file
from insights.specs import Specs


class LocalSpecs(Specs):
    leapp_report_raw = simple_file("/var/log/leapp/leapp-report.json")
    """ Returns the contents of the file ``/var/log/leapp/leapp-report.json`` """


@datasource(LocalSpecs.leapp_report_raw, HostContext)
def leapp_report(broker):
    """
    This datasource get useful information from ``leapp-report.json``.

    .. note::
        Since this file may contain sensitive information, this datasource does
        filter and only keep required data.

    Returns:
        str: JSON string after get the required data.

    Raises:
        SkipComponent: When the path does not exist, nothing is collected,
                       or any exception occurs.
    """
    relative_path = 'insights_commands/leapp_report'
    valid_keys = {
        'inhibitor': ['title', 'summary', ('detail', 'remediations')]
    }
    try:
        content = broker[LocalSpecs.leapp_report_raw].content
        report = json.loads('\n'.join(content))
        if isinstance(report, dict):
            results = []
            for entry in report.get('entries', []):
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
                return DatasourceProvider(content=json.dumps(results), relative_path=relative_path)
        raise SkipComponent("Invalid format")
    except Exception as e:
        raise SkipComponent(e)
    raise SkipComponent
