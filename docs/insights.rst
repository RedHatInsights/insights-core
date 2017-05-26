################
Red Hat Insights
################

:Version: 0.1
:Date: Oct 27, 2016

.. contents:: Table of Contents
    :depth: 6

############
Introduction
############

The Red Hat Insights application is built upon four somewhat independent
subsystems:

#. the collection component;
#. the processing engine component;
#. the plugin componets; and
#. the customer interface component.

The collection component is called Red Hat Access Insights ("Access") and is part
of the
Red Hat Enterprise Linux distribution.  It is installed via RPM onto a host
system where it collect information to send to the infrastructure engine for
analysis.  The processing engine component is called Falafel and runs on Red Hat
internal systems to process the information collected by Access and provides
results to the customer interface component.  Falafel processes the information
by extracting each unique set of data and analyzing the data via algorithms
implemented in the plugin components ("Plugins").  The results of the analysis
are presented to the user via the user interface component ("UI").  The figure
below provides a graphical overview of the components and the information flow.

.. figure:: insights_overview.png
   :alt: Insights Overview

Overview of the Insights Components and Information Flow

****************************
Access Insights - Collection
****************************

Collection of information is performed by the Access component of Insights.
The RPM is installed on one or more host systems where data collection is to
be performed. A host system may be a physical system or a virtual machine.
Information collected by Access is filtered to remove sensitive information
and then sent to Falafel for analysis.  Collection is typically performed
daily but may be configured to run on other schedules.  It may also be
disabled/enabled by the host administrator.

.. todo:: TODO: Include info about archives for Satellite and virtual machines.

.. todo:: TODO: Include info about types of data collected, for example the spec
   types such as command spec, filespec, etc.

More information about the
Access component can be found at `Red Hat Insights Portal`_

***************************
Falafel - Processing Engine
***************************

Once host information has been collected by Access it is transferred to
Falafel for processing.  Falafel is a SaaS application hosted at Red Hat.
Falafel processes information as it is received and provides the results
to the Customer Inferface for review by the customer.

Falafel begins processing the information by unarchiving the information
and identify each type of information that is included.  Based on the
type of information present, Falafel identifies specific plugins that
will perform the analysis. Falafel then configures the plugins into a
map/reduce network and executes them to analyze the data.

Each plugin provides results which are all collected by Falafel and
upon job completion the results are made available to the Customer
Interface for review.

More information about the Falafel component can be found at
https://github.com/ansible/falafel

****************************
Plugin Components - Analysis
****************************

Falafel coordinates analaysis of the information via the plugins. There
are two primary types of plugins that are used in the analysis, mappers
and reducers.  Mapper plugins are responsible for analyzing the raw data
and converting it into a usable *facts* that can be evaluated by the
reducers.  The reducer plugins then evaluate these facts and to produce
additional facts and results.  These results are then accumulated and
consolidated by Falafel to provide to the Customer Inferface.

Falafel evalutes the information and only invokes plugins if the
information or facts required by the plugin are available.

*************************************
Customer Interface - Analysis Results
*************************************

The Customer Interface provides views of the Insights results via the
`Red Hat Customer Portal`_. Multiple views are provided for all
of customer's systems reporting to Insights.


###############
Role of Plugins
###############

Plugins are the primary mechanism to add functionality to Insights.
Falafel is the framework upon which Red Hat Insights rules are built and
delivered.  The basic purpose is to apply "rules" to a set of files collected
from a system at a given point in time. There are two basic types of plugins,
Mappers and Reducers.  Reducer plugins may be further divided into Fact
Reducers and Rules.  Mappers analyze raw input data of a particular type
to produce *facts* about the information.  Fact Reducers analyze the
fact outputs of one or more Mappers to produce additional *facts*.
Rules consume facts from Mappers and Reducers to produce *results*.

****************
Role of a Mapper
****************

