################
Embedded Content
################

In ``insights-core``, we separate the return of the results from the
rendering of the results.  This separation allows applications using
``insights-core`` to produce output appropriate to their application.
So, for example, the Red Hat Insights product uses an approach that
utilizes several content artifacts (general descriptions, specific
descriptions, ansible playbooks, tagging, etc.) while an internal
diagnostic system has a very simple description and tagging approach.

Because of this separation, the methods that return results
(:py:class:`insights.core.plugins.make_response`,
:py:class:`insights.core.plugins.make_pass`, and
:py:class:`insights.core.plugins.make_fail`) should not provide
formatting themselves.  Instead, keyword arguments (kwargs) are used to
pass back information from the plugin, to be interpolated by the caller.

However, this separation can added unneeded complexity in the case of
creating rules for individual command line use.  For this reason, a
conventional approach using a simple string or dictionary is available
to embed content into the rule code.

``CONTENT`` Attribute
=====================

To embedded content with a rule, create a ``CONTENT`` attribute.  This
attribute can be a string or a dictionary.  When it is a string, it is
interpreted as a `jinja2 <http://jinja.pocoo.org/docs/2.10/>`_ template,
and the kwargs of the ``make_*`` functions are interpolated into it.
This would take place for all rules and all their responses in the
module. If you want to scope content to a particular rule, set
``content=CONTENT`` in the ``@rule`` declaraction.

When the ``CONTENT`` attribute is a dictionary, the keys are interpreted
as "ERROR_KEYS" with strings as values.   The string values are treated
as jinja2 templates with the ``make_*`` kwargs interpolated into the
string whose key matches the key specified as the first argument of the
``make_*`` function.

``make_metadata`` Limitation
============================

A limitation of the ``CONTENT`` attribute occurs when adding embedded
content for the output of the ``make_metadata`` function.  Since this
method does not take an error_key, one must use the string version of
the ``CONTENT`` attribute instead of the dictionary version.   This
effectively means that a rule that uses ``make_metadata`` will need to
be the only rule in the module.

To avoid this limitation, use the ``make_metadata_key`` function
which allows the association of an error_key with the metadata type
response.

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
kwarg (that is, ``current_version.nvr``.) In this case the string acts as a
label, and the pass or fail classification determines if it's an issue or
not.  Putting the above in a file, ``bash_bug.py`` and running on a
systems with a version outside the "bug" range results in

.. code-block:: bash
   :linenos:

    % insights-run -p bash_bug
    ---------
    Progress:
    ---------
    P

    ---------------
    Rules Executed
    ---------------
    bash_bug.check_bash_bug - [PASS]
    -----------------------------------------
    Bash Bug Check: bash-4.4.23-1.fc28


    *******************************
    **** Counts By Return Type ****
    *******************************
    Total Exceptions Reported to Broker - 0
    Total Skipped Due To Rule Dependencies Not Met - 0
    Total Return Type 'make_metadata_key' - 0
    Total Return Type 'make_fail/make_response' - 0
    Total Return Type 'make_pass' - 1
    Total Return Type 'make_metadata' - 0


For a system with the bug, the output would be

.. code-block:: bash
   :linenos:

    % insights-run -p bash_bug
    ---------
    Progress:
    ---------
    R

    ---------------
    Rules Executed
    ---------------
    bash_bug.check_bash_bug - [FAIL]
    -----------------------------------------
    Bash Bug Check: bash-4.4.15-1.fc28


    *******************************
    **** Counts By Return Type ****
    *******************************
    Total Exceptions Reported to Broker - 0
    Total Skipped Due To Rule Dependencies Not Met - 0
    Total Return Type 'make_metadata_key' - 0
    Total Return Type 'make_fail/make_response' - 1
    Total Return Type 'make_pass' - 0
    Total Return Type 'make_metadata' - 0

To make the distinction more explicit, or to return different output in
the case of a pass or a fail, we use a dictionary for
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

With this version, the "pass" use case would generate output such as

.. code-block:: bash
   :linenos:

    % insights-run -p bash_bug
    ---------
    Progress:
    ---------
    P

    ---------------
    Rules Executed
    ---------------
    bash_bug.check_bash_bug - [PASS]
    -----------------------------------------
    Bash bug not found: bash-4.4.23-1.fc28.

    ...

and the fail case would output

.. code-block:: bash
   :linenos:

    % insights-run -p bash_bug
    ---------
    Progress:
    ---------
    R

    ---------------
    Rules Executed
    ---------------
    bash_bug.check_bash_bug - [FAIL]
    -----------------------------------------
    Bash bug found! Version: bash-4.4.15-1.fc28.
    
    ...

