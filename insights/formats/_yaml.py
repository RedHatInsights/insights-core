#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import yaml

from insights.core.evaluators import SingleEvaluator
from insights.formats import EvaluatorFormatterAdapter
from yaml.representer import Representer
from insights.core import ScanMeta

Representer.add_representer(ScanMeta, Representer.represent_name)


class YamlFormat(SingleEvaluator):
    def postprocess(self):
        yaml.dump(self.get_response(), self.stream)


class YamlFormatterAdapter(EvaluatorFormatterAdapter):
    Impl = YamlFormat
