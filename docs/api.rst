############
Insights API
############

Input Data Formats
==================

Before any data reaches the rules framework, it obviously has to be generated.
There are currently several input data formats that can be processed by insights-core:

SOSReports
----------

A SOSReport_ is a command-line tool for Red Hat Enterprise Linux (and other
systems) to collect configuration and diagnostic information from the system.

.. _SOSReport: https://github.com/sos/sosreport

Insights Archives
-----------------

These archives have been designed from the ground up to fit the Insights
use case -- that is, to be automatically uploaded on a daily basis.
This means that the data contained in the archive is exactly what is
required to effectively process all currently-developed rules -- and
nothing more.

In addition, there are several features built in to the
insights-client_ package (which is the tool that creates Insights
archives) to better meet Red Hat customers' security and privacy concerns.

.. _insights-client: https://github.com/redhataccess/insights-client

Blacklists
    A list of files or commands to never upload.
Filters
    A set of grep-like strings used to filter files before adding them to
    the archive.
Dynamic Uploader Configuration
    The client will download a configuration file from Red Hat (by
    default) every time it's executed that will list out every file to
    collect and command to run, including filters to apply to each file,
    specified by rule plugins.  The configuration is signed, which
    should be verified by the client before using it to collect data.

These features allow these archives to be processed quickly and more
securely in the Insights production environment.  On the other hand, the
reduced data set narrows the scope of uses to be Insights-specific.

OCP 4 Archives
--------------

OCP 4 can generate diagnostic archives with a component called the
``insights-operator``.  They are automatically uploaded to Red Hat for analysis.

The openshift-must-gather CLI tool produces more comprehensive archives than
the operator. ``insights-core`` recognizes them as well.

.. _openshift-must-gather: https://github.com/openshift/must-gather


Execution Model
===============

To build rules effectively, one should have a general idea of how data
is executed against each rule.  At a high level:

- Each unit of input data is mapped to a symbolic name
- Each parser that "subscribes" to that symbolic name is executed with
  the given content as part of a ``Context`` object.
- The outputs of all parsers are sorted by host
- For each host, every rule is invoked with the local context,
  populated by parsers from the same plugin, and the shared
  context, the combination of all shared parser outputs for this
  particular host.
- The outputs of all rules is returned, along with other various bits
  of metadata, to the client, depending on what invoked the rules
  framework.

.. _context-label:

Contexts
========

The term ``Context`` refers to the context of the information that is collected
and evaluated by Insights.  Examples of context are Host Context (directly
collected from a host), Host Archive Context (uploaded Insights archive),
SOSReports (uploaded SOSReport archive), and Docker Image Context (directly
collected from Docker image).  The context determines which data sources are
collected, and that in determines the hierarchy of parsers, collectors and rules
that are executed.  Contexts enable different collection methods for data for
each unique context, and also provide a default set of data sources that are
common among one or more contexts.  All available contexts are defined in the
module :py:mod:`insights.core.context`.
  
Data Sources
============

``Data Sources`` define how data processed by Insights is collected.  Each
data source is specific to a unique set of data.  For example a data source
is defined for the contents of the file ``/etc/hosts`` and for the output
of the command ``/sbin/fdisk -l``.  The default data sources provide the
primary data collection specifications for all contexts and are located in
:py:class:`insights.specs.default.DefaultSpecs`.

Each specific ``Context`` may
override a default data source to provide a different collection
specification.  For instance when the Insights client collects the ``fdisk -l``
information it will use the default datasource and execute the command on
the target machine.  This is the :py:class:`insights.core.context.HostContext`.
The Insights client stores that information as a file in an archive.

When the client uploads that information to the Red Hat Insights
service it is processed in the :py:class:`insights.core.context.HostArchiveContext`.
Because the ``fdisk -l`` data is now in a file in the archive the data sources
defined in :py:class:`insights.specs.insights_archive.InsightsArchiveSpecs` are 
used instead.  In this case Insights will collect the data from a file
named ``insights_commands/fdisk_-l``.

The command type datasources in ``default.py`` (``simple_command`` and
``foreach_execute``) only target ``HostContext``. File based datasources fire for any
context annotated with ``@fs_root`` (``HostContext``, ``InsightsArchiveContext``,
``SosArchiveContext``, ``DockerImageContext``, and etc.).
That's why we need a definition in the ``*_archive.py`` files for every command but only
for the files that are different from ``default.py``.

