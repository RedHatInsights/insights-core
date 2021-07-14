=============
Insights Core
=============

Insights Core is a data collection and analysis framework that is built
for extensibility and rapid development.  Included are a set of reusable
components for gathering data in myriad ways and providing a reliable
object model for commonly useful unstructured and semi-structured data.

.. code-block:: python

    >>> from insights import run
    >>> from insights.parsers import installed_rpms as rpm
    >>> lower = rpm.Rpm("bash-4.4.11-1.fc26")
    >>> upper = rpm.Rpm("bash-4.4.22-1.fc26")
    >>> results = run(rpm.Installed)
    >>> rpms = results[rpm.Installed]
    >>> rpms.newest("bash")
    0:bash-4.4.12-7.fc26
    >>> lower <= rpms.newest("bash") < upper
    True

Features
--------

* Over 200 Enterprise Linux data parsers
* Support for Python 2.6+ and 3.3+
* Built in support for local host collection
* Data collection support for several archive formats

Installation
------------

Releases can be installed via pip

.. code-block:: shell

    $ pip install insights-core

Documentation
-------------

There are several resources for digging into the details of how to use ``insights-core``:

- A `detailed walk through of the constructing a rule
  <https://github.com/RedHatInsights/insights-core/blob/master/docs/notebooks/Diagnostic%20Walkthrough.ipynb>`_
- The `insights-core-tutorials project docs <https://insights-core-tutorials.readthedocs.io/en/latest/>`_
  have three tutorials plus instructions on how to setup the tutorial environment

  - `Preparing Your Development Environment
    <https://insights-core-tutorials.readthedocs.io/en/latest/prep_tutorial_env.html>`_
  - `Custom Parser Development
    <https://insights-core-tutorials.readthedocs.io/en/latest/customtut_parsers.html>`_
  - `Custom Combiner Development
    <https://insights-core-tutorials.readthedocs.io/en/latest/combiner_tutorial.html>`_
  - `Rule Development
    <https://insights-core-tutorials.readthedocs.io/en/latest/rule_tutorial_index.html>`_


- The basic architectural principles of ``insights-core`` can be found in
  the `Insights Core
  <https://github.com/RedHatInsights/insights-core/blob/master/docs/notebooks/Insights%20Core%20Tutorial.ipynb>`_ tutorial jupyter notebook
- A simple `stand_alone.py
  <https://github.com/RedHatInsights/insights-core/blob/master/examples/rules/stand_alone.py>`_
  script encapsulates creating all the basic components in a single script
  that can be easily executed locally
- Some `quick-start examples
  <https://github.com/RedHatInsights/insights-core/blob/master/examples>`_
  are provided in the ``examples`` directory. Each subdirectory under examples
  includes a ``README.md`` file that provides a description of the contents
  and usage information.

To Run the Jupyter Notebooks
++++++++++++++++++++++++++++

If you would like to execute the jupyter notebooks locally, you can
install jupyter:

.. code-block:: bash

    pip install jupyter

To start the notebook server:

.. code-block:: bash

    jupyter notebook

This should start a web-server and open a tab on your browser.  From
there, you can navigate to ``docs/notebooks`` and select a notebook of
interest.

Motivation
----------

Almost everyone who deals with diagnostic files and archives such as
sosreports or JBoss server.log files eventually automates the process of
rummaging around inside them. Usually, the automation is comprised of
fairly simple scripts, but as these scripts get reused and shared, their
complexity grows and a more sophisticated design becomes worthwhile.

A general process one might consider is:

#. Collect some unstructured data (e.g. from a command, an archive, a
   directory, directly from a system)

#. Convert the unstructured data into objects with standard APIs.

#. Optionally combine some of the objects to provide a higher level
   interface than they provide individually (maybe all the networking
   components go together to provide a high level API, or maybe multiple
   individual objects provide the same information. Maybe the same
   information can be gotten from multiple sources, not all of which are
   available at the same time from a given system or archive).

#. Use the data model above at any granularity to write rules that
   formalize support knowledge, persisters that build database tables,
   metadata components that extract contextual info for other systems,
   and more.

Insights Core provides this functionality. It is an extensible framework
for collecting and analyzing data on systems, from archives,
directories, etc. in a standard way.

Insights Core versus Red Hat Insights
-------------------------------------

A common confusion about this project is how it relates to `Red Hat
Insights <https://access.redhat.com/insights/>`_.  Red Hat Insights is a
product produced by `Red Hat <https://www.redhat.com>`_ for automated
discovery and remediation of issues in Red Hat products.  The
``insights-core`` project is used by Red Hat Insights, but only represents
the data collection and rule analysis infrastructure.  This
infrastructure is meant to be reusable by other projects.

So, ``insights-core`` can be used for individuals wanting to perform
analysis locally, or integrated into other diagnostics systems.  Parsers
or rules written using ``insights-core`` can be executed in Red Hat
Insights, but, it is not a requirement.
