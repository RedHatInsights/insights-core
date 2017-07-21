.. _tutorial-rule-development:

###########################
Tutorial - Rule Development
###########################

The purpose of a rule is to evaluate various facts and determine one or more
results about a system.  For our example rule we are interested in knowing
whether a system with ``sshd`` is configured according to the following
guidelines::

    # Password based logins are disabled - only public key based logins are allowed.
    AuthenticationMethods publickey

    # LogLevel VERBOSE logs user's key fingerprint on login. Needed to have
    # a clear audit track of which key was using to log in.
    LogLevel VERBOSE

    # Root login is not allowed for auditing reasons. This is because it's
    # difficult to track which process belongs to which root user:
    PermitRootLogin No

    # Use only protocol 2 which is the default.  1 should not be listed
    # Protocol 2

We also want to know what version of OpenSSH we are running if we find any problems.

**************************************
Preparing Your Development Environment
**************************************

The following instructions assume that you have a insights-core development
environment setup and working, and that your rules root dir and insights-core
root dir a subdirs of the same root dir.  First you will need to run
a command that is in your insights-core environment to create a new rules
development developmentdirectory.  The following commands will create a new
``myrules`` project for development of your new rule.  Make sure
you start with your virtual environment set to the insights-core project::

    $ cd insights-core
    $ source bin/activate
    (insights-core) $ cd ..
    (insights-core) $ mkdir myrules
    (insights-core) $ cd myrules
    (insights-core) $ insights-core-scaffold myrules
    (insights-core) $ ls -R
    .:
    conftest.py  myrules  readme.md  setup.cfg  setup.py
    
    ./myrules:
    __init__.py  plugins  tests
    
    ./myrules/plugins:
    __init__.py
    
    ./myrules/tests:
    __init__.py  integration.py

Next you need to bootstrap your development environment to create
a new virtual environment and install all required libraries::

    (insights-core) $ deactivate
    $ python setup.py bootstrap
    running bootstrap
    New python executable in /home/bfahr/work/insights/myrules/bin/python2
    Also creating executable in /home/bfahr/work/insights/myrules/bin/python
    Installing setuptools, pip, wheel...done.
    Obtaining file:///home/bfahr/work/insights/myrules
    Collecting insights-core (from Myrules==0.0.1)
    Collecting coverage (from Myrules==0.0.1)
    Collecting pytest (from Myrules==0.0.1)
      Using cached pytest-3.0.3-py2.py3-none-any.whl
    Collecting pytest-cov (from Myrules==0.0.1)
      Using cached pytest_cov-2.4.0-py2.py3-none-any.whl
    Collecting py>=1.4.29 (from pytest->Myrules==0.0.1)
      Using cached py-1.4.31-py2.py3-none-any.whl
    Installing collected packages: insights-core, coverage, py, pytest, pytest-cov, Myrules
      Running setup.py develop for Myrules
    Successfully installed Myrules coverage-4.2 insights-core-0.3.5 py-1.4.31 pytest-3.0.3 pytest-cov-2.4.0

The last step in setting up your virtual environment is to enable
your virtual environment and install your local development copy of
the insights-core project::

    $ source bin/activate
    (myrules) $ pip install -e ../insights-core/
    Obtaining file:///home/bfahr/work/insights/insights-core
    Collecting pyyaml (from insights-core==1.13.0)
    Installing collected packages: pyyaml, insights-core
      Found existing installation: insights-core 0.3.5
        Uninstalling insights-core-0.3.5:
          Successfully uninstalled insights-core-0.3.5
      Running setup.py develop for insights-core
    Successfully installed insights-core pyyaml-3.12

You are now ready to being writing your rule.

************************
Secure Shell Server Rule
************************

Rule Code
=========

First we need to create a template rule file.  It is recommendated that
you name the file based the results it produces.  Since we are looking
at sshd security we will name the file ``myrules/plugins/sshd_secure.py``.
Notice that the file is located in the ``myrules/plugins`` subdirectory
of your project::

    (myrules) $ touch myrules/plugins/sshd_secure.py