Mappers depend upon the presence of specific items in the input
information such as the contents of file such as ``/etc/fstab`` or
the output of a command such as ``/usr/bin/lsblk``.  Mappers read
the content and generate facts such as a list of devices and
mount points from ``/etc/fstab``, and relationships between
block devices from the ``/usr/bin/lsblk`` command. Mappers
also compensate for differences between the output from
different versions of Red Hat Enterprise Linux.  This allows
all Reducers and Rules to focus analysis on the facts regardless
of OS version, unless OS version is the fact of interest.

**********************
Role of a Fact Reducer
**********************

Fact Reducers are useful when multiple facts may need to be evaluated
in order to determine another fact about a system.  A simple example is
the fact indicating the Red Hat release running on a system. For example
the fact could indicate that Red Hat 6.7 or 7.2 is running on a system.
Red Hat 6.7 or 7.2. One
source of facts about Red Hat release is the ``/usr/bin/uname -a``
command.  Another source of facts is the file ``/etc/redhat_release``.
So a Uname Mapper could provide one fact about the release, and a
Redhat_Release Mapper could provide another face.  A Fact Reducer
could then be used to look at each of these facts and provide
an additional fact about the release.  The advantage of using
the Reducer is that it provides a consistent fact regardless of
whether the the Uname information or Redhat_Release information
is present in the Insights data.  As long as one of them is present
the Red Hat release Fact Reducer will provide its fact.

**************
Role of a Rule
**************

Rules analyze facts and produce results describing some
characteristic of system.  Rules may use a number of facts
to produce a result.  For instance a Rule may need to know
the Red Hat release, what version of a specific library is
installed,
and whether certain kernel parameters are set in order to determine
that a system may be subject to a particular security vulnerability.

##################
Plugin Development
##################

The Aspect Insights application collects three general types of
information:

1. files such as ``/etc/fstab``;
2. command output such as ``/usr/bin/uname -a``; and
3. pattern files such as ``/etc/sysconfig/network-scripts/ifcfg-.*``.

Specifications for the data to be collected are provided in the module
falafel.config.specs.  The specs corresponding to the preceding list
are shown in the following table:

=========  ==============  ========================================
Spec Name  Spec Type       Spec Identifier
=========  ==============  ========================================
"fstab"    SimpleFileSpec  "etc/fstab"
"uname"    CommandSpec     "/bin/uname -a"
"ifcfg"    PatternSpec     "etc/sysconfig/network-scripts/ifcfg-.*"
=========  ==============  ========================================

These specifications are also in the Aspect application, but may not
be installed on every system.  The Aspect RPM is developed and
distributed with Red Hat Enterprise Linux as part of the base distribution.
Updates to the Aspect RPM occur less frequently than to the SaaS application.
Additionally customers may not update the Aspect RPM. So developers need to
check both the Falafel and the Aspect applications to determine what information
is available for processing in Insights.

*************
Prerequisites
*************

All Plugin code is written in Python and all Insights libraries
and framework code necessary for development and execution are
stored in Git repositories.  Before you begin make sure you have
the following installed:

* Python 2.7
* Git
* Python Virtualenv
* Python PIP

Further requirements can be found in the readme.md files associated with the
specific project.

******************
Mapper Development
******************

The purpose of a Mapper is to process raw content and map it
into format that is usable by reducers and rules.  Raw content
is content obtained directly from a system file or command, and
may collected by Insights Aspect, or from some other source such
as a SOS Report.  The following examples will demonstrate development of
different types of mappers.

Preparing Your Development Environment
======================================

First you need to create your own fork of the Falafel project.  Do this by
going to the `Falafel Repository`_ on github and clicking on the
**Fork** button.

You will now have an *insights-rules* repository under your github user that
you can use to checkout the code to your development environment.  To check
out the code go to the repository page for your fork and copy the link to
download the repo.

Once you have copied this link then go to a terminal in your working directory
and use the ``git`` command to clone the repository.  In this example the
working directory is ``/home/bfahr/work``::

    [bfahr@bfahrvm2 work]$ pwd
    /home/bfahr/work
    [bfahr@bfahrvm2 work]$ git clone git@github.com:bfahr/falafel.git
    Cloning into 'falafel'...
    remote: Counting objects: 5665, done.
    remote: Compressing objects: 100% (1716/1716), done.
    remote: Total 5665 (delta 4043), reused 5378 (delta 3890)
    Receiving objects: 100% (5665/5665), 1.62 MiB | 292.00 KiB/s, done.
    Resolving deltas: 100% (4043/4043), done.

