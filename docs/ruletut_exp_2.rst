**************************************************
Example Rule-2: Heartburn CVE Rule Using Condition
**************************************************

The most effective way to get started in developing a rule is identifying the
problem you want to address as well as a succinct solution to that problem.

You can find the complete implementation of the rule and test code in the
directory ``insights/docs/examples/rules``.

Determine Rule Logic
====================

For the example rule2, we'll identify a fictitious security problem
with a commonly shared library.  Let's imagine that this is a highly publicized
CVE, and, therefore, it deserves a catchy name; let's call it Heartburn.

For this case let's check three things:

1. The shared library is installed on the system
2. The shared library is in use by a running process
3. The running process is accepting possibly network connections

For this problem let's declare that the solution is to upgrade the shared
library and restart the system.


Identify Parsers
================

- For RPM-based distributions, we can identify the installed version of the
  library by using the ``InstalledRpms`` parser.

- We can use the ``Lsof`` parser to identify if a running process is using the
  shared library.

- We can use the ``Netstat`` parser to identify if a running process is
  possibly listening on any connections.

Develop Plugin Code
===================

Now that we have identified the required parsers, let's get started on
developing our plugin.

Create a file called ``heartburn.py`` in a Python package called ``mycomponents``.

.. code-block:: shell

   [userone@hostone work]$ pwd
   /home/userone/work
   [userone@hostone work]$ ls
   insights-core mycomponents
   [userone@hostone work]$ cd mycomponents
   [userone@hostone mycomponents]$ touch rules/heartburn.py

Open ``heartburn.py`` in your text editor of choice and start by stubbing out
the rule function and imports.

.. code-block:: python
   :linenos:

   from insights.parsers.installed_rpms import InstalledRpms
   from insights.parsers.lsof import Lsof
   from insights.parsers.netstat import Netstat
   from insights import condition, rule, make_response

   @condition(InstalledRpms)
   def is_library_installed(installed_rpms):
       pass

   @condition(Lsof)
   def in_use_processes(lsof):
       pass

   @condition(Netstat)
   def listening_processes(netstat):
       pass

   @rule(is_library_installed, in_use_processes, listening_processes)
   def heartburn(pkg, in_use, listening):
       pass

Let's go over each line and describe the details:

.. code-block:: python
   :lineno-start: 1

   from insights.parsers.installed_rpms import InstalledRpms
   from insights.parsers.lsof import Lsof
   from insights.parsers.netstat import Netstat

Parsers you want to use must be imported.  You must pass the parser class
objects directly to the ``@condition`` decorator to declare them as dependencies for
your rule.

.. code-block:: python
   :lineno-start: 4

   from insights import condition, rule, make_response

``condition`` and ``rule`` are function decorator used to specify your main
plugin function.  Combiners have a set of optional dependencies that are
specified via the ``requires`` kwarg.

``make_response`` is a formatting function used to format
the `return value of a rule </api.html#rule-output>`_ function.

.. code-block:: python
   :lineno-start: 6

   @condition(InstalledRpms)
   def is_library_installed(installed_rpms):

.. code-block:: python
   :lineno-start: 10

   @condition(Lsof)
   def in_use_processes(lsof):

.. code-block:: python
   :lineno-start: 14

   @condition(Netstat)
   def listening_processes(netstat):

.. code-block:: python
   :lineno-start: 18

   @rule(is_library_installed, in_use_processes, listening_processes)
   def heartburn(pkg, in_use, listening):

Here we are specifying that this rule requires the output of the
``InstalledRpms``, ``Lsof``, and ``Netstat`` parsers.

Now let's add the logic for each ``condition`` at first:

.. code-block:: python
   :lineno-start: 6

   @condition(InstalledRpms)
   def is_library_installed(installed_rpms):
       # If not installed, returns False. Therefore not applicable
       return 'shared-library-1.0.0' in installed_rpms

   Lsof.collect_keys('libshared_procs', NAME='usr/lib64/libshared.so.1')

   @condition(Lsof)
   def in_use_processes(lsof):
       pids = []
       for p in lsof.libshared_procs:
           pids.append(p['PID'])
       return pids

   @condition(Netstat)
   def listening_processes(netstat):
       return netstat.listening_pid.keys()

There's a lot going on here, so lets look at some of the steps in detail.

.. code-block:: python
   :lineno-start: 8

       # If not installed, returns False. Therefore not applicable
       return 'shared-library-1.0.0' in installed_rpms

The
:py:class:`insights.parsers.installed_rpms.InstalledRpms` parser defines a
``__contains__`` method that allows for simple searching of rpms by name.

