"""
Bash Version
============

This is a simple rule and can be run against the local host
using the following command::

$ insights-run -p examples.rules.bash_version

or from the examples/rules directory::

$ python sample_rules.py
"""
from insights.core.plugins import make_info, rule
from insights.parsers.installed_rpms import InstalledRpms

KEY = "BASH_VERSION"

CONTENT = "Bash RPM Version: {{ bash_version }}"


@rule(InstalledRpms)
def report(rpms):
    bash = rpms.get_max('bash')
    return make_info(KEY, bash_version=bash.nvra)
