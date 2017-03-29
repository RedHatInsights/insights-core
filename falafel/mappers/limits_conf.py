"""
Limits configuration - file ``/etc/security/limits.conf`` and others
====================================================================

There are two mappers here:

get_limits
----------

The ``get_limits`` function mapper simply returns a dictionary with the
domain, type, item and value of each row found in the file, indexed in the
dictionary by the file name.

LimitsConf
----------

The ``LimitsConf`` class mapper, which provides a 'rules' list that is
similar to the above but also provides a ``find_all`` method to find all the
rules that match a given set of criteria and other properties that make it
easier to use the contents of the mapper.

"""

import os
from .. import Mapper, mapper, get_active_lines


def parse_line(string):
    domain, type_, item, value = string.split()
    # Special '-1' value for unlimited, also represented as strings
    if value == 'unlimited' or value == 'infinity':
        value = -1
    else:
        value = int(value)
    return {
        "domain": domain,
        "type": type_,
        "item": item,
        "value": value
    }


@mapper("limits.conf")
@mapper("limits.d")
def get_limits(context):
    """
    Returns a dictionary with one item, keyed to the file name, which is a
    list of dictionaries corresponding to each rule in the file in order.
    The dictionaries in this list have the keys 'domain', 'type', 'item'
    and 'value' as the four fields of each rule.

    Sample input::

        # Default limit for number of user's processes to prevent
        # accidental fork bombs.
        # See rhbz #432903 for reasoning.

        *          soft    nproc     4096
        root       soft    nproc     unlimited

    Examples:

        >>> lfile = shared[get_limits][0] # per file list
        >>> type(lfile)
        <type: dict>
        >>> lfile.keys()
        '/etc/security/limits.d/20-nproc.conf'
        >>> limits = lfile.values()
        >>> type(limits)
        <type: list>
        >>> limits[0] # Note value is integer
        {'domain': '*', 'type': 'soft', 'item': 'nproc', 'value': 4096}
    """
    result = {}
    cfg_file = os.path.basename(context.path)
    if cfg_file.strip():
        lines = []
        for line in get_active_lines(context.content):
            parsed = parse_line(line)
            lines.append(parsed)
        result[cfg_file] = lines
        return result


@mapper("limits.conf")
@mapper("limits.d")
class LimitsConf(Mapper):
    """
    Parse the /etc/security/limits.conf and files in /etc/security/limits.d.

    This mapper reads the files and records the domain, type, item and value
    for each line.  This is available as a big list of dictionaries in the
    'items' property. Each item also contains the 'file' key, which denotes
    the file that this rule was read from.

    There are several convenience methods available to make it easier to find
    specific rules:

    * ``find_all`` finds all the rules that match a given set of conditions
      that are given as parameters.  For example, ``find_all(domain='root')``
      will find all rules that apply to root (including wildcard rules).
      These rules are sorted by domain, type and item, and the most specific
      rule is used.
    * ``domains`` lists all the domains found, in alphabetical order.

    Sample input::

        # Default limit for number of user's processes to prevent
        # accidental fork bombs.
        # See rhbz #432903 for reasoning.

        *          soft    nproc     4096
        root       soft    nproc     unlimited

    Examples:

        >>> limits = shared[LimitsConf][0] # At the moment this is per filename
        >>> len(limits.rules)
        2
        >>> limits.domains
        ['*', 'root']
        >>> limits.rules[0] # note value is integer
        {'domain': '*', 'type': 'soft', 'item': 'nproc', 'value': 4096, 'file': '/etc/security/limits.d/20-nproc.conf'}
        >>> limits.find_all(domain='root')
        [{'domain': '*', 'type': 'soft', 'item': 'nproc', 'value': 4096, 'file': '/etc/security/limits.d/20-nproc.conf'},
         {'domain': 'root', 'type': 'soft', 'item': 'nproc', 'value': 4096, 'file': '/etc/security/limits.d/20-nproc.conf'}]
        >>> limits.find_all(item='data')
        []
    """

    def parse_content(self, content):
        # The intent is for this parser to run across all files, and record
        # the file given for each rule found.  But at the moment an object
        # is created for each single file and the objects have no way of
        # knowing about eachother.  Maybe a
        domains = []
        rules = []
        for line in get_active_lines(content):
            linelist = line.split(None)
            if len(linelist) != 4:
                continue
            domain, typ, item, value = (linelist)
            if value == 'unlimited' or value == 'infinity':
                value = -1
            else:
                value = int(value)
            rules.append({
                'domain': domain,
                'type': typ,
                'item': item,
                'value': value,
                'file': self.file_path,
            })
            if domain not in domains:
                domains.append(domain)

        self.rules = rules
        self.domains = sorted(domains)

    def _matches(self, param, ruleval, argval):
        """
        Test that a single rule value matches the given value for a given
        parameter.
        """
        if ruleval == argval:
            return True

        if param == 'domain':
            # Domains are special:
            # * Usernames are given exactly
            # * Group names are prefixed by @ and given exactly, argval must
            #   also start with @ and is therefore an exact match as above.
            # * Wildcards match everything:
            if ruleval == '*':
                return True
            # UID ranges - must be an integer argument:
            if (not ruleval.startswith('@')) and ':' in ruleval and \
             isinstance(argval, int):
                low, high = ruleval.split(':')
                # :max matches exactly
                if not low and int(high) == argval:
                    return True
                # min: matches everything not less than min
                if not high and int(low) <= argval:
                    return True
                # else match in range
                if low and high and (int(low) <= argval <= int(high)):
                    return True
            # GID ranges - argval must be a string starting with '@' and
            # all numbers.
            if ruleval.startswith('@') and ':' in ruleval[1:] and \
             isinstance(argval, str) and \
             argval.startswith('@') and argval[1:].isdigit():
                low, high = ruleval[1:].split(':')
                gid = int(argval[1:])
                # :max matches exactly
                if not low and int(high) == gid:
                    return True
                # min: matches everything not less than min
                if not high and int(low) <= gid:
                    return True
                # else match in range
                if low and high and (int(low) <= gid <= int(high)):
                    return True
            # * We ignore % maxlogin limits here.

        # From the man page: "Note, if you specify a type of '-' but neglect
        # to supply the item and value fields then the module will never
        # enforce any limits on the specified user/group etc."
        if param == 'type' and ruleval == '-':
            return True

        return False

    def find_all(self, **kwargs):
        """
        Find all the rules that match the given parameters.

        The three parameters that can be searched for are 'domain', 'type'
        and 'item'.  These are used as argument names in the keyword argument
        list.  If no parameters are given, no matches are returned.
        """
        matched = []
        # Only work with the list of parameters that are actually specified -
        # this allows us to give other parameters in the future to control
        # the search.
        search_params = [p for p in ['domain', 'type', 'item'] if p in kwargs]
        # If we didn't get a valid list of parameters, then don't do any work
        if not search_params:
            return matched

        params_to_match = len(search_params)
        for rule in self.rules:
            # Count up the matched parameters and append if they all match.
            param_matches = 0
            for param in search_params:
                if self._matches(param, rule[param], kwargs[param]):
                    param_matches += 1
            if param_matches == params_to_match:
                matched.append(rule)

        return matched
