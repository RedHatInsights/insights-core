"""
Limits configuration - file ``/etc/security/limits.conf`` and others
====================================================================

The ``LimitsConf`` class parser, which provides a 'rules' list that is
similar to the above but also provides a ``find_all`` method to find all the
rules that match a given set of criteria and other properties that make it
easier to use the contents of the parser.

"""

from .. import Parser, parser, get_active_lines


@parser("limits.conf")
@parser("limits.d")
class LimitsConf(Parser):
    """
    Parse the /etc/security/limits.conf and files in /etc/security/limits.d.

    This parser reads the files and records the domain, type, item and value
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

        for rule in self.rules:
            if all([
               self._matches(param, rule[param], kwargs[param])
               for param in search_params
               ]):
                matched.append(rule)

        return matched
