from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.tags)
class Tags(JSONParser):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.client_metadata.Tags` instead.

    Class for parsing the content of ``tags.json``."""
    def __init__(self, *args, **kwargs):
        deprecated(
            Tags,
            "Please use insights.parsers.client_metadata.Tags instead.",
            "3.4.0"
        )
        super(Tags, self).__init__(*args, **kwargs)
