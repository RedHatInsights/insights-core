Develop Plugin
--------------

Now that we have identified the required parsers, let's get started on
developing our plugin.

Create a file called ``heartburn.py`` in a python package called ``tutorial``.

.. code-block:: shell

    $ mkdir tutorial
    $ touch tutorial/__init__.py
    $ touch tutorial/heartburn.py

Open ``heartburn.py`` in your text editor of choice and start by stubbing out
the rule function and imports.

.. code-block:: python
   :linenos:

    from insights.parsers import rpm, lsof, netstat
    from insights.core.plugins import rule, make_response

    @rule(requires=[rpm, lsof, netstat])
    def heartburn(local, shared):
        pass

Let's go over each line and describe the details:

.. code-block:: python
   :lineno-start: 1

    from insights.parsers import rpm, lsof, netstat

Parsers you want to use must be imported.  There are two main uses:

1. specifying dependencies in the ``@rule``
2. referencing the output of the parser in the ``shared`` context.

.. code-block:: python
   :lineno-start: 2

    from insights.core.plugins import rule, make_response

``rule`` is a function decorator used to specify your main plugin function.
Combiners have a set of optional dependencies that are specified via the
``requires`` kwarg.

``make_response`` is a formatting function used to format
the `return value of a rule </api.html#rule-output>`_ function. 

.. code-block:: python
   :lineno-start: 4

    @rule(requires=[rpm, lsof, netstat])

Here we are specifying that this rule requires the output of the ``rpm``,
``lsof``, and ``netstat`` parsers.

Now let's add the rule logic

.. code-block:: python
   :linenos:

    @rule(requires=[rpm, lsof, netstat])
    def heartburn(local, shared):
 
        if 'shared-library-1.0.0' not in shared[rpm]:
            return  # not installed, therefore not applicable

        process_list = shared[lsof].using('/usr/lib64/libshared.so.1')
        listening = shared[netstat].listening

        # get the set of processes that are using the library and listening
        vulnerable_processes = set(process_list) && set(listening)

        if vulnerable_processes:
            return make_response("YOU_HAVE_HEARTBURN",
                                 listening_pids=vulnerable_processes)

There's a lot going on here, so lets look at some of the steps in detail.

.. code-block:: python
   :lineno-start: 4

    if 'shared-library-1.0.0' not in shared[rpm]:
        return  # not installed, therefore not applicable

The ``rpm`` parser defines a ``__contains__`` method that allows for simple
searching of rpms by name. 

.. code-block:: python
   :lineno-start: 7

    process_list = shared[lsof].using('/usr/lib64/libshared.so.1')

The ``lsof`` parser provides a ``using`` method that will return a list of pid
numbers that have the given file open.

.. code-block:: python
   :lineno-start: 8

    listening = shared[netstat].listening

The ``netstat`` parser provides a ``listening`` property that returns a list of
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
