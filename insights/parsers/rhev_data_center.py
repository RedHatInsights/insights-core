import json
from .. import parser, Parser
from insights.specs import Specs
from . import SkipException


@parser(Specs.rhev_data_center)
class RhevDataCenter(Parser):

    def parse_content(self, content):
        if content:
            self.data = json.loads(content)
        else:
            raise SkipException
