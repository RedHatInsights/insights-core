################
Embedded Content
################

``insights-core`` separates the return of results from their rendering.
This separation allows applications using ``insights-core`` to produce
output appropriate to the application.  So, for example, the Red Hat
Insights product utilizes several content artifacts (general
descriptions, specific descriptions, resolutions, etc.) while an
internal diagnostic system may have a single description.  Each
application may also use different rendering or templating systems for
their UI layer.  Finally, internationalization of responses may be
required.

Because of this separation, the methods that return results
(:py:class:`insights.core.plugins.make_pass` and
:py:class:`insights.core.plugins.make_fail`) should not provide
formatting themselves.  Instead, keyword arguments (kwargs) are used to
pass information from the plugin to the caller for interpretation.

However, this separation adds unneeded complexity in the case of
creating rules for individual, command line use.  For this use-case, a
conventional approach using a simple string or dictionary is available
to embed content into the rule code.

``CONTENT`` Attribute
=====================

To embed content within a rule, create a ``CONTENT`` attribute on the
rule module.  This attribute can be a string or a dictionary.

``CONTENT`` as a String
-----------------------

When ``CONTENT`` is a string, it is interpreted as a `jinja2
<http://jinja.pocoo.org/docs/2.10/>`_ template, and the kwargs of the
``make_*`` functions are interpolated into it.  This would take place
for all responses in the module. If you want to scope content to a
particular rule, set the ``content`` named argument in the ``@rule``
declaration to the desired jinja2 string.

``CONTENT`` as a Dictionary
---------------------------

When ``CONTENT`` is a dictionary, there are three possible ways to
specify template strings with results.  A template can be associated with
an *error_key* (the first argument of the ``make_pass`` or ``make_fail``
functions,) or with the ``make_pass`` and ``make_fail`` commands
themselves, or both.

Dictionary keys which are references to ``make_pass`` or ``make_fail``
can be used to specify jinja2 template strings.  These would apply to
any ``make_*`` results in the module.

.. code-block:: python

    CONTENT = {
            make_pass: "Good bash version: {{bash}}",
            make_fail: "Bad bash version: {{bash}}"
    }

Alternatively, one can use the error_key returned by the respective
``make_*`` functions to specify a jinja2 template string.

.. code-block:: python

    CONTENT = {
         ERROR_KEY_GOOD_BASH: "Good bash version: {{bash}}",
         ERROR_KEY_BAD_BASH: "Bad bash version: {{bash}}"
    }

Finally, one can use the error_key to specify a ``make_*`` set of jinja2
strings through an inner dictionary.

.. code-block:: python

    CONTENT = {
        ERROR_KEY_BASH: {
                make_pass: "Good bash version: {{bash}}",
                make_fail: "Bad bash version: {{bash}}"
        }
        ERROR_KEY_TUNED: {
                make_pass: "Good tuned version: {{tuned}}",
                make_fail: "Bad tuned version: {{tuned}}"
        }
    }

This allows one to use a single error_key with a pass/fail pair.

The Examples section provides additional examples of each type of
``CONTENT`` usage.

``make_metadata`` Limitation
============================

A limitation of the ``CONTENT`` attribute occurs when adding embedded
content for the output of the ``make_metadata`` function.  Since this
method does not take an error_key, one must use the string version of
the ``CONTENT`` attribute instead of the dictionary version.

In the case that you need multiple format strings in the module, you can
use the ``content`` argument on the ``@rule`` decorator to specify the
specific formatting for the rule.

Optional Dependencies
=====================

To use the ``CONTENT`` formatting feature, you will need to install the
optional jinja2 module.  In addition, when running insights on the
command line, you may want to install the colorama package for colorized
output. For example, ::

    pip install colorama jinja2

Examples
========

A single string can be used for all results from a file.  That is, the
``CONTENT`` attribute is applied without regard to the returned ERROR_KEY. 

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
            return make_fail('BASH_BUG', bash=current_version.nvr)
        else:
            return make_pass('BASH_BUG', bash=current_version.nvr)

The ``CONTENT`` string will be used for both the ``make_fail`` (line 12)
and ``make_pass`` (line 14) classes, substituting the value of the
``bash`` kwarg (that is, ``current_version.nvr``.) In this case the
string acts as a label, and the fail or pass classification indicates if
the version an issue or not.  Putting the above in a file,
``bash_bug.py`` and running on a system with a version outside the "bug"
range results in

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

    ...

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

    ...

To make the distinction more explicit, or to return different output in the case
of a pass or a fail, we use a dictionary for the ``CONTENT`` attribute.

.. code-block:: python
   :linenos:

    from insights import rule, make_pass, make_fail
    from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms

    CONTENT = {
        make_fail: "Bash bug found! Version: {{bash}}",
        make_pass: "Bash bug not found: {{bash}}."
    }

    @rule(InstalledRpms)
    def check_bash_bug(rpms):
        bug_version = InstalledRpm.from_package('bash-4.4.14-1.any')
        fix_version = InstalledRpm.from_package('bash-4.4.18-1.any')
        current_version = rpms.get_max('bash')
        if bug_version <= current_version < fix_version:
            return make_fail('BASH_BUG', bash=current_version.nvr)
        else:
            return make_pass('BASH_BUG', bash=current_version.nvr)

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

If you had multiple error keys and needed to distinguish between the content for
them, instead of using the response classes as the ``CONTENT`` keys, you would
use the error key values. If you needed to distinguish between the pass and
failure states of a single key, use a dictionary with the response class as the
keys.

.. code-block:: python
   :linenos:

    from insights import rule, make_pass, make_fail
    from insights.parsers.installed_rpms import InstalledRpm, InstalledRpms

    CONTENT = {
        # for any response with error key of 'SUPER_BASH_BUG'
        'SUPER_BASH_BUG': "Super Bash bug found! Version: {{bash}}",

        # distinguish between the response types of the 'BASH_BUG' error key.
        'BASH_BUG': {
            make_fail:"Bash bug found! Version: {{bash}}",
            make_pass: "Bash bug not found! Version: {{bash}}"
        }
    }

    @rule(InstalledRpms)
    def check_bash_bug(rpms):
        super_bug_version = InstalledRpm.from_package('bash-4.4.12-1.any')
        bug_version = InstalledRpm.from_package('bash-4.4.14-1.any')
        fix_version = InstalledRpm.from_package('bash-4.4.18-1.any')
        current_version = rpms.get_max('bash')
        if super_bug_version == current_version:
            return make_fail('SUPER_BASH_BUG', bash=current_version.nvr)

        if bug_version <= current_version < fix_version:
            return make_fail('BASH_BUG', bash=current_version.nvr)
        else:
            return make_pass('BASH_BUG', bash=current_version.nvr)
