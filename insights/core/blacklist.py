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

import re


_FILE_FILTERS = set()
_COMMAND_FILTERS = set()
_PATTERN_FILTERS = set()
_KEYWORD_FILTERS = set()


def add_file(f):
    _FILE_FILTERS.add(re.compile(f))


def add_command(f):
    _COMMAND_FILTERS.add(re.compile(f))


def add_pattern(f):
    _PATTERN_FILTERS.add(f)


def add_keyword(f):
    _KEYWORD_FILTERS.add(f)


def allow_file(c):
    return not any(f.match(c) for f in _FILE_FILTERS)


def allow_command(c):
    return not any(f.match(c) for f in _COMMAND_FILTERS)


def get_disallowed_patterns():
    return _PATTERN_FILTERS


def get_disallowed_keywords():
    return _KEYWORD_FILTERS