Also, the order in which spec modules load matters. Say we have 2 classes containing
specs, A and B. If B loads after A and both A and B have entries for ``hostname``,
the one that fires depends on the context that each one targets. E.g. if ``A.hostname``
targets ``HostContext`` and ``B.hostname`` targets ``InsightsArchiveContext``, then
they'll each fire for whichever context is loaded. But if both ``A.hostname`` and
``B.hostname`` target ``HostContext``, the datasource in the class that loads last
will win for that context.

While data sources are specific to the context, the purpose of the data source
hierarchy is to provide a consistent set of input to ``Parsers``.  For this
reason ``Parsers`` should generally depend upon :py:class:`insights.specs.Specs`
data sources.

This hierarchy allows a developer to override a particular datasource.  For instance,
if a developer found a bug in a sos_archive datasource,
she could create her own class inheriting from :py:class:`insights.core.spec_factory.SpecSet`,
create the datasource in it,
and have the datasource target ``SosArchiveContext``. So long as the module containing
her class loads after ``default.py``, ``insights_archive.py``, and ``sos_archive.py``,
her definition will win for that datasource when running under a ``SosArchiveContext``.

.. _specification-factories:

Specification Factories
-----------------------

Data sources may utilize various methods called spec factories for collection
of information.
Collection from a file (``/etc/hosts``) and from a command (``/sbin/fdisk -l``)
are two of the most common.  These are implemented by the
:py:func:`insights.core.spec_factory.simple_file`
and :py:func:`insights.core.spec_factory.simple_command` spec factories
respectively.  All of the spec factories currently available for the creation
of data sources are listed below.

:py:func:`insights.core.spec_factory.simple_file`
    simple_file collects the contents of files, for example::
        
        auditd_conf = simple_file("/etc/audit/auditd.conf")
        audit_log = simple_file("/var/log/audit/audit.log")

:py:func:`insights.core.spec_factory.simple_command`
    simple_command collects the output from a command, for example::
        
        blkid = simple_command("/sbin/blkid -c /dev/null")
        brctl_show = simple_command("/usr/sbin/brctl show")

:py:func:`insights.core.spec_factory.glob_file`
    glob_file collects the contents of each file matching the glob pattern(s).
    glob_file also can take a list of patterns as well as an ignore keyword
    arg that is a regular expression telling it which of the matching files to throw out,
    for example::
        
        httpd_conf = glob_file(["/etc/httpd/conf/httpd.conf", "/etc/httpd/conf.d/*.conf"])
        ifcfg = glob_file("/etc/sysconfig/network-scripts/ifcfg-*")
        rabbitmq_logs = glob_file("/var/log/rabbitmq/rabbit@*.log", ignore=".*rabbit@.*(?<!-sasl).log$")


:py:func:`insights.core.spec_factory.first_file`
    first_file collects the contents of the first readable file from a list
    of files, for example::
        
        meminfo = first_file(["/proc/meminfo", "/meminfo"])
        postgresql_conf = first_file([
                                     "/var/lib/pgsql/data/postgresql.conf",
                                     "/opt/rh/postgresql92/root/var/lib/pgsql/data/postgresql.conf",
                                     "database/postgresql.conf"
                                     ])

:py:func:`insights.core.spec_factory.listdir`
    listdir collects a simple directory listing of all the files and
    directories in a path, for example::
        
        block_devices = listdir("/sys/block")
        ethernet_interfaces = listdir("/sys/class/net", context=HostContext)

:py:func:`insights.core.spec_factory.foreach_execute`
    foreach_execute executes a command for each element in provider. Provider
    is the output of a different datasource that returns a list of single
    elements or a list of tuples.  This spec factory is typically utilized
    in combination with a simple_file, simple_command or listdir spec factory
    to generate the input elements, for example::
        
        ceph_socket_files = listdir("/var/run/ceph/ceph-*.*.asok", context=HostContext)
        ceph_config_show = foreach_execute(ceph_socket_files, "/usr/bin/ceph daemon %s config show")
        ethernet_interfaces = listdir("/sys/class/net", context=HostContext)
        ethtool = foreach_execute(ethernet_interfaces, "/sbin/ethtool %s")

:py:func:`insights.core.spec_factory.foreach_collect`
    foreach_collect substitutes each element in provider into path and collects
    the files at the resulting paths.  This spec factory is typically utilized
    in combination with a simple_command or listdir spec factory to generate
    the input elements, for example::
    
        httpd_pid = simple_command("/usr/bin/pgrep -o httpd")
        httpd_limits = foreach_collect(httpd_pid, "/proc/%s/limits")
        block_devices = listdir("/sys/block")
        scheduler = foreach_collect(block_devices, "/sys/block/%s/queue/scheduler")