Next you need to follow the steps documented in the file ``falafel/readme.md``
to create a virtual environment and set it up for development::

    [bfahr@bfahrvm2 work]$ cd falafel
    [bfahr@bfahrvm2 falafel]$ virtualenv .
    New python executable in ./bin/python
    Installing Setuptools..................................................done.
    Installing Pip....................................................done.
    [bfahr@bfahrvm2 falafel]$ source bin/activate
    (falafel)[bfahr@bfahrvm2 falafel]$ pip install -e .[develop]

Once these steps have been completed you will have a complete development
environment for mappers and reducers.  You can confirm that everything is setup
correctly by running the tests, ``py.test``.  Your results should look
something like this::

    (falafel)[bfahr@bfahrvm2 falafel]$ py.test
    ======================== test session starts =============================
    platform linux2 -- Python 2.7.5, pytest-3.0.3, py-1.4.31, pluggy-0.4.0
    rootdir: /home/bfahr/work/falafel, inifile: setup.cfg
    plugins: cov-2.4.0
    collected 414 items

    falafel/console/tests/test_package_installed_package.py ......
    [leaving out a long list of test names]
    falafel/web/tests/test_urls.py .
    ====================== short test summary info ===========================
    XFAIL falafel/mappers/tests/test_installed_rpms.py::test_max_min_kernel
      Incorrect implementation

    =============== 413 passed, 1 xfailed in 3.81 seconds ====================

Your development environment is now ready to begin development and you may move
on to the next section.  If you had problems with any of these steps then
double check that you have completed all of the steps in order and if it still
doesn't work, open a `Github issue <https://github.com/ansible/falafel/issues/new>`_.

Secure Shell Mapper
===================

Overview
--------

Secure Shell or ``ssh`` ("SSH") is a commonly used tool to access and interact
with remote systems.  SSH server is configured on a system using the
``/etc/sshd_conf`` file.  Red Hat Enterprise Linux utilizes OpenSSH and the
documentation for the ``/etc/sshd_conf`` file is located
`here <http://man.openbsd.org/sshd_config>`_.

.. _sample-sshd-input:

Here is a portion of the configuration file showing the syntax::

    #	$OpenBSD: sshd_config,v 1.93 2014/01/10 05:59:19 djm Exp $

    Port 22
    #AddressFamily any
    ListenAddress 10.110.0.1
    #ListenAddress ::

    # The default requires explicit activation of protocol 1
    #Protocol 2

Many lines begin with a ``#`` indicating comments, and blank lines are used
to aid readability.  The important lines have a configuration keyword followed
by space and then a configuration value.  So in the mapper we want to make sure
we capture the important lines and ignore the comments and blank lines.

Creating the Initial Mapper Files
---------------------------------

First we need to create the mapper file.  Mapper files are implemented in modules.
The module should be limited to one type of applications.  In this case we are
working with ``ssh`` applications so we will create an ``ssh`` module.  Create
the module file ``falafel/mappers/ssh.py`` in the mappers directory::

    $ touch falafel/mappers/ssh.py

Now edit the file and create the mapper skeleton:

.. code-block:: python
    :linenos:

    from .. import Mapper, mapper


    @mapper('sshd_config')
    class SshDConfig(Mapper):

        def parse_content(content):
            pass

We start by importing the ``Mapper`` class and the ``mapper`` decorator.  Our
mapper will inherit from the ``Mapper`` class and it will be associated with
the ``sshd_config`` input data using the ``mapper`` decorator. Finally we
need to implement the ``parse_content`` subroutine which is required to parse
store the input data in our class.  The base class ``Mapper`` implements a
constructor that will invoke our ``parse_content`` method when the class
is created.

.. note:: The ``from .. import`` here is equivalent to
       ``from falafel.mappers import`` and is implemented by some *magic*
       code elsewhere to help minimize changes to all mappers if the project
       name changes.

