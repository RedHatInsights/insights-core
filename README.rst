=============
Insights Core
=============

Almost everyone who deals with diagnostic files and archives such as
sosreports or JBoss server.log files automates the process of rummaging
around inside them. Usually, the automation is fairly simple scripts.
But as these scripts get reused and shared, their complexity grows and a
more sophisticated design becomes worthwhile.

A general process one might consider is

#. Collect some unstructured data (from a command, an archive, a
   directory, directly from a system, etc.)

#. Convert the unstructured data into objects with standard APIs.

#. Optionally combine some of the objects to provide a higher level
   interface than they provide individually (maybe all the networking
   components go together to provide a high level API, or maybe multiple
   individual objects provide the same information. Maybe the same
   information can be gotten from multiple sources, not all of which are
   available at the same time from a given system or archive).

#. Use the data model above at any granularity to write rules that
   formalize KCS articles, persisters that build database tables,
   metadata components that extract contextual info for other systems,
   etc.

Insights Core provides this functionality. It is an extensible framework
for collecting and processing data on systems, from archives,
directories, etc. in a standard way.

Insights Core verses Red Hat Insights
-------------------------------------

A common confusion about this project is how it relates to `Red Hat
Insights <https://access.redhat.com/insights/>`_.  Red Hat Insights is a
product produced by `Red Hat <https://www.redhat.com>`_ for automated
discovery and remediation of issues in Red Hat products.  The
`insights-core` project is used by Red Hat Insights, but only represents
the data collection and rule analysis infrastructure.  This
infrastructure is meant to be reusable by other projects.

So, `insights-core` can be used for individuals wanting to perform
analysis locally, or integrated into other diagnostics systems.  Parsers
or rules written using `insights-core` can be executed in Red Hat
Insights, but, it is not a requirement. 

Getting Started Using `insights-core`
-------------------------------------

The rest of this README will go into how to use `insights-core` to
perform analysis.  That is, it will address users of the framework.
Contributors to `insights-core` are directed to the
`contributor's guide <CONTRIBUTING.md>`_.

A Simple Preview
----------------

Let's start with a simple example that shows the motivation of the
framework.  (This example is covered in a bit more detail in `one of the
jupyter notebook examples
<https://github.com/RedHatInsights/insights-core/blob/master/docs/notebooks/Diagnostic%20Walkthrough.ipynb>`_.)

Suppose that you are trying to detect if a Red Hat Enterprise Linux
system contains a version of `bash` with a particular bug.  The first
approach would be to do something like check the output of the `rpm -qa`
to see what version of `bash` is installed.

::

    rpm -qa | grep bash

This will output any bash packages installed and one can review the Name
Version and Release (NVR) to see if it is the buggy version.  On my box,
the result of the command is::

    bash-completion-2.6-2.fc27.noarch
    bash-4.4.19-1.fc27.x86_64

To further automate this, I would want to parse the lines to insure I
only received the `bash` package, and to compare the version with the
known buggy versions.  That's a bit more work, but certainly something
that could be done.

Let's complicate the example a bit further and assume that the bug was
introduced in `bash-4.4.16-1.fc27` and was fixed in
`bash-4.4.22-1.fc27`.  Now we would need to compare the version in a
range of NVRs making the script quite a bit more complicated.
Especially if we wanted to be able to apply it to other packages in the
future and the parsing of the NVR and version comparison would need to
be generalized.

So, how would we code this using `insights-core`?  The following script
will identify whether the current system has a version of `bash`
installed within the range.

.. code-block:: python

    from insights import rule, make_response, run
    from insights.parsers.installed_rpms import InstalledRpms, InstalledRpm

    lower = InstalledRpm.from_package("bash-4.4.16-1.fc27")
    upper = InstalledRpm.from_package("bash-4.4.22-1.fc27")

    @rule(InstalledRpms)
    def report(rpms):
        rpm = rpms.get_max("bash")
        if rpm and rpm >= lower and rpm < upper:
            return make_response("BASH_AFFECTED", version=rpm.nvr)
        elif rpm:
            return make_response("BASH_UNAFFECTED", version=rpm.nvr)
        else:
            return make_response("NO_BASH_FOUND")

    if __name__ == "__main__":
        run(report, print_summary=True)

To keep this preview simple, we won't unpack everything here, delegating
to the other tutorials and examples for further details.  However, let's
highlight some points to help understand what's going on.

After importing the components we need, we define the bounds of our
version range by creating a `lower` and `upper` `InstalledRpm` version.
Then we define our `rule` which depends upon the `InstalledRpms`
"parser" class.  This class will be passed in as the first argument to
the `report` function.

