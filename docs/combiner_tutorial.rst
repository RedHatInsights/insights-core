.. _tutorial-combiner-development:

###############################
Tutorial - Combiner Development
###############################

********************
Combiner Development
********************
In the Map-Reduce model, Parsers are responsible for mapping the data from a
datasource and Combiners are responsible for reducing the data from multiple
Parsers into a reduced dataset.  Combiners help to consolidate information from
different data sources, hide differences between the same data source across
operating system versions, and make Parser output more rule friendly. 

For example, the *hostname* of a system may be obtained from the ``Hostname``,
``Facter``, and ``SystemID`` parsers.  A rule could rely on all three parsers
and might need to process each one differently depending upon which was present.
However, a rule could instead simply rely on the ``hostname`` combiner which
does the job of evaluating all of the parser data and determining the best
source of *hostname*, greatly simplifying logic in the rule.

Another example is the ``GrubConf`` combiner which evaluates multiple versions
(1, 2, non-EFI, EFI) Grub configuration data to provide one consolidated source
of information for Grub configuration on a system.

You can find the complete implementation of the combiner and test code in the
directory ``insights/docs/examples/combiners``.

Preparing Your Development Environment
======================================

We will use the same development environment that is necessary for Parser
Development which is described in :ref:`parser-development-environment`.

Hostname Combiner
=================

Overview
--------

For this tutorial we will create a new *hostname* combiner that will consolidate
information from the :py:class:`insights.parsers.uname.Uname` and
:py:class:`insights.parsers.hostname.Hostname` parsers.  There is an existing
:py:class:`insights.combiners.hostname.Hostname` combiner so we will call ours
``HostnameUH`` to avoid confusion.

Creating the Initial Combiner Files
-----------------------------------

First we need to create the combiner file.  Combiner files are implemented in
modules. The module should be limited to one purpose.  In this case we are
working with ``hostname`` data so we will create an ``hostname_uh`` module.
Also there is already a ``hostname`` combiner module so we want to avoid 
confusion.  Create the module file ``insights/combiners/hostname_uh.py`` in the
combiners directory::

    (insights-core)[userone@hostone insights-core]$ touch insights/combiners/hostname_uh.py

Now edit the file and create the combiner skeleton:

.. code-block:: python
    :linenos:

    from insights.core.plugins import combiner
    from insights.parsers.hostname import Hostname
    from insights.parsers.uname import Uname


    @combiner([Hostname, Uname])
    class HostnameUH(object):
        
        def __init__(self, hostname, uname):
            pass

We start by importing the ``combiner`` decorator.  As discussed above our
combiner will depend upon the ``Hostname`` and ``Uname`` parsers and these
are imported and included as arguments to the ``combiner`` decorator.  Notice
that the decorator arguments are in a ``list`` meaning that our combiner
needs at least one of the parsers in the list.  See the discussion of
:ref:`Rule Decorators <rule-decorator>` for more information on *required*,
*at least one*, and *optional* arguments to the combiner decorator.

We also need to pass the parser instance objects as arguments to the ``__init__``
method of our combiner.  If either of these objects is not present then its
value with be ``None``.

Next we'll create the combiner test file ``insights/combiners/tests/test_hostname_uh.py``
as a skeleton that will aid in the combiner development process:

.. code-block:: python
    :linenos:

    from insights.combiners.hostname_uh import HostnameUH


    def test_hostname_uh():
        pass

Once you have created and saved both of these files, you can the test
to make sure everything is setup correctly::

    (insights-core)[userone@hostone insights-core]$ py.test -k hostname_uh
    ======================= test session starts ==============================
    platform linux2 -- Python 2.7.14, pytest-3.0.6, py-1.5.2, pluggy-0.4.0
    rootdir: /home/bfahr/work/insights/insights-core, inifile: setup.cfg
    plugins: cov-2.4.0
    collected 825 items

    insights/combiners/tests/test_hostname_uh.py .

    ====================== 824 tests deselected ==============================
    ============ 1 passed, 824 deselected in 1.02 seconds ====================

When you invoke ``py.test`` with the ``-k`` option it will only run tests
which match the filter, in this case tests that match *hostname_uh*.  So our
test passed as expected.

.. hint:: You may sometimes see a message that ``py.test`` cannot be found,
       or see some other related message that doesn't make sense. The first
       think to check is that you have activated your virtual environment by
       executing the command ``source bin/activate`` from the root directory
       of your insights-core project.  Your prompt should change to include
       ``(insights-core)`` if your virtual environment is activated. You can
       deactivate the virtual environment by typing ``deactivate``. You can
       find more information about virtual environments here:
       http://docs.python-guide.org/en/latest/dev/virtualenvs/

Combiner Implementation
-----------------------

Typically parser and combiner development is driven by rules that need facts
generated by the parsers and combiners.  Regardless of the specific
requirements, it is important (1) to implement basic functionality by getting
the raw data into a usable format, and (2) to not overdo the implementation
because we can't anticipate every use of the combiner output.  In our example
the output is simple, but some combiners can be complicated so keep these
two criteria in mind when developing new parsers or combiners.  You can always
add more capability later on if needed by your rules.

Test Code
^^^^^^^^^

We will start by creating a test for the output that we want from our combiner
using the two input sources.  You can look at the documentation for
:py:mod:`insights.parsers.hostname` and :py:mod:`insights.parsers.uname` to see
what methods will be available.  In our tests we want to ensure that we can
test with the parser object so we'll use input data to feed the parsers and
then use the parsers as input to our combiner tests.