Next we'll create the mapper test file ``falafel/mappers/tests/test_ssh.py``
as a skeleton that will aid in the mapper development process:

.. code-block:: python
    :linenos:

    from falafel.mappers.ssh import SshDConfig


    def test_sshd_config():
        pass

Once you have created and saved both of these files and we'll run the test
to make sure everything is setup correctly:

.. code-block:: bash
    :linenos:

    (falafel)[bfahr@bfahrvm2 falafel]$ py.test -k test_ssh
    ================== test session starts ========================
    platform linux2 -- Python 2.7.5, pytest-3.0.3, py-1.4.31, pluggy-0.4.0
    rootdir: /home/bfahr/work/falafel, inifile: setup.cfg
    plugins: cov-2.4.0
    collected 415 items
    
    falafel/mappers/tests/test_ssh.py .
    
    ================== 414 tests deselected =======================
    ========= 1 passed, 414 deselected in 0.46 seconds ============
    
When you invoke ``py.test`` with the ``-k`` option it will only run tests
which match the filter, in this case tests that match *test_ssh*.  So our
test passed as expected.

.. hint:: You may sometimes see a message that ``py.test`` cannot be found,
       or see some other related message that doesn't make sense. The first
       think to check is that you have activated your virtual environment by
       executing the command ``source bin/activate`` from the root directory
       of your project.  You prompt should change to include ``(falafel)`` if
       your virtual enviroment is activated. You can deactivate the virtual
       environment by typing ``deactivate``. You can find more information
       about virtual environments here: 
       http://docs.python-guide.org/en/latest/dev/virtualenvs/

Mapper Implementation
---------------------

Typically mapper and reducer development is driven by rules that need facts
generated by the mappers and redcucers.  Regardless of the specific
requirements, it is important (1) to implement basic functionality by getting
the raw data into a usable format, and (2) to not overdo the implementation
because we can't anticipate every use of the mapper output.  In our example
we will eventually be implementing the rules that will warn us about systems
that are not configured properly. Initially
our mapper implementation will parsing the input data into
key/value pairs.  We may later discover that we can optimize rules by moving
duplicate or complex processing into the mapper.

Test Code
^^^^^^^^^

Referring back to our :ref:`sample SSHD input <sample-sshd-input>` we will
start by creating a test for the output that we want from our mapper:

.. code-block:: python
   :linenos:

   from falafel.mappers.ssh import SshDConfig
   from falafel.tests import context_wrap

   SSHD_CONFIG_INPUT = """
   #	$OpenBSD: sshd_config,v 1.93 2014/01/10 05:59:19 djm Exp $

   Port 22
   #AddressFamily any
   ListenAddress 10.110.0.1
   Port 22
   ListenAddress 10.110.1.1
   #ListenAddress ::

   # The default requires explicit activation of protocol 1
   #Protocol 2
   Protocol 1
   """.strip()


   def test_sshd_config():
       sshd_config = SshDConfig(context_wrap(SSHD_CONFIG_INPUT))
       assert sshd_config is not None
       assert 'Port' in sshd_config
       assert 'PORT' in sshd_config
       assert sshd_config['port'] == ['22', '22']
       assert 'ListenAddress' in sshd_config
       assert sshd_config['ListenAddress'] == ['10.110.0.1', '10.110.0.1']
       assert sshd_config['Protocol'] == ['1']
       assert 'AddressFamily' not in sshd_config
       ports = [l for l in sshd_config if l.keyword == 'Port']
       assert len(ports) == 2
       assert ports[0].value == '22'


First we added an import for the helper function ``context_wrap`` which we'll
use to put our input data into a ``Context`` object to pass to our class
constructor:

.. code-block:: python
   :linenos:
   :emphasize-lines: 2

   from falafel.mappers.ssh import SshDConfig
   from falafel.tests import context_wrap

Next we include the sample data that will be used for the test.  Use of the
``strip()`` function ensures that all whitespace at the beginning and end
of the data are removed:

