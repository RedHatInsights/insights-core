.. _tutorial-parser-development:

******************
Parser Development
******************

The purpose of a Parser is to process raw content collected by the Client
and map it
into a format that is usable by Combiners and Rules.  Raw content
is content obtained directly from a system file or command, and
may collected by Insights Client, or from some other source such
as a SOS Report.  The following examples will demonstrate development of
different types of parsers.

Preparing Your Development Environment
======================================

First you need to create your own fork of the insights-core project.  Do this by
going to the `insights-core Repository`_ on github and clicking on the
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
    [bfahr@bfahrvm2 work]$ git clone git@github.com:bfahr/insights-core.git
    Cloning into 'insights-core'...
    remote: Counting objects: 5665, done.
    remote: Compressing objects: 100% (1716/1716), done.
    remote: Total 5665 (delta 4043), reused 5378 (delta 3890)
    Receiving objects: 100% (5665/5665), 1.62 MiB | 292.00 KiB/s, done.
    Resolving deltas: 100% (4043/4043), done.

Next you need to follow the steps documented in the file ``insights-core/readme.md``
to create a virtual environment and set it up for development::

    [bfahr@bfahrvm2 work]$ cd insights-core
    [bfahr@bfahrvm2 insights-core]$ virtualenv .
    New python executable in ./bin/python
    Installing Setuptools..................................................done.
    Installing Pip....................................................done.
    [bfahr@bfahrvm2 insights-core]$ source bin/activate
    (insights-core)[bfahr@bfahrvm2 insights-core]$ pip install -e .[develop]

Once these steps have been completed you will have a complete development
environment for parsers and combiners.  You can confirm that everything is setup
correctly by running the tests, ``py.test``.  Your results should look
something like this::

    (insights-core)[bfahr@bfahrvm2 insights-core]$ py.test
    ======================== test session starts =============================
    platform linux2 -- Python 2.7.5, pytest-3.0.3, py-1.4.31, pluggy-0.4.0
    rootdir: /home/bfahr/work/insights-core, inifile: setup.cfg
    plugins: cov-2.4.0
    collected 414 items

    insights/console/tests/test_package_installed_package.py ......
    [leaving out a long list of test names]
    insights/web/tests/test_urls.py .
    ====================== short test summary info ===========================
    XFAIL insights/parsers/tests/test_installed_rpms.py::test_max_min_kernel
      Incorrect implementation

    =============== 413 passed, 1 xfailed in 3.81 seconds ====================

Your development environment is now ready to begin development and you may move
on to the next section.  If you had problems with any of these steps then
double check that you have completed all of the steps in order and if it still
doesn't work, open a `Github issue <https://github.com/RedHatInsights/insights-core/issues/new>`_.

Secure Shell Parser
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
by space and then a configuration value.  So in the parser we want to make sure
we capture the important lines and ignore the comments and blank lines.

Creating the Initial Parser Files
---------------------------------

First we need to create the parser file.  Parser files are implemented in modules.
The module should be limited to one type of applications.  In this case we are
working with ``ssh`` applications so we will create an ``ssh`` module.  Create
the module file ``insights/parsers/ssh.py`` in the parsers directory::

    $ touch insights/parsers/ssh.py

Now edit the file and create the parser skeleton:

.. code-block:: python
    :linenos:

    from .. import Parser, parser


    @parser('sshd_config')
    class SshDConfig(Parser):

        def parse_content(self, content):
            pass

We start by importing the ``Parser`` class and the ``parser`` decorator.  Our
parser will inherit from the ``Parser`` class and it will be associated with
the ``sshd_config`` input data using the ``parser`` decorator. Finally we
need to implement the ``parse_content`` subroutine which is required to parse
store the input data in our class.  The base class ``Parser`` implements a
constructor that will invoke our ``parse_content`` method when the class
is created.

.. note:: The ``from .. import`` here is equivalent to
       ``from insights.parsers import`` and is implemented by some *magic*
       code elsewhere to help minimize changes to all parsers if the project
       name changes.

Next we'll create the parser test file ``insights/parsers/tests/test_ssh.py``
as a skeleton that will aid in the parser development process:

.. code-block:: python
    :linenos:

    from insights.parsers.ssh import SshDConfig


    def test_sshd_config():
        pass

Once you have created and saved both of these files and we'll run the test
to make sure everything is setup correctly:

