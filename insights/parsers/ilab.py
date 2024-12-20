"""
Ilab parsers
============

Parsers provided by this module include:

IlabModuleList - command ``/usr/bin/ilab model list``
-----------------------------------------------------
"""
from insights.core import CommandParser
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
        'models/prometheus-8x7b-v2-0'

    Attributes:
        models (list): list of model names

    """
    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty")
        if not content[0].startswith("+-"):
            raise ParseException("Unexpected format: %s" % content[0])
        for line in content:
            if line.startswith("|") and "Model Name" not in line:
                split_items = line.split("|")
                if len(split_items) == 5:
                    self.append(
                        {
                            "model_name": split_items[1].strip(),
                            "last_modified": split_items[2].strip(),
                            "size": split_items[3].strip(),
                        }
                    )
                else:
                    raise ParseException("Unexpected format: %s" % line)
        self.models = [m['model_name'] for m in self]
