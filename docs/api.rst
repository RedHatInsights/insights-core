Input Data Formats
==================

Before any data reaches the rules framework, it obviously has to be generated.
There are currently several input data formats that can be processed by insights-core:

SoSReports
----------

A SoSReport_ is a command-line tool for Red Hat Enterprise Linux (and other
systems) to collect configuration and diagnostic information from the system.

.. _SoSReport: https://github.com/sos/sosreport

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
    A set of grep-like strings used to filter files before adding it to
    the archive.
Dynamic Uploader Configuration
    The client will download a configuration file from Red Hat (by
    default) ever time it's executed that will list out every file to
    collect and command to run, including filters to apply to each file,
    specified by rule plugins.  The configuration is signed, which
    should be verified by the client before using it to collect data.

These features allow these archives to be processed quickly and more
securely in the Insights production environment.  On the other hand, the
reduced data set narrows the scope of uses to be Insights-specific.

Execution Model
===============

To build rules effectively, one should have a general idea of how data
is executed against each rule.  At a high level:

- Each unit of input data is mapped to a symbolic name
- Each mapper that "subscribes" to that symbolic name is executed with
  the given content as part of a ``Context`` object.
- The outputs of all mappers are sorted by host
- For each host, every reducer is invoked with the local context,
  populated by mappers from the same plugin, and the shared reducer
  context, the combination of all shared mapper outputs for this
  particular host.
- The outputs of all reducers is returned, along with other various bits
  of metadata, to the client, depending on what invoked the rules
  framework.

Mappers
=======

A mapper takes the raw content of a particular file or command output (from our
specs), parses it, and then provides a small API for plugins to query.  The
parsed data and computed facts available via the API are also serialized to be
used in downstream processes.

Legacy Mappers
--------------

It was once standard to write all mappers in the same plugin module as
the reducers.  This is now considered **deprecated** and will be removed
in a future release.

The deprecation of "local mappers" is due to a number of reasons:

Code Maintenance
    Many plugins were parsing the same file in very similar ways,
    causing maintenance overhead (i.e. if one mapper had to change, it
    was likely that all of them had to change).  Many plugin mappers
    were implemented slightly differently, potentially introducing bugs
    that are difficult to catch since only one reducer is using the
    output of a local mapper.
Performance
    Many plugin mappers would parse the same symbolic file that other
    mappers were parsing, which is much more expensive than analyzing
    pre-parsed data structures provided by a single shared mapper.
Usability
    Shared mappers are generally designed to produce more user-friendly
    output.

.. note::
   "Shared mappers" will be known simply as "mappers" once the
   deprecated legacy mappers have been removed from the framework.

Much of a plugin's "business logic" was placed in legacy mappers, but with new
"shared mappers", all business logic must be placed in the *reducer*.

Choosing a Module
-----------------

Currently all shared mappers are defined in the package
``insights.mappers``.  From there, the mappers are separated into
modules based on the command or file that the mapper consumes.  Commands or
files that are logically grouped together can go in the same module, e.g. the
``ethtool`` based commands and ``ps`` based commands.

Defining Mappers
----------------

There are a couple things that make a function a mapper:

1. The function is decorated with the ``@mapper`` decorator
2. The function takes one parameter, which is expected to be of type
   ``Context``.

Registration and Symbolic Names
-------------------------------

Mappers are registered with the framework by use of the ``@mapper`` decorator.
This decorator will add the function object to the list of mappers associated
with the given symbolic name.  Without the decorator, the mapper will
never be found by the framework.

Symbolic names represent all the possible file content types that can be
analyzed by mappers.  The rules framework uses the symbolic name mapping
defined in ``insights.specs.static`` to map a symbolic name to either a
command or absolute file path.  The same mapping is used to create the
``uploader.json`` file consumed by Insights clients to collect data from
customer systems.

.. autofunction:: insights.core.plugins.mapper
   :noindex:

Mapper Contexts
---------------

Each mapper takes exactly one parameter, which is expected to be of type
``Context``.  All information available to a mapper is found in the
``Context`` object.  Please refer to the `Context API documentation
</api_index.html#insights.core.context.Context>`_ for
more details.

Mapper Outputs
--------------

Mappers can return any value, as long as it's serializable.

Mapper developers are encouraged to wrap output data in a ``Mapper``
class.  This makes plugin developers able to query for higher-level facts about
a particular file, while also exporting the higher level facts for use outside
of Insights plugins.

.. autoclass:: insights.core.Mapper
   :members:
   :noindex:

Plugins (Reducers)
==================

The purpose of "plugins" is to identify a particular problem in a given system
based on certain facts about that system.  Each plugin consists of a module
with:

- One ``@reducer``-decorated function
- An ``ERROR_KEY`` member (recommended)
- A docstring for the module that includes
    - A summary of the plugin
    - A longer description of what the plugin identifies
    - A Trello/Jira link

.. autofunction:: insights.core.plugins.reducer
   :noindex:

Reducer Context
---------------

Each reducer function must have only two parameters, named ``local`` and
``shared``.  The ``local`` parameter contains mapper outputs from local (i.e.
legacy) mappers, and the ``shared`` parameter contains mapper outputs from
shared mappers.  Since local mappers are considered deprecated, the ``local``
parameter will eventually be removed.

.. note::
   New plugins should avoid using the ``local`` context since it is deprecated.

The ``shared`` context is a dictionary where the keys are the function object
of the mapper that produced the output.  This means that plugins must import
every mapper that they intend to use, and they should list the function objects
in the ``requires`` keyword argument to the ``@reducer`` decorator, if
applicable.  If the symbolic name for the given mapper is a pattern file, then
the value of the mapper's output will be a list, otherwise it will be whatever
the mapper returns.  If the given mapper returns a ``Mapper`` instance,
plugins are are encouraged to use the higher-level functions defined on the
given ``Mapper`` object to perform its business logic over functions
performed directly on the built-in data structures found in the
``Mapper`` instance.

Reducer Output
--------------

Reducers can return two types of responses:  a rule "hit" or "action", or
system metadata.

To return a rule "hit", return the result of ``make_response``:

.. autofunction:: insights.core.plugins.make_response
   :noindex:

To return system metadata, return the result of ``make_metadata``:

.. autofunction:: insights.core.plugins.make_metadata
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