Here's the basic contents of the rule file:

.. code-block:: python
   :linenos:

   from insights.core.plugins import make_response, rule
   from insights.parsers.ssh import SshDConfig

   ERROR_KEY = "SSHD_SECURE"


   @rule(requires=[SshDConfig])
   def report(local, shared):
       sshd_config = shared[SshDConfig]
       """
       1. Evalute config file facts
       2. Evaluate version facts
       """
       if results_found:
           return make_response(ERROR_KEY, results=the_results)

First we import the insights-core methods ``make_response()`` for creating
a response and ``rule()`` to decorate our rule method so that it
will be invoked by insights-core with the appropriate parser information.
Then we import the parsers that provide the facts we need.

.. code-block:: python
   :linenos:

   from insights.core.plugins import make_response, rule 
   from insights.parsers.ssh import SshDConfig

Next we define a unique error key string, ``ERROR_KEY`` that will be
collected by insights-core when our rule is executed, and provided in the results for
all rules.  This string must be unique among all of your rules, or
the last rule to execute will overwrite any results from other rules
with the same key.

.. code-block:: python
   :linenos:
   :lineno-start: 4

   ERROR_KEY = "SSHD_SECURE"

The ``@rule()`` decorator is used to mark the rule method that will be
invoked by insights-core.  Arguments to ``@rule()`` are listed in the
following table. If the rule should handle Satellite clusters, use
`@cluster_rule` instead of `@rule`.

========  =======  ==================================================
Arg Name  Type     Description
========  =======  ==================================================
required  list     List of required shared parsers, it may include
                   an embedded list meaning any one in the list is
                   sufficient.
optional  list     List of options shared parsers.
========  =======  ==================================================

Our rule requires one shared parser ``SshDConfig``.  We will add a
requirement to obtain facts about installed RPMs in the final code.

.. code-block:: python
   :linenos:
   :lineno-start: 7

   @rule(requires=[SshDConfig])

The name of our
rule method is ``report``, but the name may be any valid method name.
The purpose of the method is to access the parser facts stored
in ``shared[SshDConfig]``, evaluate the facts.  If any results
are found in the evaluation then a response is created with the
``ERROR_KEY`` and any data that you want to be associated with
the results.  This data is made available in the customer interface
or results output.  You may use zero or more named arguments to
provide the data to ``make_response``.  You should use meaningful
argument names as it helps in understanding of the results.

.. code-block:: python
   :linenos:
   :lineno-start: 8

   def report(local, shared):
       sshd_config = shared[SshDConfig]
       """
       1. Evalute config file facts
       2. Evaluate version facts
       """
       if results_found:
           return make_response(ERROR_KEY, results=the_results)

In order to perform the evaluation we need the facts for ``sshd_config``
and for the OpenSSH version.  The ``SshDConfig`` parser we developed
will provide
the facts for ``sshd_config`` and we can use another parser,
``InstalledRpms`` to help us determine facts about installed software.

Here is our updated rule with check for the configuration options and
the software version:

.. code-block:: python
   :linenos:

   from insights.core.plugins import make_response, rule
   from insights.parsers.ssh import SshDConfig
   from insights.parsers.installed_rpms import InstalledRpms

   ERROR_KEY = "SSHD_SECURE"


   @rule(requires=[InstalledRpms, SshDConfig])
   def report(local, shared):
       sshd_config = shared[SshDConfig]
       errors = {}

       auth_method = sshd_config.last('AuthenticationMethods')
       if auth_method:
           if auth_method.lower() != 'publickey':
               errors['AuthenticationMethods'] = auth_method
       else:
           errors['AuthenticationMethods'] = 'default'

       log_level = sshd_config.last('LogLevel')
       if log_level:
           if log_level.lower() != 'verbose':
               errors['LogLevel'] = log_level
       else:
           errors['LogLevel'] = 'default'

       permit_root = sshd_config.last('PermitRootLogin')
       if permit_root:
           if permit_root.lower() != 'no':
               errors['PermitRootLogin'] = permit_root
       else:
           errors['PermitRootLogin'] = 'default'

       # Default Protocol is 2
       protocol = sshd_config.last('Protocol')
       if protocol:
           if protocol.lower() != '2':
               errors['Protocol'] = protocol

       if errors:
           openssh_version = shared[InstalledRpms].get_max('openssh')
           return make_response(ERROR_KEY, errors=errors, openssh=openssh_version.package)