The `report` function gets the maximum version of `bash` found in
`InstalledRpms` and then compares it to the `upper` and `lower` values.
If a version of `bash` is found between those versions, it returns
`BASH_AFFECTED` and the version it found.  Otherwise, if it finds a
version of `bash` that is outside the range, it returns
`BASH_UNAFFECTED` and the version found.  Finally, if it doesn't find
any version of bash, it returns `NO_BASH_FOUND`.

This is all executed by the `run` command.  The `run` command will
"know" about the `report` function and that it depends upon
`InstalledRpms` based on the `@rule` decorator.  

That's cool, but is it really simpler?
--------------------------------------

Certainly, for a simple check, just grepping a file is simpler.
However, there are gains as the complexity and automation requirements
come into play.  In this particular case, the complexity is hidden in two
places.

First, complexity around parsing the `rpm -qa` command, and presenting
it in a usable data model is handled by the `InstalledRpms` class.  It
is just `one
<http://insights-core.readthedocs.io/en/latest/shared_parsers_catalog/installed_rpms.html#installedrpms-command-rpm-qa>`_
of many `parsers
<http://insights-core.readthedocs.io/en/latest/parsers_index.html#shared-parsers-catalog>`_
and `combiners
<http://insights-core.readthedocs.io/en/latest/combiners_index.html#shared-combiners-catalog>`_
that one can use.   In addition, new custom parsers can be easily
created. (See the `stand_alone.py
<https://github.com/RedHatInsights/insights-core/blob/master/stand_alone.py>`_
script for a full example defining a full set of components.)

The complexity of execution is hidden in the `run` function.  This
function understands the dependences that need to be met, determining
the order of processing.  In addition, it understands various contexts
of execution.  In the above example, a "host" context is used and the
data gathering command is simply executed on the current host.  But,
contexts exist to run the same function over a sosreport, Red Hat
Insights archive, or a directory containing expanded archives.  Finally,
the same code could be run in Red Hat Insights itself.

Next Steps
----------

There are several resources for digging into the details of how to use `insights-core`:

- A more `detailed walk through of the example above
  <https://github.com/RedHatInsights/insights-core/blob/master/docs/notebooks/Diagnostic%20Walkthrough.ipynb>`_
- The `core api docs <http://insights-core.readthedocs.io/en/latest/>`_
  has three tutorials

  - `Rule Using Existing Parsers and Combiners
    <http://insights-core.readthedocs.io/en/latest/rule_tutorial_index.html#tutorial-rule-using-existing-parsers-and-combiners>`_
  - `Custom Parser and Rule
    <http://insights-core.readthedocs.io/en/latest/custom_tutorial_index.html#tutorial-custom-parser-and-rule>`_
  - `Combiner Development
    <http://insights-core.readthedocs.io/en/latest/combiner_tutorial.html#tutorial-combiner-development>`_

- The basic architectural principles of `insights-core` can be found in
  the `Insights Core Tutorial
  <https://github.com/RedHatInsights/insights-core/blob/master/docs/notebooks/Insights%20Core%20Tutorial.ipynb>`_ jupyter notebook
- A simple `stand_alone.py
  <https://github.com/RedHatInsights/insights-core/blob/master/stand_alone.py>`_
  script encapsulates creating all the basic components in a single script
  that can be easily executed locally

Setup
-----

All the examples should run locally on a Red Hat Enterprise Linux or
Fedora system once setup.   `insights-core` has recently been updated to
support both Python 2 and Python 3.  So, we'll provide information on
how to setup both.

Prior to setting up the project ensure that you have Python 2 or 3 (or
both) installed.  For Python 2, you will also need virtualenv installed.
The steps for this will vary depending upon your system.


Python 2
++++++++

To get the project setup for Python 2, use the following commands

.. code-block:: bash

    mkdir .python2
    virtualenv .  # Make sure you're using the python2 runtime
    source .python2/bin/activate
    pip install --upgrade pip
    pip install -e .[develop]


Python 3
++++++++

To setup the project for Python 3, use the following commands

.. code-block:: bash

    mkdir .python3
    python3 venv -m .python3
    source .python3/bin/activate
    pip install --upgrade pip
    pip install -e .[develop]

After setup
++++++++++++

You can validate the setup by running the unit tests::

    py.test

To generate docs:

.. code-block:: bash

    cd docs/
    make html

And they can be found under `docs/_build/html`.

To Run the Jupyter Notebooks
++++++++++++++++++++++++++++

If you would like to execute the jupyter notebooks locally, you can
install jupyter::

    pip install jupyter # be sure your virtual environment is activated.

To start the notebook server::

    jupyter notebook

This should start a web-server and open a tab on your browser.  From
there, you can navigate to docs/notebooks and select a notebook of
interest.