.. code-block:: python
   :linenos:

   from insights.combiners.hostname_uh import HostnameUH
   from insights.parsers.hostname import Hostname
   from insights.parsers.uname import Uname
   from insights.tests import context_wrap

   HOSTNAME = "hostone_h.example.com"
   UNAME = "Linux hostone_u.example.com 3.10.0-693.21.1.el7.x86_64 #1 SMP Fri Feb 23 18:54:16 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux"


   def test_hostname_uh():
       hostname = Hostname(context_wrap(HOSTNAME))
       uname = Uname(context_wrap(UNAME))

       hostname_uh = HostnameUH(hostname, None)
       assert hostname_uh.hostname == HOSTNAME

       hostname_uh = HostnameUH(None, uname)
       assert hostname_uh.hostname == "hostone_u.example.com"

       hostname_uh = HostnameUH(hostname, uname)
       assert hostname_uh.hostname == HOSTNAME


First we added an import for the combiner object and the parser objects.  Next
we import a helper function ``context_wrap`` which we'll
use to create our parser instance objects:

.. code-block:: python
   :linenos:

    from insights.combiners.hostname_uh import HostnameUH
    from insights.parsers.hostname import Hostname
    from insights.parsers.uname import Uname
    from insights.tests import context_wrap

Next we include the sample data that will be used for the test.  We will use
data for input to the parsers so we need both sample outputs of the ``hostname``
command and the ``uname -a`` command:

.. code-block:: python
   :linenos:
   :lineno-start: 6

   HOSTNAME = "hostone_h.example.com"
   UNAME = "Linux hostone_u.example.com 3.10.0-693.21.1.el7.x86_64 #1 SMP Fri Feb 23 18:54:16 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux"

Next, to the body of the test, we add code to create instances of the
necessary parser classes:

.. code-block:: python
   :linenos:
   :lineno-start: 10
   :emphasize-lines: 2,3

   def test_hostname_uh():
       hostname = Hostname(context_wrap(HOSTNAME))
       uname = Uname(context_wrap(UNAME))

Finally we add our tests using the attributes that we want to be able to
access in our rules.  For our combiner we trust ``hostname`` more than
``uname`` so we give ``hostname`` priority by checking it first and then
fall back to ``uname`` if hostname is not available.  If neither of these is
available the combiner will not be called.  It is always guaranteed that our
combiner will get at least one of the parsers when called.

Now here are the tests:

.. code-block:: python
   :linenos:
   :lineno-start: 14

   hostname_uh = HostnameUH(hostname, None)
   assert hostname_uh.hostname == HOSTNAME

   hostname_uh = HostnameUH(None, uname)
   assert hostname_uh.hostname == "hostone_u.example.com"

   hostname_uh = HostnameUH(hostname, uname)
   assert hostname_uh.hostname == HOSTNAME

We use a different hostname in each parser so that we can confirm that the
correct parser data is chosen.

Combiner Code
^^^^^^^^^^^^^

The class ``__init__`` method performs all of the work in our combiner.  If
your combiner is more complex you may need to add additional methods and utility
functions.  Some general recommendations for the combiner class implementation
are:

* Choose attributes that make sense for use by actual rules, or how you
  anticipate rules to use the information. If rules need to iterate over
  the information then a ``list`` might be best, or if rules could access
  via keywords then ``dict`` might be better.
* Choose attribute types that are not so complex they cannot be easily
  understood or serialized.  Unless you know you need something complex
  keep it simple.
* Use the ``@property`` decorator to create read-only getters and simplify
  access to information.

Now we need to implement the combiner that will satisfy our tests.

.. code-block:: python
   :linenos:

   from insights.core.plugins import combiner
   from insights.parsers.hostname import Hostname
   from insights.parsers.uname import Uname


   @combiner([Hostname, Uname])
   class HostnameUH(object):

       def __init__(self, hostname, uname):
           if hostname:
               self.hostname = hostname.fqdn
           else:
               self.hostname = uname.nodename

We've replaced our original ``__init__`` to include the logic for our combiner.
The ``Hostname`` parser is passed in as the ``hostname`` attribute, and if it
is present then we use it to acquire the hostname data.  If ``hostname`` is
``None``, meaning that there was no data or there was some error in the data
for the ``Hostname`` parser, we fall back to use the ``Uname`` parser data
passed in the ``uname`` attribute.

Now save this file and run the tests again to confirm that we have successfully
written our combiner to pass all tests::
    
    (insights-core)[userone@hostone insights-core]$ py.test -k hostname_uh
    ======================= test session starts ==============================
    platform linux2 -- Python 2.7.14, pytest-3.0.6, py-1.5.2, pluggy-0.4.0
    rootdir: /home/bfahr/work/insights/insights-core, inifile: setup.cfg
    plugins: cov-2.4.0
    collected 825 items

    insights/combiners/tests/test_hostname_uh.py .

    ====================== 824 tests deselected ==============================
    ============ 1 passed, 824 deselected in 1.02 seconds ====================

Combiner Documentation and Testing
----------------------------------

The last step to complete implementation of our combiner is to create
the documentation.  The guidelines and examples for combiner documentation is
provided in the section :doc:`docs_guidelines` and parallels the information
provided in the instructions for :ref:`parser-documentation`.  Combiner
testing parallels the information provided in the instructions for the
:ref:`parser-testing`

.. --------------------------------------------------------------------
.. Put all of the references that are used throughout the document here
.. Links:

.. _Red Hat Customer Portal: https://access.redhat.com
.. _Red Hat Insights Portal: https://access.redhat.com/products/red-hat-insights.
.. _insights-core Repository: https://github.com/RedHatInsights/insights-core
.. _Mozilla OpenSSH Security Guidelines: https://wiki.mozilla.org/Security/Guidelines/OpenSSH



