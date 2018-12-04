Develop Plugin
--------------

Now that we have identified the required parsers, let's get started on
developing our plugin.

Create a file called ``corrupt_rpmdb.py`` in a Python package called ``tutorial``.

.. code-block:: shell

    $ mkdir tutorial
    $ touch tutorial/__init__.py
    $ touch tutorial/corrupt_rpmdb.py

Open ``corrupt_rpmdb.py`` in your text editor of choice and start by stubbing out
the rule function and imports.

.. code-block:: python
   :linenos:

    from insights.parsers.installed_rpms import InstalledRpms
    from insights import rule, make_response

    @rule(InstalledRpms)
    def report(installed_rpms):
        pass

Let's go over each line and describe the details:

.. code-block:: python
   :lineno-start: 1

    from insights.parsers.installed_rpms import InstalledRpms

Parsers you want to use must be imported.  You must pass the parser class
objects directly to the ``@rule`` decorator to declare them as dependencies for
your rule.

.. code-block:: python
   :lineno-start: 2

    from insights import rule, make_response

``rule`` is a function decorator used to specify your main plugin function.
Combiners have a set of optional dependencies that are specified via the
``requires`` kwarg.

``make_response`` is a formatting function used to format
the `return value of a rule </api.html#rule-output>`_ function.

.. code-block:: python
   :lineno-start: 4

    @rule(InstalledRpms)

Here we are specifying that this rule requires the output of the
:py:class:`insights.parsers.installed_rpms.InstalledRpms`,

Now let's add the rule logic

.. code-block:: python
   :lineno-start: 4


    ERROR_KEY = 'RPMDB_CORRUPT'


    @rule(InstalledRpms)
    def report(rpms):
        if rpms.corrupt:
            for line in rpms.errors:
                if 'rpmdbNextIterator:' in line.split():
                    return make_response(ERROR_KEY, rpmdb_error=line)

There's a lot going on here, so lets look at some of the steps in detail.

.. code-block:: python
   :lineno-start: 6

    if rpms.corrupt:

The ``InstalledRpms`` parser defines a ``corrupt`` method that allows for
simple boolean check to determine if the parser has indicated that the rpm
database is corrupt.

.. code-block:: python
   :lineno-start: 7

    for line in rpms.errors:
        if 'rpmdbNextIterator:' in line.split():
            return make_response(ERROR_KEY, rpmdb_error=line)

Here we iterate through the returned lines searching for line that contained
the `rpmdbNextIterator:` indicating the corruption. If the line is found it is
returned in the response along with the error_key.
This error key can be referenced by other systems for display or tracking
purposes.
