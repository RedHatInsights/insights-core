###############################
Quickstart Insights Development
###############################

.. contents:: Table of Contents
    :depth: 6

Insights-core is the framework upon which Red Hat Insights rules are built and
delivered.  The basic purpose is to apply "rules" to a set of files collected
from a system at a given point in time.

Insights-core rule "plugins" are written in Python.  The rules follow a
"MapReduce" approach, dividing the logic between "mapping" and
"reducing" methods.  This is a convenient approach where a rule's logic
takes place in two steps.  First, there is a "gathering of facts" (the
map phase) followed by logic being applied to the facts (the reduce
phase).

*************
Prerequisites
*************

All Plugin code is written in Python and all Insights libraries
and framework code necessary for development and execution are
stored in Git repositories.  Before you begin make sure you have
the following installed:

* Python 3 (recommended Python 3.6)
* Git
* Python Virtualenv
* Python PIP

Further requirements can be found in the
`README.rst <https://github.com/RedHatInsights/insights-core/blob/master/README.rst>`_
file associated with the insights-core project.

.. HINT::
   You many also need to install ``gcc`` to be able to build some python modules,
   ``unzip`` to be able to run `pytest` on the ``insights-core`` repo,
   and ``pandoc`` to build Insights Core documentation.

**********************
Rule Development Setup
**********************

