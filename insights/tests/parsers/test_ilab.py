import doctest
import pytest

from insights.core.exceptions import SkipComponent, ParseException
from insights.parsers import ilab
from insights.parsers.ilab import IlabModuleList
from insights.tests import context_wrap

ILAB_MODULE_LIST = """
+-----------------------------------+---------------------+---------+
| Model Name                        | Last Modified       | Size    |
+-----------------------------------+---------------------+---------+
| models/prometheus-8x7b-v2-0       | 2024-08-09 13:28:50 |  87.0 GB|
| models/mixtral-8x7b-instruct-v0-1 | 2024-08-09 13:28:24 |  87.0 GB|
| models/granite-7b-redhat-lab      | 2024-08-09 14:28:40 |  12.6 GB|
| models/granite-7b-starter         | 2024-08-09 14:40:35 |  12.6 GB|
+-----------------------------------+---------------------+---------+
""".strip()

ILAB_MODULE_LIST_ISSUE_FORMAT = """
+-----------------------------------+---------------------+
| Model Name                        | Last Modified       |
+-----------------------------------+---------------------+
| models/mixtral-8x7b-instruct-v0-1 | 2024-08-09 13:28:24 |
| models/granite-7b-redhat-lab      | 2024-08-09 14:28:40 |
| models/granite-7b-starter         | 2024-08-09 14:40:35 |
+-----------------------------------+---------------------+
""".strip()

ILAB_MODULE_LIST_ERROR = """
Usage: ilab model [OPTIONS] COMMAND [ARGS]...
Try 'ilab model --help' for help.

Error: `/root/.config/instructlab/config.yaml` does not exist or is not a readable file.
Please run `ilab config init` or point to a valid configuration file using `--config=<path>`.
""".strip()

ILAB_MODULE_LIST_EMPTY = ""


def test_ilab_model_list():
    ilab_module_list_info = IlabModuleList(context_wrap(ILAB_MODULE_LIST))
    assert len(ilab_module_list_info) == 4
    assert ilab_module_list_info[0]["model_name"] == "models/prometheus-8x7b-v2-0"
    assert ilab_module_list_info[1]["last_modified"] == "2024-08-09 13:28:24"
    assert ilab_module_list_info[2]["size"] == "12.6 GB"
    assert ilab_module_list_info.models == ["models/prometheus-8x7b-v2-0", "models/mixtral-8x7b-instruct-v0-1", "models/granite-7b-redhat-lab", "models/granite-7b-starter"]

    with pytest.raises(SkipComponent):
        IlabModuleList(context_wrap(ILAB_MODULE_LIST_EMPTY))

    with pytest.raises(ParseException):
        IlabModuleList(context_wrap(ILAB_MODULE_LIST_ERROR))

    with pytest.raises(ParseException):
        IlabModuleList(context_wrap(ILAB_MODULE_LIST_ISSUE_FORMAT))


def test_ilab_doc_examples():
    env = {
        'ilab_model_list_info': IlabModuleList(context_wrap(ILAB_MODULE_LIST))
    }
    failed, total = doctest.testmod(ilab, globs=env)
    assert failed == 0
