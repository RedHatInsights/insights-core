Develop Tests
=============

Start out by creating a ``test_is_fedora.py`` module in a ``tests`` package.

.. code-block:: shell

    $ mkdir tutorial/tests
    $ touch tutorial/tests/__init__.py
    $ touch tutorial/tests/test_is_fedora.py

Open ``test_is_fedora.py`` in your text editor of choice and start by stubbing
out a test and the required imports.

.. code-block:: python
   :linenos:

    from .. import is_fedora
    from insights.specs import Specs
    from insights.tests import InputData, archive_provider
    from insights.core.plugins import make_response


    @archive_provider(is_fedora.report)
    def integration_test():
        pass

The framework provides an integration test framework that allows you to define
an ``InputData`` object filled with raw examples of files required by your rule
and an expected response.  The object is evaluated by the pipeline as it would
be in a production context, after which the response is compared to your
expected output.

The ``@archive_provider`` decorator registers your test function with the
framework.  This function must be a generator that yields ``InputData`` and an
expected response in a two tuple.  The ``@archive_provider`` decorator takes
one parameter, the rule function to test.

The bulk of the work in building a test for a rule is in defining the
``InputData`` object.  If you remember our rule we accept ``RedhatRelease``.
We will define a data snippet for each test.

.. code-block:: python

    FEDORA = "Fedora release 28 (Twenty Eight)".strip()
    RHEL = "Red Hat Enterprise Linux Server release 7.4 (Maipo)".strip()

Next for each test we need to build ``InputData`` objects and populate it with the content
and build the expected return. Then finally we need to yield the pair.

.. code-block:: python
   :lineno-start: 15

    input_data = InputData("test_fedora")
    input_data.add(Specs.redhat_release, FEDORA)
    expected = make_response("IS_FEDORA", product="Fedora")

    yield input_data, expected

    input_data = InputData("test_rhel")
    input_data.add(Specs.redhat_release, RHEL)
    expected = make_response("IS_NOT_FEDORA", product="Red Hat Enterprise Linux Server")

    yield input_data, expected


Now for the entire test:

.. code-block:: python
    :linenos:

    from .. import is_fedora
    from insights.specs import Specs
    from insights.tests import InputData, archive_provider
    from insights.core.plugins import make_response

    FEDORA = "Fedora release 28 (Twenty Eight)"
    RHEL = "Red Hat Enterprise Linux Server release 7.4 (Maipo)"


    @archive_provider(is_fedora.report)
    def integration_test():

        input_data = InputData("test_fedora")
        input_data.add(Specs.redhat_release, FEDORA)
        expected = make_response("IS_FEDORA", product="Fedora")

        yield input_data, expected

        input_data = InputData("test_rhel")
        input_data.add(Specs.redhat_release, RHEL)
        expected = make_response("IS_NOT_FEDORA", product="Red Hat Enterprise Linux Server")

        yield input_data, expected