.. code-block:: python
   :linenos:
   :lineno-start: 4

   SSHD_CONFIG_INPUT = """
   #	$OpenBSD: sshd_config,v 1.93 2014/01/10 05:59:19 djm Exp $

   Port 22
   #AddressFamily any
   ListenAddress 10.110.0.1
   Port 22
   ListenAddress 10.110.1.1
   #ListenAddress ::

   # The default requires explicit activation of protocol 1
   #Protocol 2
   Protocol 1
   """.strip()

Next, to the body of the test, we add code to create an instance of our
mapper class:


.. code-block:: python
   :linenos:
   :lineno-start: 31
   :emphasize-lines: 2

   def test_sshd_config():
       sshd_config = SshDConfig(context_wrap(SSHD_CONFIG_INPUT))


Finally we add our tests using the attributes that we want to be able to
access in our rules.  First a assumptions about the data:

#. some keywords may be present more than once in the config file
#. we want to access keywords in a case insensitive way
#. order of the keywords matter
#. we are not trying to validate the configration file so we won't parse the
   values or analyze sequence of keywords

Now here are the tests:

.. code-block:: python
   :linenos:
   :lineno-start: 33

       assert sshd_config is not None
       assert 'Port' in sshd_config
       assert 'PORT' in sshd_config
       assert sshd_config['port'] == ['22', '22']
       assert 'ListenAddress' in sshd_config
       assert sshd_config['ListenAddress'] == ['10.110.0.1', '10.110.0.1']
       assert sshd_config['Protocol'] == ['1']
       assert 'AddressFamily' not in sshd_config
       ports = [l for l in sshd_config if l.keyword == 'Port']
       assert len(ports) == 2
       assert ports[0].value == '22'

Our tests assume that we want to know whether a particular keyword is present,
regardless of character case used in the keyword, and we want to know the
values of the keyword if present. We don't want
our rules to have to assume any particular case of characters in keywords
so we can make it easy by performing case insensitive compares and assuming
all lowercase for access.  This may not always work, but in this example
it is a safe assumption.

Mapper Code
^^^^^^^^^^^

The subroutine ``parse_content`` is responsible for parsing the input data and
storing the results in class attributes.  You may choose the attributes that
are necessary for your mapper, there are no requirements to use specific names
or types.  Some general recommendations for mapper class implementation are:

* Choose attributes that make sense for use by actual rules, or how you
  anticipate rules to use the information. If rules need to iterate over
  the information then a ``list`` might be best, or if rules could access
  via keywords then ``dict`` might be better.
* Choose attribute types that are not so complex they cannot be easily
  understood or serialized.  Unless you know you need something complex
  keep it simple.
* Use the ``@property`` decorator to create readonly getters and simplify
  access to information.

Now we need to implement the mapper that will satisify our tests.

.. code-block:: python
   :linenos:

    from collections import namedtuple
    from .. import Mapper, mapper, get_active_lines


    @mapper('sshd_config')
    class SshDConfig(Mapper):

        KeyValue = namedtuple('KeyValue', ['keyword', 'value', 'kw_lower'])

        def parse_content(self, content):
            self.lines = []
            for line in get_active_lines(content):
                kw, val = line.split(None, 1)
                self.lines.append(self.KeyValue(kw.strip(), val.strip(), kw.lower().strip()))
            self.keywords = set([k.kw_lower for k in self.lines])

        def __contains__(self, keyword):
            return keyword.lower() in self.keywords

        def __iter__(self):
            for line in self.lines:
                yield line

        def __getitem__(self, keyword):
            kw = keyword.lower()
            if kw in self.keywords:
                return [kv.value for kv in self.lines if kv.kw_lower == kw]

We added an imports to our skeleton to utilize ``get_active_lines()`` and
``namedtuples``. ``get_active_lines()`` is one of the many helper methods
that you can find in ``falafel/mappers/__init__.py``, ``falafel/core/__init__.py``,
and ``falafel/util/__init__.py``.  ``get_active_lines()`` will remove all
blank lines and comments from the input which simplifies your mappers
parsing logic.

.. code-block:: python
   :linenos:

    from collections import namedtuple
    from .. import Mapper, mapper, get_active_lines

