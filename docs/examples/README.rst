======================
Insights Core Examples
======================

The files contained in the ``insights/docs/examples`` directory are described
in detail in the tutorials:

* :doc:`../customtut_parsers`
* :doc:`../customtut_rule`
* :doc:`../combiner_tutorial`

The examples directory includes these files::
    
    examples
    ├── combiners
    │   ├── hostname_uh.py
    │   ├── __init__.py
    │   └── tests
    │       ├── __init__.py
    │       └── test_hostname_uh.py
    ├── parsers
    │   ├── __init__.py
    │   ├── secure_shell.py
    │   └── tests
    │       ├── __init__.py
    │       └── test_secure_shell.py
    ├── README.rst
    └── rules
        ├── __init__.py
        ├── sshd_secure.py
        └── tests
            ├── __init__.py
            ├── test_integration.py
            └── test_sshd_secure.py

If you would rather skip straight to running the examples you can always
copy the examples directly into you ``work`` directory. You will need to
have the ``insights-core`` environment set up as described in
:ref:`parser-development-environment`.
You will need to add your newly copied ``examples`` directory path to
``PYTHONPATH``

>$ export PYTHONPATH=<examples path>:$PYTHONPATH

You will also need to make a few changes as described below

Parses
------

Change lines in module ``examples/parsers/tests/test_secure_shell.py`` from:

.. code-block:: python
    :linenos:

    from docs.examples.parsers.secure_shell import SshDConfig
    from docs.examples.parsers import secure_shell

To

.. code-block:: python
    :linenos:

    from examples.parsers.secure_shell import SshDConfig
    from examples.parsers import secure_shell


Combiners
---------

Change line in module ``examples/combiners/tests/test_hostname_uh.py`` from:

.. code-block:: python
    :linenos:

    from docs.examples.combiners.hostname_uh import HostnameUH

To

.. code-block:: python
    :linenos:

    from examples.combiners.hostname_uh import HostnameUH

Rules
-----

Change line in module ``examples/rules/sshd_secure.py`` from:

.. code-block:: python
    :linenos:

    from docs.examples.parsers.secure_shell import SshDConfig

To

.. code-block:: python
    :linenos:

    from examples.parsers.secure_shell import SshDConfig


Change lines in module ``examples/rules/tests/test_sshd_secure.py`` from:

.. code-block:: python
    :linenos:

    from docs.examples.rules import sshd_secure
    from docs.examples.parsers.secure_shell import LocalSpecs

To

.. code-block:: python
    :linenos:

    from examples.rules import sshd_secure
    from examples.parsers.secure_shell import LocalSpecs

