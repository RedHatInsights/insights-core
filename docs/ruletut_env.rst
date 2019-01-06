**************************************
Preparing Your Development Environment
**************************************

The following instructions assume that you have an insights-core development
environment setup and working, and that your rules root dir and insights-core
root dir are subdirs of the same root dir.  First you will need to create
a ``mycomponents`` directory and then copy the example rules directory into
``mycomponents``.  You will also need to copy the ``conftest.py`` from the
``insights-core`` root directory in order for your tests to work correctly.
Here are the commands to setup your rule development environment::

    [userone@hostone work]$ pwd
    /home/userone/work
    [userone@hostone work]$ ls
    insights-core
    [userone@hostone work]$ mkdir mycomponents
    [userone@hostone work]$ cd mycomponents
    [userone@hostone mycomponents]$ cp -R insights-core/docs/examples/rules ./rules
    [userone@hostone mycomponents]$ cp ../insights-core/conftest.py .
    [userone@hostone mycomponents]$ ls
    conftest.py  rules

Once you have completed this your project directory tree should look like this
(note the details of the ``insights-core`` directory tree are not being shown)::

    work
    ├── insights-core
    └── mycomponents
        ├── parsers
        ├── rules
        │   ├── __init__.py
        │   ├── heartburn.py
        │   └── sshd_secure.py
        └── tests
            ├── __init__.py
            ├── test_heartburn.py
            ├── test_integration.py
            └── test_sshd_secure.py

Make sure you start with your virtual environment set to the insights-core
project::

    [userone@hostone mycomponents]$ source ../insights-core/bin/activate
    (insights-core)[userone@hostone mycomponents]$

You are now ready to begin writing your rule.
