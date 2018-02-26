=============
Insights Core QE TESTING
=============

https://access.redhat.com/insights/

**insights-core** is the framework, common components, and utilities for
Insights rules.

To get the project set up::

    virtualenv .
    source bin/activate
    pip install -e .[develop]

To run the tests::

    py.test

To generate docs::

    cd docs/
    make html

And they can be found under `docs/_build/html`.

Configuration
-------------

Insights Core also houses the centralized configuration module for the Insights
Engine and Insights Content Server.  This is to enable each project to use the
same file(s) and code module for configuration.  insights-core checks several
locations for the configuration file, in this order:

- `$INSIGHTS_CORE/insights/defaults.yaml`
- `/etc/insights.yaml`
- `$HOME/.local/insights.yaml`
- `$PWD/.insights.yaml`

Options from files read later will override options from files read earlier.

To see the layout of the file and the available options, please take a look at
`defaults.yaml <insights/defaults.yaml>`_ in this repo.