:py:func:`insights.core.spec_factory.first_of`
    first_of returns the first of a list of dependencies that exists. At least
    one must be present, or this component won't fire.  This spec factory is
    typically utilized in combination with other spec factories to generate
    the input list, for example::
        
        postgresql_log = first_of([glob_file("/var/lib/pgsql/data/pg_log/postgresql-*.log"),
                                   glob_file("/opt/rh/postgresql92/root/var/lib/pgsql/data/pg_log/postgresql-*.log"),
                                   glob_file("/database/postgresql-*.log")])
        systemid = first_of([simple_file("/etc/sysconfig/rhn/systemid"),
                             simple_file("/conf/rhn/sysconfig/rhn/systemid")])

Custom Data Source
------------------

If greater control over data source content is required than provided by the
existing specification factories, it is possible to write a custom data source.
This is accomplished by decorating a function with the ``@datasource`` decorator
and returning a ``list`` type.  Here's an example:

.. code-block:: python
   :linenos:

   @datasource(HostContext)
   def block(broker):
       remove = (".", "ram", "dm-", "loop")
       tmp = "/dev/%s"
       return [(tmp % f) for f in os.listdir("/sys/block") if not f.startswith(remove)]

Custom datasources also can return :py:class:`insights.core.spec_factory.CommandOutputProvider`,
:py:class:`insights.core.spec_factory.TextFileProvider`, or
:py:class:`insights.core.spec_factory.RawFileProvider` instances.

Parsers
=======

A ``Parser`` takes the raw content of a particular ``Data Source`` such as
file contents or command output, parses it, and then provides a small API for
plugins to query.  The parsed data and computed facts available via the API are
also serialized to be used in downstream processes.

Choosing a Module
-----------------

Currently all shared parsers are defined in the package
``insights.parsers``.  From there, the parsers are separated into
modules based on the command or file that the parser consumes.  Commands or
files that are logically grouped together can go in the same module, e.g. the
``ethtool`` based commands and ``ps`` based commands.

Defining Parsers
----------------

There are a couple things that make a function a parser:

1. The function is decorated with the ``@parser`` decorator
2. The function can take multiple parameters, the first is always
   expected to be of type ``Context``.
   Any additional parameters will normally represent  a ``component``
   with a sole purpose of determining if the parser will fire.

Registration and Symbolic Names
-------------------------------

Parsers are registered with the framework by use of the ``@parser`` decorator.
This decorator will add the function object to the list of parsers associated
with the given data source name.  Without the decorator, the parser will
never be found by the framework.

Data source names represent all the possible file content types that can be
analyzed by parsers.  The rules framework uses the data source name mapping
defined in :py:class:`insights.specs.Specs` to map a symbolic
name to a command, a single file or multiple files.  More detail on this mapping
is provided in the section :ref:`specification-factories`

The same mapping is used to create the
``uploader.json`` file consumed by Insights Client to collect data from
customer systems. The Client RPM is developed and
distributed with Red Hat Enterprise Linux as part of the base distribution.
Updates to the Client RPM occur less frequently than to the Insights Core application.
Additionally customers may not update the Client RPM on their systems.
So developers need to check both the Insights Core and the Client applications
to determine what information is available for processing in Insights.

.. autoclass:: insights.core.plugins.parser
   :noindex:

Parser Contexts
---------------

Each parser may take multiple parameters.
The first is always expected to be of type ``Context``.
Order is also important and the parameter of type ``Context``
must always be first.
All information available to a parser is found in the
:py:class:`insights.core.context.Context` object.
Please refer to the Context API documentation
:py:mod:`insights.core.context` for more details.
Any additional parameters will not be of type ``Context``
but will normally represent a ``component`` with a sole
purpose of determining if the parser will fire.

Parser Outputs
--------------

Parsers can return any value, as long as it's serializable.

Parser developers are encouraged to wrap output data in a ``Parser``
class.  This makes plugin developers able to query for higher-level facts about
a particular file, while also exporting the higher level facts for use outside
of Insights plugins.

.. autoclass:: insights.core.Parser
   :members:
   :noindex:

Rule Plugins
============

The purpose of Rule plugins is to identify a particular problem in a given system
based on certain facts about that system.  Each Rule plugin consists of a module
with:

- One ``@rule``-decorated function
- An ``ERROR_KEY`` member (recommended)
- A docstring for the module that includes
    - A summary of the plugin
    - A longer description of what the plugin identifies
    - Links to Red Hat solutions

.. autoclass:: insights.core.plugins.rule
   :noindex:

Rule Parameters
---------------

The parameters for each rule function mirror the parser or parsers identified
in the ``@rule`` decorator. This is best demonstrated by an example:

.. code-block:: python
   :linenos:

    @rule(InstalledRpms, Lsof, Netstat)
    def heartburn(installed_rpms, lsof, netstat):
        # Rule implementation
        
Line 1 of this example indicates that the rule depends on 3 parsers,
``InstalledRpms``, ``Lsof``, and ``Netstat``.  The signature for the
rule function on line 2 contains the parameters that correspond respectively
to the parsers specified in the decorator.  All three parsers are required
so if any are not present in the input data, then the rule will not be called.
This also means that all three input parameters will have some value corresponding
to the parser objects.  It is up to the rule to evaluate the object attributes
and methods to determine if the criteria is met to trigger the rule.

Rule Output
-----------

Rules can return multiple types of responses. If a rule is detecting some
problem and finds it, it should return ``make_fail``. If it is detecting a
problem and is sure the problem doesn't exist, it should return ``make_pass``.
If it wants to return information not associated with a failure or success, it
should return ``make_info``.

To return a rule "hit", return the result of ``make_fail``:

.. autoclass:: insights.core.plugins.make_fail
   :noindex:

To return a rule success, return the result of ``make_pass``:

.. autoclass:: insights.core.plugins.make_pass
   :noindex:

To return system info, return the result of ``make_info``:

.. autoclass:: insights.core.plugins.make_info
   :noindex:

Testing
=======

Since the plugin itself is a fairly simple set of python functions,
individual functions can be easily unit tested.  Unit tests are required
for all plugins and can be found in the ``rules/tests`` directory of the
source.  Unit tests are written using the usual x-unit based
``unittests`` module with some helpers from
`pytest framework <http://pytest.org/latest/>`_. ``pytest`` is the used
test runner.

To run all unit tests with pytest:

    py.test

Run a single single unit test one can:

    py.test path/test_plugin_name.py::TestCaseClass::test_method

To get test results with coverage report:

    py.test  --cov=plugin_package

Feature Deprecation
===================

Parsers and other parts of the framework go through periodic revisions and
updates, and sometimes previously used features will be deprecated.  This is
a three step process:

1. An issue to deprecate the outdated feature is raised in GitHub.  This
   allows discussion of the plans to deprecate this feature and the proposed
   replacement functionality.
2. The outdated function, method or class is marked as deprecated.
   Code using this feature now generates a warning when the tests are run,
   but otherwise works.  At this stage anyone receiving a warning about
   pending deprecation SHOULD change over to using the new functionality or
   at least not using the deprecated version.  The deprecation message MUST
   include information about how to replace the deprecated function.
3. Once sufficient time has elapsed, the outdated feature is removed.  The
   py.test tests will fail with a fatal error, and any code
   checked in that uses deprecated features will not be able to be merged
   because of the tests failing.  Anyone receiving a warning about
   deprecation MUST fix their code so that it no longer warns of deprecation.

The usual time between each step should be two minor versions of the Insights
core.

To deprecate code, call the :py:func:`insights.util.deprecated` function from
within the code that will be eventually removed, in the following manner:

Functions
---------

.. code-block:: python

    from insights.util import deprecated

    def old_feature(arguments):
        deprecated(old_feature, "Use the new_feature() function instead")
        ...

Class methods
-------------

.. code-block:: python

    from insights.util import deprecated

    class ThingParser(Parser):
        ...

        def old_method(self, *args, **kwargs):
            deprecated(self.old_method, "Use the new_method() method instead")
            self.new_method(*args, **kwargs)
        ...

Class
-----

.. code-block:: python

    from insights.util import deprecated

    class ThingParser(Parser):
        def __init__(self, *args, **kwargs):
            deprecated(ThingParser, "Use the new_feature() function instead")
            super(ThingParser, self).__init__(*args, **kwargs)
        ...

The :py:func:`insights.util.deprecated` function takes three arguments:

- The ``function`` or method being deprecated.  This is used to tell the user
  where the deprecated code is.  Classes cannot be directly deprecated, and
  should instead emit a deprecation message in their ``__init__`` method.
- The ``solution`` to using this deprecated.  This is a descriptive string
  that should tell anyone using the deprecated function what to do in future.
  Examples might be:

    - For a replaced parser: "Please use the ``NewParser`` parser in the
      ``new_parser`` module."
    - For a specific method being replaced by a general mechanism: "Please
      use the ``search`` method with the arguments ``state="LISTEN"``."
