"""
Ilab parsers
============

Parsers provided by this module include:

IlabModuleList - command ``/usr/bin/ilab model list``
-----------------------------------------------------
IlabConfigShow - command ``/usr/bin/ilab config show``
------------------------------------------------------
"""

from insights.core import CommandParser, YAMLParser
from insights.core.plugins import parser
from insights.core.exceptions import SkipComponent, ParseException
from insights.specs import Specs


@parser(Specs.ilab_model_list)
class IlabModuleList(CommandParser, list):
    """
    This parser will parse the output of "/usr/bin/ilab model list".

    Sample output from ``/usr/bin/ilab model list``::

        +-----------------------------------+---------------------+---------+
        | Model Name                        | Last Modified       | Size    |
        +-----------------------------------+---------------------+---------+
        | models/prometheus-8x7b-v2-0       | 2024-08-09 13:28:50 |  87.0 GB|
        | models/mixtral-8x7b-instruct-v0-1 | 2024-08-09 13:28:24 |  87.0 GB|
        | models/granite-7b-redhat-lab      | 2024-08-09 14:28:40 |  12.6 GB|
        | models/granite-7b-starter         | 2024-08-09 14:40:35 |  12.6 GB|
        +-----------------------------------+---------------------+---------+

    Examples:
        >>> type(ilab_model_list_info)
        <class 'insights.parsers.ilab.IlabModuleList'>
        >>> ilab_model_list_info[0]["model_name"]
        'prometheus-8x7b-v2-0'

    Attributes:
        models (list): list of model names
        unparsed_lines (list): the not table content lines in command output

    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty content")

        self.unparsed_lines = []
        headings = None
        for _line in content:
            line = _line.strip()
            if line.startswith("|") and line.endswith("|"):
                # a table content line
                linesp = [_.strip() for _ in line.strip('|').split('|')]
                if "Model Name" in line:
                    headings = ['_'.join(h.lower().split()) for h in linesp]
                elif headings and len(linesp) == len(headings):
                    parsed_row = dict(zip(headings, linesp))
                    # drop the leading "models/" if present
                    if parsed_row["model_name"].startswith("models/"):
                        parsed_row["model_name"] = parsed_row["model_name"][7:]
                    if not parsed_row["model_name"]:
                        raise ParseException("Unexpected parsed model line: %s" % line)
                    self.append(parsed_row)
                else:
                    raise ParseException("Unparsable table line: %s" % line)

            elif not line.startswith("+--------"):
                self.unparsed_lines.append(_line)

        if not self:
            raise SkipComponent("Empty table after parsing")

        self.models = [m['model_name'] for m in self]


@parser(Specs.ilab_config_show)
class IlabConfigShow(CommandParser, YAMLParser):
    """
    This parser will parse the output of "/usr/bin/ilab config show".

    Sample output from ``/usr/bin/ilab config show``::

        time="2025-04-15T08:23:44Z" level=warning msg="The input device is not a TTY. The --tty and --interactive flags might not work properly"
        # Chat configuration section.
        chat:
          context: default
          logs_dir: /root/.local/share/instructlab/chatlogs
          max_tokens:
          model: /root/.cache/instructlab/models/granite-8b-lab-v1
        evaluate:
          base_branch:
          base_model: /root/.cache/instructlab/models/granite-8b-starter-v1
          mmlu:
            batch_size: auto
            few_shots: 5
        serve:
          backend: vllm
          vllm:
            gpus:
            llm_family: ''
            vllm_args:
            - --tensor-parallel-size
            - '1'

    Examples:
        >>> type(ilab_config_show_info)
        <class 'insights.parsers.ilab.IlabConfigShow'>
        >>> ilab_config_show_info['chat']['logs_dir']
        '/root/.local/share/instructlab/chatlogs'

    Attributes:
        data(dict): The ilab config information
    """

    ignore_lines = ['time=']