In order to develop rules to run in Red Hat Insights you'll need Insights
Core (http://github.com/RedHatInsights/insights-core) as well as your own rules code.
The commands below assume the following sample project directory structure
containing the insights-core project repo and your directory and files
for rule development::

    project_dir
    ├── insights-core
    └── myrules
        ├── hostname_rel.py
        └── bash_version.py


.. _insights_dev_setup:

Insights Core Setup
===================

Clone the project::

    [userone@hostone project_dir]$ git clone git@github.com:RedHatInsights/insights-core.git

Or, alternatively, using HTTPS::

    [userone@hostone project_dir]$ git clone https://github.com/RedHatInsights/insights-core.git

Initialize a virtualenv (depending on your python installation you may need to specify a specific
version of python using the `-p` option and the name or path of the python you want to use.  For
example `-p python3` or `-p /usr/bin/python3.6`)::

    [userone@hostone project_dir]$ cd insights-core
    [userone@hostone project_dir/insights-core]$ virtualenv -p python3.6 .

Verify that you have the desired version of python by enabling the virtualenv::

    [userone@hostone project_dir/insights-core]$ source bin/activate
    (insights-core)[userone@hostone project_dir/insights-core]$ python --version

You can also ensure that your virtualenv is set by checking which python is being used::

    (insights-core)[userone@hostone project_dir/insights-core]$ which python
    project_dir/insights-core/bin/python

Depending upon your environment, your prompt may also indicate you are using a virtualenv.
In the example above it is indicated by *(insights-core)*.

Next install the insights-core project and its dependencies into your virtualenv::

    (insights-core)[userone@hostone project_dir/insights-core]$ bin/pip install -e .[develop]

Now check to make sure your environment is setup correctly by invoking the `insights-run` command.
You should see the help information for insights-run::

    (insights-core)[userone@hostone project_dir/insights-core]$ insights-run --help

When you are finished working on this project you can deactivate your virtualenv using the `deactivate`
command.

.. TIP::
   If you don't plan on digging into the Insights Core code you can skip cloning the ``insights-core``
   repo and follow these steps:

   1. Create a virtualenv in your ``myrules`` directory.
   2. Activate and check your virtualenv as specified above
   3. Install ``insights-core`` using the command `pip install insights-core`
   4. Check insights installation with `insights-run --help`

   If you use this method make sure you periodically update insights core in your virtualenv
   with the command `pip install --upgrade insights-core`.

Rule Development
================

From your project root directory create a directory for your rules::
    
    (insights-core)[userone@hostone project_dir/insights-core]$ cd ..
    (insights-core)[userone@hostone project_dir]$ mkdir myrules
    (insights-core)[userone@hostone project_dir]$ cd myrules
    (insights-core)[userone@hostone project_dir/myrules]$

Create an empty file named ``__init__.py`` that will enable your rules directory
as a python package. This makes the ``myrules`` directory a python package allowing
you to use `insights-run` to run multiple components in the package.
If you create subdirectories create an empty
``__init__.py`` in each subdir that contains any components you want to run.

    (insights-core)[userone@hostone project_dir/myrules]$ touch __init__.py

Create a sample rule called ``hostname_rel.py`` in the ``myrules`` directory:

.. code-block:: python
   :linenos:

   #!/usr/bin/env python
   from insights.core.plugins import make_fail, make_pass, rule
   from insights.parsers.hostname import Hostname
   from insights.parsers.redhat_release import RedhatRelease

   ERROR_KEY_1 = "RELEASE_IS_RHEL"
   ERROR_KEY_2 = "RELEASE_IS_NOT_RECOGNIZED"
   ERROR_KEY_3 = "RELEASE_CANNOT_BE_DETERMINED"

   CONTENT = {
       ERROR_KEY_1: "This release is RHEL\nHostname: {{ hostname }}\nRelease: {{ release }}",
       ERROR_KEY_2: "This release is not RHEL\nHostname: {{ hostname }}\nRelease: {{ release }}",
       ERROR_KEY_3: "This release is not RHEL\nHostname: {{ hostname }}\nRelease: not present"
   }


   @rule(Hostname, [RedhatRelease])
   def report(hostname, release):
       if release and release.is_rhel:
           return make_pass(ERROR_KEY_1,
                            hostname=hostname.fqdn,
                            release=release.version)
       elif release:
           return make_fail(ERROR_KEY_2,
                            hostname=hostname.fqdn,
                            release=release.raw)
       else:
           return make_fail(ERROR_KEY_3, hostname=hostname.fqdn)


   if __name__ == "__main__":
       from insights import run
       run(report, print_summary=True)

.. HINT::
   You can download the
   `code for hostname_rel.py <https://github.com/RedHatInsights/insights-core/blob/master/examples/rules/hostname_rel.py>`_

Now you can use Insights to evaluate your rule by running your rule script::
    
    (insights-core)[userone@hostone project_dir/myrules]$ python hostname_rel.py
    
Depending upon the system you are using you will see several lines of
output ending with a your rule results that should look something like this::

   ---------
   Progress:
   ---------
   F

   --------------
   Rules Executed
   --------------
   [FAIL] __main__.report
   ---------------
   This release is not RHEL
   Hostname: hostone
   Release: Fedora release 29 (Twenty Nine)


   ----------------------
   Rule Execution Summary
   ----------------------
   Missing Deps: 0
   Passed      : 0
   Fingerprint : 0
   Failed      : 1
   Metadata    : 0
   Metadata Key: 0
   Exceptions  : 0

Depending on your system you may also be able to make this file executable (chmod +x hostname_rel.py)
and run like this: `./hostname_rel.py`.

Now create a second rule named ``bash_version.py``` and include the following code

.. code-block:: python
   :linenos:

   from insights.core.plugins import make_pass, rule
   from insights.parsers.installed_rpms import InstalledRpms

   KEY = "BASH_VERSION"

   CONTENT = "Bash RPM Version: {{ bash_version }}"


   @rule(InstalledRpms)
   def report(rpms):
       bash_ver = rpms.get_max('bash')
       return make_pass(KEY, bash_version=bash_ver)

.. HINT::
   You can download the
   `code for bash_version.py <https://github.com/RedHatInsights/insights-core/blob/master/examples/rules/bash_version.py>`_

You'll notice that this file does not include the `#!/usr/bin/env python` and the `run(report...)`
lines.  You can still run this rule easily from the command line using `insights-run`.  Here's how
you can run each rule individually with `insights-run`::

    (insights-core)[userone@hostone project_dir/myrules]$ insights-run -p bash_version
    (insights-core)[userone@hostone project_dir/myrules]$ insights-run -p hostname_rel

Finally you can run multiple rules at once.  First you can specify a comma separate list of all rules
as the argument to `-p`::

    (insights-core)[userone@hostone project_dir/myrules]$ insights-run -p bash_version,hostname_rel

The second way to do this is by taking advantage of the fact that all of your rules are in one package
(remember the empty ``__init__.py`` file we created in the ``myrules`` dir to make it a python package).
Just provide the name of the package to run all rules in the package::

    (insights-core)[userone@hostone project_dir/myrules]$ cd ..
    (insights-core)[userone@hostone project_dir]$ insights-run -p myrules

You can run one module in the package using either dot notation, ``myrules.bash_version``, or simply
using bash tab completion to specify the path name ``myrules/bash_version.py``::

    (insights-core)[userone@hostone project_dir]$ insights-run -p myrules.bash_version
    (insights-core)[userone@hostone project_dir]$ insights-run -p myrules/bash_version.py

.. TIP::
   If you don't see the results you expect when using `insights-run`, try adding the `-t` flag
   to show python exception tracebacks and look for exceptions in your rule code.  You can
   expect to see some exceptions from parsers if the data is not accessible due to permissions
   or is missing from your system or the data source.

Evaluating Archive Files and Directories
========================================

By default Insights will collect information from your computer for evaluation
of your rules.  You can also evaluate a sosreport or insights archive or directory by
specifying it as the last argument on the command line::

    (insights-core)[userone@hostone project_dir/myrules]$ insights-run -p bash_version sosreport.tar.xz
    (insights-core)[userone@hostone project_dir/myrules]$ insights-run -p bash_version sosreport_dir

For a more detailed description of how to develop your own rules see the
`Rule tutorial section <https://insights-core-tutorials.readthedocs.io/en/latest/rule_tutorial_index.html>`_
in the
`Insights Core Tutorials <https://insights-core-tutorials.readthedocs.io/en/latest/index.html>`_.

*******************************
Insights Core Contributor Setup
*******************************

If you wish to contribute to the insights-core project you'll need to create a fork in GitHub.
See `Fork a repo <https://help.github.com/articles/fork-a-repo/>`_ on Github for help on forking
a repo.  After you have created your fork continue with these steps to setup your development
environment.

1. Clone your fork::

    [userone@hostone project_dir]$ git clone git@github.com:your-user/insights-core.git

2. Reference the original project as "upstream"::

    [userone@hostone project_dir]$ cd insights-core
    [userone@hostone project_dir/insights-core]$ git remote add upstream git@github.com:RedHatInsights/insights-core.git

At this point, you would synchronize your fork with the upstream project
using the following commands::

    [userone@hostone project_dir/insights-core]$ git pull upstream master
    [userone@hostone project_dir/insights-core]$ git push origin master

You should synchronize your fork with the upstream project regularly to ensure you have the most
recent Insights Core code.

For more details steps on contributing to Insights Core see
`CONTRIBUTING.md <https://github.com/RedHatInsights/insights-core/blob/master/CONTRIBUTING.md>`_.