.. code-block:: bash
    :linenos:

    (insights-core)[bfahr@bfahrvm2 insights-core]$ py.test -k test_ssh
    ================== test session starts ========================
    platform linux2 -- Python 2.7.5, pytest-3.0.3, py-1.4.31, pluggy-0.4.0
    rootdir: /home/bfahr/work/insights-core, inifile: setup.cfg
    plugins: cov-2.4.0
    collected 415 items

    insights/parsers/tests/test_ssh.py .

    ================== 414 tests deselected =======================
    ========= 1 passed, 414 deselected in 0.46 seconds ============

When you invoke ``py.test`` with the ``-k`` option it will only run tests
which match the filter, in this case tests that match *test_ssh*.  So our
test passed as expected.

.. hint:: You may sometimes see a message that ``py.test`` cannot be found,
       or see some other related message that doesn't make sense. The first
       think to check is that you have activated your virtual environment by
       executing the command ``source bin/activate`` from the root directory
       of your project.  You prompt should change to include ``(insights-core)`` if
       your virtual enviroment is activated. You can deactivate the virtual
       environment by typing ``deactivate``. You can find more information
       about virtual environments here:
       http://docs.python-guide.org/en/latest/dev/virtualenvs/

Parser Implementation
---------------------

Typically parser and combiner development is driven by rules that need facts
generated by the parsers and combiners.  Regardless of the specific
requirements, it is important (1) to implement basic functionality by getting
the raw data into a usable format, and (2) to not overdo the implementation
because we can't anticipate every use of the parser output.  In our example
we will eventually be implementing the rules that will warn us about systems
that are not configured properly. Initially our parser implementation will
be parsing the input data into key/value pairs.  We may later discover that
we can optimize rules by moving duplicate or complex processing into the parser.

Test Code
^^^^^^^^^

Referring back to our :ref:`sample SSHD input <sample-sshd-input>` we will
start by creating a test for the output that we want from our parser:

.. code-block:: python
   :linenos:

   from insights.parsers.ssh import SshDConfig
   from insights.tests import context_wrap

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
   """


   def test_sshd_config():
       sshd_config = SshDConfig(context_wrap(SSHD_CONFIG_INPUT))
       assert sshd_config is not None
       assert 'Port' in sshd_config
       assert 'PORT' in sshd_config
       assert sshd_config['port'] == ['22', '22']
       assert 'ListenAddress' in sshd_config
       assert sshd_config['ListenAddress'] == ['10.110.0.1', '10.110.1.1']
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

   from insights.parsers.ssh import SshDConfig
   from insights.tests import context_wrap

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
   """

Next, to the body of the test, we add code to create an instance of our
parser class:


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

Parser Code
^^^^^^^^^^^

The subroutine ``parse_content`` is responsible for parsing the input data and
storing the results in class attributes.  You may choose the attributes that
are necessary for your parser, there are no requirements to use specific names
or types.  Some general recommendations for parser class implementation are:

* Choose attributes that make sense for use by actual rules, or how you
  anticipate rules to use the information. If rules need to iterate over
  the information then a ``list`` might be best, or if rules could access
  via keywords then ``dict`` might be better.
* Choose attribute types that are not so complex they cannot be easily
  understood or serialized.  Unless you know you need something complex
  keep it simple.
* Use the ``@property`` decorator to create readonly getters and simplify
  access to information.

Now we need to implement the parser that will satisify our tests.

.. code-block:: python
   :linenos:

    from collections import namedtuple
    from .. import Parser, parser, get_active_lines


    @parser('sshd_config')
    class SshDConfig(Parser):

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
that you can find in ``insights/parsers/__init__.py``, ``insights/core/__init__.py``,
and ``insights/util/__init__.py``.  ``get_active_lines()`` will remove all
blank lines and comments from the input which simplifies your parsers
parsing logic.

.. code-block:: python
   :linenos:

    from collections import namedtuple
    from .. import Parser, parser, get_active_lines

We can use ``namedtuples`` to help simplify access to the information we
are storing in our parser by creating a namedtuple with the named attributes
``keyword``, ``value``, and ``kw_lower`` where *kw_lower* is the lowercase
version of the *keyword*.

.. code-block:: python
   :linenos:
   :lineno-start: 8

        KeyValue = namedtuple('KeyValue', ['keyword', 'value', 'kw_lower'])

In this particular parser we have chosen to store all lines (``self.lines``)
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

We now have a complete implementation of our parser.  It could certainly
perform further analysis of the data and more methods for access, but
it is better keep the parser simple in the beginning.  Once it is in
use by rules it will be easy to add functionality to the parser to
allow simplification of the rules.

Parser Documentation
--------------------

The last step to complete implementation of our parser is to create
the documentation.  The guidelines and examples for parser documentation is
provided in the section :doc:`docs_guidelines`.

