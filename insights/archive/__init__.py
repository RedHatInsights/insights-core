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

import sys
from insights.core.dr import load_components


def get_archives(module_name, system_filter):
    load_components(module_name)
    m = sys.modules[module_name]
    for sub_m in m.__all__:
        demo_submodule = sys.modules[".".join([module_name, sub_m])]
        if hasattr(demo_submodule, "demo"):
            for a in demo_submodule.demo:
                if system_filter in a.name:
                    yield a
