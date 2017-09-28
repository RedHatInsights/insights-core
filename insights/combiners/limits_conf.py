"""
Limits configuration
====================

The limits files are normally available to rules as a list of LimitsConf
objects.  This combiner turns those into one set of data, and provides a
``find_all()`` method to search the rules from all the files.
"""

from insights.core.plugins import combiner
from insights.parsers.limits_conf import LimitsConf


@combiner(LimitsConf)
class AllLimitsConf(object):
    """
    Combiner for accessing all the limits configuration files.

    Attributes:
        domains(set): the set of domains found in all data files.
        limits(list): a list of the original LimitsConf parser results.
        rules(list): the entire list of rules.
    """
    def __init__(self, limits):
        rules = []
        domains = set([])
        self.limits = limits
        # Store the tuple of domain, type and item against the row of that
        # limit in our full list of rules.
        rule_tuples_found = {}
        rule_number = 0
        for limits in sorted(limits, key=lambda f: f.file_path):
            # The rule dictionary contains the file_path as a key for later.
            # Make sure that we keep only the last rule for this combination
            # of domain, type and item, according to https://access.redhat.com/solutions/199993
            for rule in limits.rules:
                rule_tuple = (rule['domain'], rule['type'], rule['item'])
                if rule_tuple in rule_tuples_found:
                    row_number = rule_tuples_found[rule_tuple]
                    rules[row_number] = rule
                else:
                    rules.append(rule)
                    rule_tuples_found[rule_tuple] = rule_number
                    rule_number += 1
            # The domains update is much easier :-)
            domains.update(limits.domains)

        self.rules = rules
        self.domains = domains
        super(AllLimitsConf, self).__init__()

    def find_all(self, **kwargs):
        """
        Find all the rules that match the given parameters.  We cheat a bit
        here and combine the results from the find_all() method from the
        original parsers.  Otherwise we'd have to reimplement the _matches
        method from the LimitsConf class.

        Examples:
            >>> data = limits
            >>> results = data.find_all(domain='nproc')
            >>> len(results)
            1
            >>> results[0]['domain']
            'nproc'

        Parameters:
            **kwargs(dict): key-value pairs for the search data.

        Returns:
            (list): a list of the rules matching the given keywords, as
                determined by the ``_matches()`` method in the ``LimitsConf``
                class.
        """
        return [match for data in self.limits for match in data.find_all(**kwargs)]