This rules code implements the checking of the four configuration values
``AuthenticationMethods``, ``LogLevel``, ``PermitRootLogin``, and ``Protocol``,
and returns any errors found using ``make_response`` in the return. Also,
if errors are found, the ``InstalledRpms`` parser facts are queried to determine
the version of `OpenSSH` installed and that value is also returned.  If
no values are found then an implicit ``None`` is returned.

Rule Testing
============

Testing is an important aspect of rule development and it helps ensure
accurate rule logic.  There are generally two types of testing to be
performed on rules, unit and integration testing.  If rule logic is
divided among multiple methods then unit tests should be written to
test the methods.  If there is only one method then unit tests may
not be necessary.  Integration tests are necessary to test the rule
in a simulated insights-core environment.  This will be easier to understand
by viewing the test code:

.. code-block:: python
   :linenos:

   from myrules.plugins import sshd_secure
   from insights.tests import InputData, archive_provider, context_wrap
   from insights.core.plugins import make_response
   # The following imports are not necessary for integration tests
   from insights.parsers.ssh import SshDConfig
   from insights.parsers.installed_rpms import InstalledRpms

   OPENSSH_RPM = """
   openssh-6.6.1p1-31.el7.x86_64
   openssh-6.5.1p1-31.el7.x86_64
   """.strip()

   EXPECTED_OPENSSH = "openssh-6.6.1p1-31.el7"

   GOOD_CONFIG = """
   AuthenticationMethods publickey
   LogLevel VERBOSE
   PermitRootLogin No
   # Protocol 2
   """.strip()

   BAD_CONFIG = """
   AuthenticationMethods badkey
   LogLevel normal
   PermitRootLogin Yes
   Protocol 1
   """.strip()

   DEFAULT_CONFIG = """
   # All default config values
   """.strip()


   def test_sshd_secure():
       """This is not really necessary since it duplicates the testing
       performed in the integration tests. But sometimes it is useful
       when debugging a rule. It is useful if you have modules in your
       rules that need to be tested.
       """
       local = {}
       shared = {}
       shared[SshDConfig] = SshDConfig(context_wrap(BAD_CONFIG))
       shared[InstalledRpms] = InstalledRpms(context_wrap(OPENSSH_RPM))
       result = sshd_secure.report(local, shared)
       errors = {
           'AuthenticationMethods': 'badkey',
           'LogLevel': 'normal',
           'PermitRootLogin': 'Yes',
           'Protocol': '1'
       }
       expected = make_response(sshd_secure.ERROR_KEY,
                                errors=errors,
                                openssh=EXPECTED_OPENSSH)
       assert result == expected


   @archive_provider(sshd_secure)
   def integration_tests():
       input_data = InputData(name="GOOD_CONFIG")
       input_data.add("sshd_config", GOOD_CONFIG)
       input_data.add("installed-rpms", OPENSSH_RPM)
       yield input_data, []

       input_data = InputData(name="BAD_CONFIG")
       input_data.add("sshd_config", BAD_CONFIG)
       input_data.add("installed-rpms", OPENSSH_RPM)
       errors = {
           'AuthenticationMethods': 'badkey',
           'LogLevel': 'normal',
           'PermitRootLogin': 'Yes',
           'Protocol': '1'
       }
       expected = make_response(sshd_secure.ERROR_KEY,
                                errors=errors,
                                openssh=EXPECTED_OPENSSH)
       yield input_data, [expected]

       input_data = InputData(name="DEFAULT_CONFIG")
       input_data.add("sshd_config", DEFAULT_CONFIG)
       input_data.add("installed-rpms", OPENSSH_RPM)
       errors = {
           'AuthenticationMethods': 'default',
           'LogLevel': 'default',
           'PermitRootLogin': 'default'
       }
       expected = make_response(sshd_secure.ERROR_KEY,
                                errors=errors,
                                openssh=EXPECTED_OPENSSH)
       yield input_data, [expected]