We can use ``namedtuples`` to help simplify access to the information we
are storing in our mapper by creating a namedtuple with the named attributes
``keyword``, ``value``, and ``kw_lower`` where *kw_lower* is the lowercase
version of the *keyword*.

.. code-block:: python
   :linenos:
   :lineno-start: 8

        KeyValue = namedtuple('KeyValue', ['keyword', 'value', 'kw_lower'])

In this particular mapper we have chosen to store all lines (``self.lines``)
as ``KeyValue`` named tuples since we don't know what future rules might.
We are also storing the ``set`` of lowercase keywords (``self.keywords``)
to make it easier to
determine if a keyword is present in the data.  The values are left
unparsed as we don't know how a rule might need to evaluate them.

.. code-block:: python
   :linenos:
   :lineno-start: 10

        def parse_content(self, content):
            self.lines = []
            for line in get_active_lines(content):
                kw, val = line.split(None, 1)
                self.lines.append(self.KeyValue(kw.strip(), val.strip(), kw.lower().strip()))
            self.keywords = set([k.kw_lower for k in self.lines])

Finally we implement some "dunder" methods to simplify use of the class.
``__contains__`` enables the ``in`` operator for keyword checking.  
``__iter__`` enables iteration over the contents of ``self.lines``. And
``__getitem__`` enables access to all values of a keyword.

.. code-block:: python
   :linenos:
   :lineno-start: 17

        def __contains__(self, keyword):
            return keyword.lower() in self.keywords

        def __iter__(self):
            for line in self.lines:
                yield line

        def __getitem__(self, keyword):
            kw = keyword.lower()
            if kw in self.keywords:
                return [kv.value for kv in self.lines if kv.kw_lower == kw]

We now have a complete implementation of our mapper.  It could certainly
perform further analysis of the data and more methods for access, but
it is better keep the mapper simple in the beginning.  Once it is in
use by rules it will be easy to add functionality to the mapper to
allow simplification of the rules.

Mapper Documentation
--------------------

The last step to complete implementation of our mapper is to create
the documentation.  The guidelines and examples for mapper documentation is
provided in the section :doc:`docs_guidelines`.

The following shows our completed mapper including documentation.

.. code-block:: python
   :linenos:

   """
   ssh - Files for configuration of `ssh`
   ======================================

   The ``ssh`` module provides parsing for the ``sshd_config``
   file.  The ``SshDConfig`` class implements the parsing and
   provides a ``list`` of all configuration lines present in
   the file.

   Sample input is provided in the *Examples*.

   Examples:
       >>> sshd_config_input = '''
       ... #	$OpenBSD: sshd_config,v 1.93 2014/01/10 05:59:19 djm Exp $
       ...
       ... Port 22
       ... #AddressFamily any
       ... ListenAddress 10.110.0.1
       ... Port 22
       ... ListenAddress 10.110.1.1
       ... #ListenAddress ::
       ...
       ... # The default requires explicit activation of protocol 1
       ... #Protocol 2
       ... Protocol 1
       ... '''.strip()
       >>> from falafel.tests import context_wrap
       >>> shared = {SshDConfig: SshDConfig(context_wrap(sshd_config_input))}
       >>> sshd_config = shared[SshDConfig]
       >>> 'Port' in sshd_config
       True
       >>> 'PORT' in sshd_config
       True
       >>> 'AddressFamily' in sshd_config
       False
       >>> sshd_config['port']
       ['22', '22']
       >>> sshd_config['Protocol']
       ['1']
       >>> [line for line in sshd_config if line.keyword == 'Port']
       [KeyValue(keyword='Port', value='22', kw_lower='port'), KeyValue(keyword='Port', value='22', kw_lower='port')]
       >>> sshd_config.last('ListenAddress')
       '10.110.1.1'
   """
   from collections import namedtuple
   from .. import Mapper, mapper, get_active_lines


   @mapper('sshd_config')
   class SshDConfig(Mapper):
       """Parsing for ``sshd_config`` file.

       Attributes:
           lines (list): List of `KeyValue` namedtupules for each line in
               the configuration file.
           keywords (set): Set of keywords present in the configuration
               file, each keyword has been converted to lowercase.
       """

       KeyValue = namedtuple('KeyValue', ['keyword', 'value', 'kw_lower'])
       """namedtuple: Represent name value pair as a namedtuple with case ."""

       def parse_content(self, content):
           self.lines = []
           for line in get_active_lines(content):
               kw, val = line.split(None, 1)
               self.lines.append(self.KeyValue(kw.strip(), val.strip(), kw.lower().strip()))
           self.keywords = set([k.kw_lower for k in self.lines])

       def __contains__(self, keyword):
           return keyword.lower() in self.keywords

       def __iter__(self):
           for line in self.lines:
               yield line

       def __getitem__(self, keyword):
           kw = keyword.lower()
           if kw in self.keywords:
               return [kv.value for kv in self.lines if kv.kw_lower == kw]

       def last(self, keyword):
           """str: Returns the value of the last keyword found in config."""
           entries = self.__getitem__(keyword)
           if entries:
               return entries[-1]


   if __name__ == '__main__':
       import doctest
       doctest.testmod()

