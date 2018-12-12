Develop Plugin
--------------

Now that we have identified the required parsers, let's get started on
developing our plugin.

Create a file called ``is_fedora.py`` in a Python package called ``tutorial``.

.. code-block:: shell

    $ mkdir tutorial
    $ touch tutorial/__init__.py
    $ touch tutorial/is_fedora.py

Open ``is_fedora.py`` in your text editor of choice and start by stubbing out
the rule function and imports.

.. code-block:: python
   :linenos:

    from insights.parsers.redhat_release import RedhatRelease
    from insights import rule, make_response

    @rule(RedhatRelease)
    def report(rhrel):
        pass

Let's go over each line and describe the details:

.. code-block:: python
   :lineno-start: 1

    from insights.parsers.redhat_release import RedhatRelease

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
   :lineno-start: 6

    CONTENT = {
        "IS_FEDORA": "This machine runs {{product}}.",
        "IS_NOT_FEDORA": "This machine runs {{product}}."
    }

Here we define the ``Jinga`` template for message to be displayed for either
response tag


.. code-block:: python
   :lineno-start: 12

    @rule(RedhatRelease)

Here we are specifying that this rule requires the output of the
:py:class:`insights.parsers.redhat_release.RedhatRelease`,

Now let's add the rule logic

.. code-block:: python
   :lineno-start: 12

    @rule(RedhatRelease, content=CONTENT)
    def report(rhrel):
        """Fires if the machine is running Fedora."""

        if "Fedora" in rel.product:
            return make_response("IS_FEDORA", product=rhrel.product)
        else:
            return make_response("IS_NOT_FEDORA", product=rhrel.product)

Now lets look at what the rule is doing.

The ``RedhatRelease`` parser parses content from the ``/etc/redhat-release`` file on the
host it is running on and returns an object containing the Red Hat OS information for the
host.

.. code-block:: python
   :lineno-start: 16

        if "Fedora" in rhrel.product:
            return make_response("IS_FEDORA", product=rhrel.product)
        else:
            return make_response("IS_NOT_FEDORA", product=rhrel.product)

Here we check to see if the value ``Fedora`` is in the "product" property of the
"rhrel" object. If true then the rule returns a response telling us that the host
is indeed running ``Fedora``, along with the product information returned by the
parser. If false then the rule returns a response telling us that the host is
not running ``Fedora``, along with the product information returned by the parser.
