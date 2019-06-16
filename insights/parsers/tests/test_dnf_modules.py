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

import doctest
from insights.parsers import dnf_modules
from insights.tests import context_wrap

DNF_MODULES_INPUT = """
[postgresql]
name=postgresql
profiles=client
state=enabled
stream=9.6
[python36]
name=python36
profiles=
state=enabled
stream=3.6
[virt]
name=virt
profiles=
state=enabled
stream=rhel
"""


def test_dnf_modules():
    modules_config = dnf_modules.DnfModules(context_wrap(DNF_MODULES_INPUT))
    assert modules_config is not None
    assert 'postgresql' in modules_config.sections()
    assert 'python36' in modules_config.sections()
    assert 'virt' in modules_config.sections()
    assert 'enabled' == modules_config.get('postgresql', 'state')


def test_dnf_modules_doc_examples():
    failed, total = doctest.testmod(
        dnf_modules,
        globs={'dnf_modules': dnf_modules.DnfModules(context_wrap(DNF_MODULES_INPUT))}
    )
    assert failed == 0
