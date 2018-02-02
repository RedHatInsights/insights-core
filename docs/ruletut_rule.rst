Develop Plugin
--------------

Now that we have identified the required parsers, let's get started on
developing our plugin.

Create a file called ``heartburn.py`` in a Python package called ``tutorial``.

.. code-block:: shell

    $ mkdir tutorial
    $ touch tutorial/__init__.py
    $ touch tutorial/heartburn.py

Open ``heartburn.py`` in your text editor of choice and start by stubbing out
the rule function and imports.

.. code-block:: python
   :linenos:

    from insights.parsers.installed_rpms import InstalledRpms
    from insights.parsers.lsof import Lsof
    from insights.parsers.netstat import Netstat
    from insights import rule, make_response

    @rule(InstalledRpms, Lsof, Netstat)
    def heartburn(installed_rpms, lsof, netstat):
        pass

Let's go over each line and describe the details:

.. code-block:: python
   :lineno-start: 1

    from insights.parsers.installed_rpms import InstalledRpms
    from insights.parsers.lsof import Lsof
    from insights.parsers.netstat import Netstat

Parsers you want to use must be imported.  You must pass the parser class
objects directly to the ``@rule`` decorator to declare them as dependencies for
your rule.

.. code-block:: python
   :lineno-start: 4

    from insights import rule, make_response

``rule`` is a function decorator used to specify your main plugin function.
Combiners have a set of optional dependencies that are specified via the
``requires`` kwarg.

``make_response`` is a formatting function used to format
the `return value of a rule </api.html#rule-output>`_ function.

.. code-block:: python
   :lineno-start: 6

    @rule(InstalledRpms, Lsof, Netstat)

Here we are specifying that this rule requires the output of the ``InstalledRpms``,
``Lsof``, and ``Netstat`` parsers.

Now let's add the rule logic

.. code-block:: python
   :linenos:

    @rule(InstalledRpms, Lsof, Netstat)
    def heartburn(installed_rpms, lsof, netstat):

        if 'shared-library-1.0.0' not in installed_rpms:
            return  # not installed, therefore not applicable

        process_list = lsof.using('/usr/lib64/libshared.so.1')

        listening = netstat.listening

        # get the set of processes that are using the library and listening
        vulnerable_processes = set(process_list) && set(listening)

        if vulnerable_processes:
            return make_response("YOU_HAVE_HEARTBURN",
                                 listening_pids=vulnerable_processes)

There's a lot going on here, so lets look at some of the steps in detail.

.. code-block:: python
   :lineno-start: 4

    if 'shared-library-1.0.0' not in installed_rpms:
        return  # not installed, therefore not applicable

The ``InstalledRpms`` parser defines a ``__contains__`` method that allows for simple
searching of rpms by name.

.. code-block:: python
   :lineno-start: 7

    process_list = lsof.using('/usr/lib64/libshared.so.1')

The ``Lsof`` parser provides a ``using`` method that will return a list of pid
numbers that have the given file open.

.. code-block:: python
   :lineno-start: 8

    listening = netstat.listening

The ``Netstat`` parser provides a ``listening`` property that returns a list of
all pid numbers that are bound to a non-internal address.

.. code-block:: python
   :lineno-start: 13

    if vulnerable_processes:
        return make_response("YOU_HAVE_HEARTBURN",
                             listening_pids=vulnerable_processes)

Here we are checking to see if there were any processes that were using the
library and might be bound to an external address.  If any such processes were
found we are returning a result with the error key of ``YOU_HAVE_HEARTBURN``.
This error key can be referenced by other systems for display or tracking
purposes.