Test Data
---------

Data utilized for all tests is defined in the test module.  In this
case we will use an OpenSSH RPM version that is present in RHEL 7.2,
``OPENSSH_RPM`` and three configuration files for ``sshd_config``.
``GOOD_CONFIG`` has all of the values that we are looking for and
should not return any error results.  ``BAD_CONFIG`` has all bad
values so it should return all error results.  And ``DEFAULT_CONFIG``
has no values present so it should return errors for all values
except ``Protocol`` which defaults to the correct value.

.. code-block:: python
   :linenos:
   :lineno-start: 8

   OPENSSH_RPM = """
   openssh-6.6.1p1-31.el7.x86_64
   openssh-6.5.1p1-31.el7.x86_64
   """.strip()

   EXPECTED_OPENSSH = "openssh-6.6.1p1-31.el7"

   GOOD_CONFIG = """
   AuthenticationMethods publickey
   LogLevel VERBOSE
   PermitRootLogin No
   # Protocol 2
   """.strip()

   BAD_CONFIG = """
   AuthenticationMethods badkey
   LogLevel normal
   PermitRootLogin Yes
   Protocol 1
   """.strip()

   DEFAULT_CONFIG = """
   # All default config values
   """.strip()

Unit Tests
----------

First lets look at a unit test for our rule.  The unit test
is named ``test_sshd_secure``.  It may be named anything as long
as the name begins with ``test_`` which is what ``py.test`` looks
for to identify tests.  As with all unit tests, no framework is
provided so you must create all of the necessary structures for
your tests.  In this case we need a ``shared`` parameter which
is a ``dict`` object, and it need keys for each parser that we
require in our rule, here ``SshDConfig`` and ``InstalledRpms``.
This looks very similar to our parser test code except that 
we may have to support multiple parsers.  We invoke our 
rule ``ssh_secure.report`` and compare the results to the
expected results using the ``assert`` statement:

.. code-block:: python
   :linenos:
   :lineno-start: 34

   def test_sshd_secure():
       """This is not really necessary since it duplicates the testing
       performed in the integration tests. But sometimes it is useful
       when debugging a rule. It is useful if you have modules in your
       rules that need to be tested.
       """
       local = {}
       shared = {}
       shared[SshDConfig] = SshDConfig(context_wrap(BAD_CONFIG))
       shared[InstalledRpms] = InstalledRpms(context_wrap(OPENSSH_RPM))
       result = sshd_secure.report(local, shared)
       errors = {
           'AuthenticationMethods': 'badkey',
           'LogLevel': 'normal',
           'PermitRootLogin': 'Yes',
           'Protocol': '1'
       }
       expected = make_response(sshd_secure.ERROR_KEY,
                                errors=errors,
                                openssh=EXPECTED_OPENSSH)
       assert result == expected

As you will see when we review the integration tests, this code is
duplicative of the testing done there.  However, it does show how
unit tests work, and it is sometimes necessary to debug complex rules.
Because integration tests run in the framework, which is in turn run
within py.test, it's not as easy to get output for debugging purposes.
Performing these tests as unit tests removes one layer of complexity
but requires more setup code.

Integration Tests
-----------------

Integration tests are performed within the insights-core framework.  The
``InputData`` class is used to define the raw data that we want to be
present, and the framework creates an archive file to be input to
the insights-core framework so that the parsers will be invoked, and then
the rules will be invoked.  You need to create ``InputData`` objects
will all of the information that is necessary for parsers required
by your rules.  If input data is not present then parsers will not be
executed, and if your rule requires any of those parsers, your rule.

