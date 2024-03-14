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
        SkipComponent: When the file does not exist or nothing need to collect
        ContentException: When any exception occurs.
    """
    valid_keys = {
        'inhibitor': ['title', 'summary', 'detail']
    }
    leapp_report_path = "/var/log/leapp/leapp-report.json"
    if not os.path.isfile(leapp_report_path):
        raise SkipComponent("No such file")
    try:
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
                    relative_path = 'insights_commands/leapp_report'
                    return DatasourceProvider(content=json.dumps(results), relative_path=relative_path)
                raise SkipComponent("Nothing")
    except Exception as e:
        raise ContentException(e)


@datasource(HostContext)
def migration_results(broker):
    """
    This datasource get useful information from ``/etc/migration-results``.

    .. note::
        Since this file may contain sensitive information, this datasource does
        filter and only keep required data.

    Returns:
        str: JSON string after get the required data.

    Raises:
        SkipComponent: When the file does not exist or nothing need to collect
        ContentException: When any exception occurs.
    """
    valid_keys = {
        'activity': None,
        'activity_ended': None,
        'activity_started': None,
        'env': lambda env_var: env_var.startswith('LEAPP_') or env_var.startswith('CONVERT2RHEL_'),
        'run_id': None,
        'source_os': None,
        'success': None,
        'target_os': None,
        'version': None,
    }
    migration_results_file = "/etc/migration-results"
    if not os.path.isfile(migration_results_file):
        raise SkipComponent("No such file")
    try:
        with open(migration_results_file, 'r') as fp:
            json_report = json.load(fp)
            if isinstance(json_report, dict):
                results = []
                for activity in json_report.get('activities', []):
                    ret = {}
                    for key, filter_fn in valid_keys.items():
                        if key not in activity:
                            continue
                        val = activity.get(key)
                        if filter_fn is None or not val:
                            ret[key] = val
                        elif isinstance(val, dict) and callable(filter_fn):
                            sub_ret = dict(
                                (sub_key, sub_val)
                                for sub_key, sub_val in val.items()
                                if filter_fn(sub_key)
                            )
                            if sub_ret:
                                ret[key] = sub_ret
                    results.append(ret) if ret else None
                if results:
                    relative_path = 'insights_commands/leapp_migration_results'
                    return DatasourceProvider(content=json.dumps(results), relative_path=relative_path)
                raise SkipComponent("Nothing")
    except Exception as e:
        raise ContentException(e)
