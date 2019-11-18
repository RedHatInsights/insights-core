from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.tags)
class Tags(JSONParser):
    """ Class for parsing the content of ``tags.json``."""
    pass