Mapper Testing
--------------

It is important that we ensure our tests will run successfully after any change
to our mapper. We are able to do that in two ways, first by running ``doctest``
to test our *Examples* section of the ``ssh`` module, and second by running
``pytest``.

``doctest`` is implemented by including the following lines in our module::

   if __name__ == '__main__':
       import doctest
       doctest.testmod()

To execute the ``doctest`` use the following command::

    $ python -m falafel.mappers.ssh

If no errors are displayed then ``doctest`` was successful. To run
``pytest`` on just the ``ssh`` mapper execute the following command::

    $ py.test -k test_ssh

You should also run all tests by executing the following command::

    $ py.test

Once your tests all run successfully your mapper is complete.

*******************
Reducer Development
*******************

TODO: write this section

################
Rule Development
################

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

The following instructions assume that you have a falafel development
environment setup and working, and that your rules root dir and falafel
root dir a subdirs of the same root dir.  First you will need to run
a command that is in your falafel environment to create a new rules
development developmentdirectory.  The following commands will create a new
``myrules`` project for development of your new rule.  Make sure
you start with your virtual environment set to the falafel project::

    $ cd falafel
    $ source bin/activate
    (falafel) $ cd ..
    (falafel) $ mkdir myrules
    (falafel) $ cd myrules
    (falafel) $ falafel-scaffold myrules
    (falafel) $ ls -R
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

    (falafel) $ deactivate
    $ python setup.py bootstrap
    running bootstrap
    New python executable in /home/bfahr/work/insights/myrules/bin/python2
    Also creating executable in /home/bfahr/work/insights/myrules/bin/python
    Installing setuptools, pip, wheel...done.
    Obtaining file:///home/bfahr/work/insights/myrules
    Collecting falafel (from Myrules==0.0.1)
    Collecting coverage (from Myrules==0.0.1)
    Collecting pytest (from Myrules==0.0.1)
      Using cached pytest-3.0.3-py2.py3-none-any.whl
    Collecting pytest-cov (from Myrules==0.0.1)
      Using cached pytest_cov-2.4.0-py2.py3-none-any.whl
    Collecting py>=1.4.29 (from pytest->Myrules==0.0.1)
      Using cached py-1.4.31-py2.py3-none-any.whl
    Installing collected packages: falafel, coverage, py, pytest, pytest-cov, Myrules
      Running setup.py develop for Myrules
    Successfully installed Myrules coverage-4.2 falafel-0.3.5 py-1.4.31 pytest-3.0.3 pytest-cov-2.4.0

