from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.tags)
class BranchInfo(JSONParser):
    """ Class for parsing the content of ``branch_info``."""
    pass
