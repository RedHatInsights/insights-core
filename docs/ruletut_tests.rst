Develop Tests
=============

Start out by creating a ``test_heartburn``.py module in a ``tests`` package.

.. code-block:: shell

    $ mkdir tutorial/tests
    $ touch tutorial/tests/__init__.py
    $ touch tutorial/tests/test_heartburn.py

Open ``test_heartburn.py`` in your text editor of choice and start by stubbing
out a test and the required imports.

.. code-block:: python
   :linenos:

    from insights.specs import Specs
    from insights.specs import InputData, archive_provider
    from insights import make_response

    from tutorial import heartburn

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

    from insights.specs import Specs
    from insights.specs import InputData, archive_provider
    from insights import make_response

    from tutorial import heartburn

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