.. code-block:: python
   :lineno-start: 11

   Lsof.collect_keys('libshared_procs', NAME='usr/lib64/libshared.so.1')

   @condition(Lsof)
   def in_use_processes(lsof):
       pids = []
       for p in lsof.libshared_procs:
           pids.append(p['PID'])
       return pids

The :py:class:`insights.parsers.lsof.Lsof` parser provides a ``collect_keys``
method that will generate an attribute that will return a list of pid numbers
that have the given file open.

.. code-block:: python
   :lineno-start: 22

       return netstat.listening_pid.keys()

The :py:class:`insights.parsers.netstat.Netstat` parser provides a
``listening_pid`` property that returns a dictionary of all pid numbers that
are bound to all LISTEN processes.

.. code-block:: python
   :lineno-start: 24

   @rule(is_library_installed, in_use_processes, listening_processes)
   def heartburn(pkg, in_use, listening):
       if pkg and in_use and listening:

           # get the set of processes that are using the library and listening
           vulnerable_processes = set(in_use) & set(listening)

           if vulnerable_processes:
               return make_response("YOU_HAVE_HEARTBURN",
                                    listening_pids=vulnerable_processes)

Here, the name of this rule method is ``heartburn``, but the name may be any
valid method name. It will combine the results of each ``@condition`` and check
to see if there were any processes that were using the library and might be
bound to an connection.  If any such processes were found we are returning a
result with the error key of ``YOU_HAVE_HEARTBURN``.  This error key can be
referenced by other systems for display or tracking purposes.

Here is the complete rule code with the combined check:

.. code-block:: python
   :linenos:

   from insights.parsers.installed_rpms import InstalledRpms
   from insights.parsers.lsof import Lsof
   from insights.parsers.netstat import Netstat
   from insights import condition, rule, make_response

   @condition(InstalledRpms)
   def is_library_installed(installed_rpms):
       # If not installed, returns False. Therefore not applicable
       return 'shared-library-1.0.0' in installed_rpms

   Lsof.collect_keys('libshared_procs', NAME='usr/lib64/libshared.so.1')

   @condition(Lsof)
   def in_use_processes(lsof):
       pids = []
       for p in lsof.libshared_procs:
           pids.append(p['PID'])
       return pids

   @condition(Netstat)
   def listening_processes(netstat):
       return netstat.listening_pid.keys()

   @rule(is_library_installed, in_use_processes, listening_processes)
   def heartburn(pkg, in_use, listening):
       if pkg and in_use and listening:

           # get the set of processes that are using the library and listening
           vulnerable_processes = set(in_use) & set(listening)

           if vulnerable_processes:
               return make_response("YOU_HAVE_HEARTBURN",
                                    listening_pids=vulnerable_processes)

Develop Tests
=============

Start out by creating a ``test_heartburn``.py module in a ``tests`` package.

.. code-block:: shell

   [userone@hostone work]$ pwd
   /home/userone/work/mycomponents
   [userone@hostone work]$ cd mycomponents
   [userone@hostone mycomponents]$ ls
   parsers rules tests
   [userone@hostone mycomponents]$ touch tests/__init__.py
   [userone@hostone mycomponents]$ touch tests/test_heartburn.py

Open ``test_heartburn.py`` in your text editor of choice and start by stubbing
out a test and the required imports.

.. code-block:: python
   :linenos:

   from rules import heartburn
   from insights.specs import Specs
   from insights.tests import InputData, archive_provider
   from insights.core.plugins import make_response

   @archive_provider(heartburn.heartburn)
   def integration_test():
       pass

The framework provides an integration test framework that allows you to define
an ``InputData`` object filled with raw examples of files required by your rule
and an expected response.  The object is evaluated by the pipeline as it would
be in a production context, after which the response is compared to your
expected output.

The ``@archive_provider`` decorator registers your test function with the
framework.  This function must be a generator that yields ``InputData`` and an
expected response in a two tuple.  The ``@archive_provider`` decorator takes
one parameter, the rule function to test.

The bulk of the work in building a test for a rule is in defining the
``InputData`` object.  If you remember our rule we accept ``Lsof``,
``InstalledRpms``, and ``Netstat``.  We will define a snippet for each.

