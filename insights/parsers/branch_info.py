import yaml

from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.branch_info)
class BranchInfo(Parser):
    def parse_content(self, content):
        self.data = yaml.safe_load(content)
