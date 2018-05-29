from insights.core import YAMLParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.branch_info)
class BranchInfo(YAMLParser):
    """ Class for parsing the content of ``branch_info``."""
    pass