.. code-block:: python

   LSOF_EXAMPLE = """
   COMMAND     PID   TID      USER    FD  TYPE    DEVICE  SIZE/OFF       NODE    NAME
   sshd       1304     0   example   mem   REG     253,2    255888   10130663    /usr/lib64/libssl3.so
   """.strip()

   NETSTAT_TEXT = """
   Active Internet connections (servers and established)
   Proto Recv-Q Send-Q Local Address               Foreign Address             State       User       Inode      PID/Program name    Timer
   tcp        0      0 0.0.0.0:322                 0.0.0.0:*                   LISTEN      0          13044      23041/irrelevant    off (0.00/0/0)
   tcp        0      0 127.0.0.1:22                0.0.0.0:*                   LISTEN      0          30419      21968/sshd          off (0.00/0/0)
   Active UNIX domain sockets (servers and established)
   Proto RefCnt Flags       Type       State         I-Node PID/Program name    Path
   unix  2      [ ACC ]     STREAM     LISTENING     17911  4220/multipathd     /var/run/multipathd.sock
   """.strip()

   INSTALLED_RPMS = """
   xz-libs-4.999.9-0.3.beta.20091007git.el6.x86_64             Thu 22 Aug 2013 03:59:09 PM HKT
   openssl-static-1.0.1e-16.el6_5.1.x86_64                     Thu 22 Aug 2013 03:59:09 PM HKT
   rootfiles-8.1-6.1.el6.noarch                                Thu 22 Aug 2013 04:01:12 PM HKT
   """.strip()


Next we need to build ``InputData`` objects and populate it with the content.

.. code-block:: python

   input_data = InputData("test_one")
   input_data.add(Specs.lsof, LSOF_EXAMPLE)
   input_data.add(Specs.installed_rpms, INSTALLED_RPMS)
   input_data.add(Specs.netstat, NETSTAT_TEXT)

Next we need to build the expected return.

.. code-block:: python

   expected = make_response("YOU_HAVE_HEARTBURN", listening_pids=[1304])

And finally we need to yield the pair.

.. code-block:: python

   yield input_data, expected

Now for the entire test:

.. code-block:: python
   :linenos:

   from rules import heartburn
   from insights.specs import Specs
   from insights.tests import InputData, archive_provider
   from insights.core.plugins import make_response

   LSOF_EXAMPLE = """
   COMMAND     PID   TID      USER    FD  TYPE    DEVICE  SIZE/OFF       NODE    NAME
   sshd       1304     0   example   mem   REG     253,2    255888   10130663    /usr/lib64/libssl3.so
   """.strip()

   NETSTAT_TEXT = """
   Active Internet connections (servers and established)
   Proto Recv-Q Send-Q Local Address               Foreign Address             State       User       Inode      PID/Program name    Timer
   tcp        0      0 0.0.0.0:322                 0.0.0.0:*                   LISTEN      0          13044      23041/irrelevant    off (0.00/0/0)
   tcp        0      0 127.0.0.1:22                0.0.0.0:*                   LISTEN      0          30419      21968/sshd          off (0.00/0/0)
   Active UNIX domain sockets (servers and established)
   Proto RefCnt Flags       Type       State         I-Node PID/Program name    Path
   unix  2      [ ACC ]     STREAM     LISTENING     17911  4220/multipathd     /var/run/multipathd.sock
   """.strip()

   INSTALLED_RPMS = """
   xz-libs-4.999.9-0.3.beta.20091007git.el6.x86_64             Thu 22 Aug 2013 03:59:09 PM HKT
   openssl-static-1.0.1e-16.el6_5.1.x86_64                     Thu 22 Aug 2013 03:59:09 PM HKT
   rootfiles-8.1-6.1.el6.noarch                                Thu 22 Aug 2013 04:01:12 PM HKT
   """.strip()


   @archive_provider(heartburn.heartburn)
   def integration_test():
       input_data = InputData("test_one")
       input_data.add(Specs.lsof, LSOF_EXAMPLE)
       input_data.add(Specs.installed_rpms, INSTALLED_RPMS)
       input_data.add(Specs.netstat, NETSTAT_TEXT)

       expected = make_response("YOU_HAVE_HEARTBURN", listening_pids=[1304])

       yield input_data, expected

Keep in mind that the above is a minimal _positive_ test and that covering as
many situations as possible can be very valuable.  If you wish to test a case
where you do _not_ expect a response create the appropriate ``InputData`` and
yield it along with ``None``.  To illustrate the point let's simply remove a
required piece of information, ``InstalledRpms``.

.. code-block:: python

   input_data = InputData("test_two")
   input_data.add(Specs.lsof, LSOF_EXAMPLE)
   input_data.add(Specs.netstat, NETSTAT_TEXT)

   yield input_data, None
