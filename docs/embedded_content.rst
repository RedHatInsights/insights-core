################
Embedded Content
################

In ``insights-core``, we separate the return of the results from the rendering of
the results.  This separation allows applications using ``insights-core``
to produce output appropriate to their application.  So, for example,
the Red Hat Insights product uses an approach that utilizes several
content artifacts (general descriptions, specific descriptions, ansible
playbooks, tagging, etc.) while an internal diagnostic system has a very
simple description and tagging approach.

Because of this separation, the methods that return results
(``make_response``, ``make_pass``, and ``make_fail``) should not provide
formatting themselves.  Instead, keyword arguments (kwargs) are used to
pass back information from the plugin, to be interpolated by the caller.

However, in the case of creating rules for individual use, structuring
the data returned by the command line invocation of insights-core, the
separation can add unneeded complexity.  For this reason, a conventional
approach using a simple string or dictionary has been created.

``CONTENT`` Attribute
=====================

To embedded content with a rule, create a ``CONTENT`` attribute.  This
attribute can be a string or a dictionary.  When it is a string, it is
interpreted as a jinja2 string.  The kwargs of the ``make_*`` functions
are interpolated into the string.   This would take place for all rules
and all their responses in the module.

When the ``CONTENT`` attribute is a dictionary, the keys are interpreted
as "ERROR_KEYS" with strings as values.   The string values are treated
as jinja2 templates with the ``make_*`` kwargs interpolated into the
string whose key matches the key specified as the first argument of the
``make_*`` function.

Optional Dependencies
=====================

To use the ``CONTENT`` formatting feature, you will need to install the
optional jinja2 module.  In addition, when running insights on the
command line, you may want to install the colorama package for colorized
output. For example, ::

    pip install colorama jinja2

Examples
========

A single string can be used for all results from a file.  That
is, the ``CONTEXT`` attribute is applied without regard to the returned
ERROR_KEY. 

.. code-block:: python
   :linenos:

    from insights import rule, make_pass, make_fail
    from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms

    CONTENT = "Bash Bug Check: {{bash}}"

    @rule(InstalledRpms)
    def check_bash_bug(rpms):
        bug_version = InstalledRpm.from_package('bash-4.4.14-1.any')
        fix_version = InstalledRpm.from_package('bash-4.4.18-1.any')
        current_version = rpms.get_max('bash')
        if bug_version <= current_version < fix_version:
            return make_fail('BASH_BUG_PRESENT', bash=current_version.nvr)
        else:
            return make_pass('BASH_BUG_NOT_PRESENT', bash=current_version.nvr)

The ``CONTENT`` string will be used for both the ``make_fail`` (line 12) and
``make_pass`` (line 14) functions, substituting the value of the ``bash``
kwarg (that is, ``current_version.nvr``.  In this case the string acts as a
label and the pass or fail classification determines if it's an issue or
not.

But, we can be more explicit with the error by using a dictionary for
the ``CONTENT`` attribute.

.. code-block:: python
   :linenos:

    from insights import rule, make_pass, make_fail
    from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms

    CONTENT = {
        "BASH_BUG_PRESENT": "Bash bug found! Version: {{bash}}",
        "BASH_BUG_NOT_PRESENT": "Bash bug not found: {{bash}}."
    }

    @rule(InstalledRpms)
    def check_bash_bug(rpms):
        bug_version = InstalledRpm.from_package('bash-4.4.14-1.any')
        fix_version = InstalledRpm.from_package('bash-4.4.18-1.any')
        current_version = rpms.get_max('bash')
        if bug_version <= current_version < fix_version:
            return make_fail('BASH_BUG_PRESENT', bash=current_version.nvr)
        else:
            return make_pass('BASH_BUG_NOT_PRESENT', bash=current_version.nvr)

In this example, the specific message for each type of response is
returned, keyed by the first argument (the ERROR_KEY) of the ``make_*``
function.