The last step in setting up your virtual environment is to enable
your virtual environment and install your local development copy of
the falafel project::

    $ source bin/activate
    (myrules) $ pip install -e ../falafel/
    Obtaining file:///home/bfahr/work/insights/falafel
    Collecting pyyaml (from falafel==1.13.0)
    Installing collected packages: pyyaml, falafel
      Found existing installation: falafel 0.3.5
        Uninstalling falafel-0.3.5:
          Successfully uninstalled falafel-0.3.5
      Running setup.py develop for falafel
    Successfully installed falafel pyyaml-3.12

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

   from falafel.core.plugins import make_response, reducer
   from falafel.mappers.ssh import SshDConfig

   ERROR_KEY = "SSHD_SECURE"


   @reducer(requires=[SshDConfig])
   def report(local, shared):
       sshd_config = shared[SshDConfig]
       """
       1. Evalute config file facts
       2. Evaluate version facts
       """
       if results_found:
           return make_response(ERROR_KEY, results=the_results)

First we import the falafel methods ``make_response()`` for creating
a response and ``reducer()`` to decorate our rule method so that it
will be invoked by falafel with the appropriate mapper information.
Then we import the mappers that provide the facts we need.

.. code-block:: python
   :linenos:

   from falafel.core.plugins import make_response, reducer
   from falafel.mappers.ssh import SshDConfig

Next we define a unique error key string, ``ERROR_KEY`` that will be
collected by falafel when our rule is executed, and provided in the results for
all rules.  This string must be unique among all of your rules, or
the last rule to execute will overwrite any results from other rules
with the same key.

.. code-block:: python
   :linenos:
   :lineno-start: 4

   ERROR_KEY = "SSHD_SECURE"

The ``@reducer()`` decorator is used to mark the rule method that will be
invoked by falafel.  Arguments to ``@reducer()`` are listed in the
following table.

========  =======  ==================================================
Arg Name  Type     Description
========  =======  ==================================================
required  list     List of required shared mappers, it may include
                   an embedded list meaning any one in the list is
                   sufficient.
optional  list     List of options shared mappers.
cluster   boolean  Flag indicating whether this reducer handles
                   Satellite clusters.
========  =======  ==================================================

Our rule requires one shared mapper ``SshDConfig``.  We will add a
requirement to obtain facts about installed RPMs in the final code.

.. code-block:: python
   :linenos:
   :lineno-start: 7

   @reducer(requires=[SshDConfig])

The name of our
rule method is ``report``, but the name may be any valid method name.
The purpose of the method is to access the mapper facts stored
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
and for the OpenSSH version.  The ``SshDConfig`` mapper we developed
will provide
the facts for ``sshd_config`` and we can use another mapper,
``InstalledRpms`` to help us determine facts about installed software.

Here is our updated rule with check for the configuration options and
the software version:

.. code-block:: python
   :linenos:

   from falafel.core.plugins import make_response, reducer
   from falafel.mappers.ssh import SshDConfig
   from falafel.mappers.installed_rpms import InstalledRpms

   ERROR_KEY = "SSHD_SECURE"


   @reducer(requires=[InstalledRpms, SshDConfig])
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
if errors are found, the ``InstalledRpms`` mapper facts are queried to determine
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
in a simulated falafel environment.  This will be easier to understand
by viewing the test code:

.. code-block:: python
   :linenos:

   from myrules.plugins import sshd_secure
   from falafel.tests import InputData, archive_provider, context_wrap
   from falafel.core.plugins import make_response
   # The following imports are not necessary for integration tests
   from falafel.mappers.ssh import SshDConfig
   from falafel.mappers.installed_rpms import InstalledRpms

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
is a ``dict`` object, and it need keys for each mapper that we
require in our rule, here ``SshDConfig`` and ``InstalledRpms``.
This looks very similar to our mapper test code except that 
we may have to support multiple mappers.  We invoke our 
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

Integration tests are performed within the falafel framework.  The
``InputData`` class is used to define the raw data that we want to be
present, and the framework creates an archive file to be input to
the falafel framework so that the mappers will be invoked, and then
the rules will be invoked.  You need to create ``InputData`` objects
will all of the information that is necessary for mappers required
by your rules.  If input data is not present then mappers will not be
executed, and if your rule requires any of those mappers, your rule.

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
.. _Falafel Repository: https://github.com/ansible/falafel
.. _Mozilla OpenSSH Security Guidelines: https://wiki.mozilla.org/Security/Guidelines/OpenSSH