The following shows our completed parser including documentation.

.. code-block:: python
   :linenos:

    """
    ssh - Files for configuration of `ssh`
    ======================================

    The ``ssh`` module provides parsing for the ``sshd_config``
    file.  The ``SshDConfig`` class implements the parsing and
    provides a ``list`` of all configuration lines present in
    the file.

    Sample content from the ``/etc/sshd/sshd_config`` file is::

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

    Examples:
        >>> sshd_config = shared[SshDConfig]
        >>> 'Port' in sshd_config
        True
        >>> 'PORT' in sshd_config  # items are stored case-insentive
        True
        >>> 'AddressFamily' in sshd_config  # comments are ignored
        False
        >>> sshd_config['port']  # All value stored by keyword in lists
        ['22', '22']
        >>> sshd_config['Protocol']  # Single items have one list element
        ['1']
        >>> [line for line in sshd_config if line.keyword == 'Port']  # can be used as an iterator
        [KeyValue(keyword='Port', value='22', kw_lower='port'), KeyValue(keyword='Port', value='22', kw_lower='port')]
        >>> sshd_config.last('ListenAddress')  # Easy way of finding the current configuration for a single item
        '10.110.1.1'
    """
    from collections import namedtuple
    from .. import Parser, parser, get_active_lines


    @parser('sshd_config')
    class SshDConfig(Parser):
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
                kw, val = (w.strip() for w in line.split(None, 1))
                self.lines.append(self.KeyValue(kw, val, kw.lower()))
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

Parser Testing
--------------

It is important that we ensure our tests will run successfully after any
change to our parser. We are able to do that in two ways, first by using
``doctest`` to test our *Examples* section of the ``ssh`` module, and second
by writing tests that can be tested automatically using ``pytest``.  Starting
with adding ``import doctest`` our original code:

.. code-block:: python
    :linenos:

    from insights.parsers import ssh
    from insights.tests import context_wrap
    import doctest

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
    """

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

To test the documentation, we can then use ``doctest``:

.. code-block:: python
    :linenos:
    :lineno-start: 35

    def test_sshd_documentation():
        """
        Here we test the examples in the documentation automatically using
        doctest.  We set up an environment which is similar to what a
        rule writer might see - a 'shared' object that stores parser
        objects by class.  This saves doing this setup in the example code.
        """
        env = {
            'SshDConfig': ssh.SshDConfig,
            'shared': {
                ssh.SshDConfig: ssh.SshDConfig(context_wrap(SSHD_CONFIG_INPUT)),
            }
        }
        failed, total = doctest.testmod(ssh, globs=env)
        assert failed == 0

The environment setup allows us to 'hide' the set-up of the environment that
normally provided to the rule, which is the context in which the example
code is written.  This must provide both a name for the parser class, as if
it had been imported by the rule, and the 'shared' dictionary with a
reference, by class, to the object created by parsing the sample input.

The ``assert`` line here makes sure that any failures in the examples are
detected by pytest.  This will also include the testing output from doctest,
showing where the code failed to evaluate or where the output differed from
what was given.

Because this code essentially duplicates many of the things previously
tested explicitly in the ``test_sshd_config`` function, we can remove some
of those tests and only test the 'corner cases':

.. code-block:: python
    :linenos:
    :lineno-start: 51

    def test_sshd_corner_cases():
        """
        Here we test any corner cases for behaviour we expect to deal with
        in the parser but doesn't make a good example.
        """
        config = ssh.SshDConfig(context_wrap(SSHD_DOCS_EXAMPLE))
        assert config.last('AddressFamily') is None
        assert config['AddressFamily'] is None
        ports = [l for l in config if l.keyword == 'Port']
        assert len(ports) == 2
        assert ports[0].value == '22'


To run ``pytest`` on just the ``ssh`` parser execute the following command::

    $ py.test -k test_ssh

You should also run all tests by executing the following command::

    $ py.test

You can also check how well your tests cover all the paths in the code
using the following command::

    $ py.test insights/parsers --cov=insights/parsers

Once your tests all run successfully your parser is complete.

.. --------------------------------------------------------------------
.. Put all of the references that are used throughout the document here
.. Links:

.. _Red Hat Customer Portal: https://access.redhat.com
.. _Red Hat Insights Portal: https://access.redhat.com/products/red-hat-insights.
.. _insights-core Repository: https://github.com/RedHatInsights/insights-core
.. _Mozilla OpenSSH Security Guidelines: https://wiki.mozilla.org/Security/Guidelines/OpenSSH
