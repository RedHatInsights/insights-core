# Copyright (c) 2014 Fatih Erikli
# The MIT License (MIT)
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""  A class that parses nginx configuration with pyparsing """


import string
import copy
from insights.contrib.pyparsing import (
    Literal, White, Word, alphanums, CharsNotIn, Combine, Forward, Group,
    Optional, OneOrMore, ZeroOrMore, Regex, stringEnd, restOfLine)


def create_parser():
    # constants
    space = Optional(White())
    nonspace = Regex(r"\S+")
    left_bracket = Literal("{").suppress()
    right_bracket = space.leaveWhitespace() + Literal("}").suppress()
    semicolon = Literal(";").suppress()
    key = Word(alphanums + "_/+-.")
    dollar_var = Combine(Literal('$') + Regex(r"[^\{\};,\s]+"))
    condition = Regex(r"\(.+\)")
    # Matches anything that is not a special character, and ${SHELL_VARS}, AND
    # any chars in single or double quotes
    # All of these COULD be upgraded to something like
    # https://stackoverflow.com/a/16130746
    dquoted = Regex(r'(\".*\")')
    squoted = Regex(r"(\'.*\')")
    nonspecial = Regex(r"[^\{\};,]")
    varsub = Regex(r"(\$\{\w+\})")
    # nonspecial nibbles one character at a time, but the other objects take
    # precedence.  We use ZeroOrMore to allow entries like "break ;" to be
    # parsed as assignments
    value = Combine(ZeroOrMore(dquoted | squoted | varsub | nonspecial))

    location = CharsNotIn("{};," + string.whitespace)
    # modifier for location uri [ = | ~ | ~* | ^~ ]
    modifier = Literal("=") | Literal("~*") | Literal("~") | Literal("^~")

    # rules
    comment = space + Literal('#') + restOfLine

    assignment = space + key + Optional(space + value, default=None) + semicolon
    location_statement = space + Optional(modifier) + Optional(space + location + space)
    if_statement = space + Literal("if") + space + condition + space
    charset_map_statement = space + Literal("charset_map") + space + value + space + value

    map_statement = space + Literal("map") + space + nonspace + space + dollar_var + space
    # This is NOT an accurate way to parse nginx map entries; it's almost
    # certainly too permissive and may be wrong in other ways, but it should
    # preserve things correctly in mmmmost or all cases.
    #
    #    - I can neither prove nor disprove that it is correct wrt all escaped
    #      semicolon situations
    # Addresses https://github.com/fatiherikli/nginxparser/issues/19
    map_pattern = Regex(r'".*"') | Regex(r"'.*'") | nonspace
    map_entry = space + map_pattern + space + value + space + semicolon
    map_block = Group(
        Group(map_statement).leaveWhitespace() +
        left_bracket +
        Group(ZeroOrMore(Group(comment | map_entry)) + space).leaveWhitespace() +
        right_bracket)

    block = Forward()

    # key could for instance be "server" or "http", or "location" (in which case
    # location_statement needs to have a non-empty location)

    block_begin = (Group(space + key + location_statement) ^
                   Group(if_statement) ^
                   Group(charset_map_statement)).leaveWhitespace()

    block_innards = Group(ZeroOrMore(Group(comment | assignment) | block | map_block) + space).leaveWhitespace()

    block << Group(block_begin + left_bracket + block_innards + right_bracket)

    script = OneOrMore(Group(comment | assignment) ^ block ^ map_block) + space + stringEnd
    return script.parseWithTabs().leaveWhitespace()


class UnspacedList(list):
    """After handling by create_parser(), there is white space existing in the list. Use this class to wrap a list
     [of lists], making any whitespace entries magically invisible"""

    def __init__(self, list_source):
        # ensure our argument is not a generator, and duplicate any sublists
        self.spaced = copy.deepcopy(list(list_source))
        self.dirty = False

        # Turn self into a version of the source list that has spaces removed
        # and all sub-lists also UnspacedList()ed
        list.__init__(self, list_source)
        for i, entry in reversed(list(enumerate(self))):
            if isinstance(entry, list):
                sublist = UnspacedList(entry)
                list.__setitem__(self, i, sublist)
                self.spaced[i] = sublist.spaced
            elif self._spacey(entry):
                list.__delitem__(self, i)

    def _spacey(self, x):
        return (isinstance(x, str) and x.isspace()) or x == ''