To create your integration tests you must first create a method that
does not begin with ``test_`` and decorate that method with
``@archive_provider(rule_name)`` having an argument that is your
rule module name.  Typically we name the method ``integration_tests``.

.. code-block:: python
   :linenos:
   :lineno-start: 57

   @archive_provider(sshd_secure)
   def integration_tests():

Next we create an ``InputData`` object and it is useful to provide
a ``name=test_name`` argument to the contstructor.  When you execute
integration tests, that name will show up in the results and make it
easier to debug if you have any problems. Next you add your test
inputs to the ``InputData`` object that will be used to create the
test archive. Once all of the data has been added, a ``yield``
statement provides the input data and expected results to the
``archive_provider`` to run the test.  In this particular test
case we provided all `good` data so we did not expect any results
``[]``.

.. code-block:: python
   :linenos:
   :lineno-start: 59

       input_data = InputData(name="GOOD_CONFIG")
       input_data.add("sshd_config", GOOD_CONFIG)
       input_data.add("installed-rpms", OPENSSH_RPM)
       yield input_data, []

.. note:: If your input data has a path that is significant
    to the interpretation of the data, such as
    ``/etc/sysconfig/network-scripts/ifcfg-eth0`` where there may be
    multiple ``ifcfg`` scripts, you'll need to add the path as well.
    For example::

        input_data.add("ifcfg",
                       IFCFG_ETH0,
                       path="etc/sysconfig/network-scripts/ifcfg-eth0")
        input_data.add("ifcfg",
                       IFCFG_ETH1,
                       path="etc/sysconfig/network-scripts/ifcfg-eth1")

In the second test case we are using `bad` input data so we have to
also provide the errors that we expect our rule to return to the
framework.  The expected results are in the same format that we
create the return value in ``ssh_secure.report``.

.. code-block:: python
   :linenos:
   :lineno-start: 64

       input_data = InputData(name="BAD_CONFIG")
       input_data.add("sshd_config", BAD_CONFIG)
       input_data.add("installed-rpms", OPENSSH_RPM)
       errors = {
           'AuthenticationMethods': 'badkey',
           'LogLevel': 'normal',
           'PermitRootLogin': 'Yes',
           'Protocol': '1'
       }
       expected = make_response(sshd_secure.ERROR_KEY,
                                errors=errors,
                                openssh=EXPECTED_OPENSSH)
       yield input_data, [expected]

Running the Tests
=================

We execute these tests by moving to the root directory of our rules
project, ensuring that our virtual environment is active, and running
``py.test``::

    (myrules) $ py.test
    ================== test session starts =======================
    platform linux2 -- Python 2.7.12, pytest-3.0.3, py-1.4.31, pluggy-0.4.0
    rootdir: /home/bfahr/work/insights/myrules, inifile: setup.cfg
    plugins: cov-2.4.0
    collected 4 items
    
    myrules/tests/integration.py ...
    myrules/tests/test_sshd_secure.py .
    
    ================ 4 passed in 0.02 seconds ===================
    
If any tests fail you can use the following ``py.test`` ``-s -v --appdebug``
options to help get additional information.  If you want to limit which
test run you can also use the ``-k test_filter_string`` option.

Also run ``py.test`` with no options when you have finished to ensure that
you everything in your environment is working correctly, and once all tests
pass you are finished.

.. --------------------------------------------------------------------
.. Put all of the references that are used throughout the document here
.. Links:

.. _Red Hat Customer Portal: https://access.redhat.com
.. _Red Hat Insights Portal: https://access.redhat.com/products/red-hat-insights.
.. _insights-core Repository: https://github.com/RedHatInsights/insights-core
.. _Mozilla OpenSSH Security Guidelines: https://wiki.mozilla.org/Security/Guidelines/OpenSSH
