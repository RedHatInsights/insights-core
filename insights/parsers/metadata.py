import yaml

from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.metadata_json)
class MetadataJson(Parser):
    def parse_content(self, content):
        self.data = yaml.safe_load(content)
