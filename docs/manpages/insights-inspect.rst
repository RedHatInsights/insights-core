###################
INSIGHTS-INSPECT(1)
###################

NAME
====

    insights-inspect - execute an insights component into an iPython session

SYNOPSIS
========

    **insights-inspect** [OPTIONS] COMPONENT [ARCHIVE]

DESCRIPTION
===========

The *insights-inspect* command provides a tool to execute a component in insights,
and then load the component into an iPython session so that it can be inspected
and manipulated.  The **COMPONENT** can be anything in the dependency tree including
a datasource, parser, combiner, and rule.

*Insights-inspect* executes
the **COMPONENT** and collects data from the system, or if **ARCHIVE**
is provided it will collect data from the archive.
Archive datasources are documented
in :py:mod:`insights.specs.insights_archive`,
:py:mod:`insights.specs.sos_report` and :py:mod:`insights.specs.jdr_archives`.

OPTIONS
=======

    -c CONFIG --config CONFIG
        Configure components.

    -D --debug
        Show debug level information.

    -h --help
        Show the command line help and exit.

EXAMPLES
========

    insights-inspect insights.specs.Specs.redhat_release
        Executes insights-core and opens an iPython session with a
        datasource object populated for
        :py:attr:`insights.specs.Specs.redhat_release` and
        all objects that the datasource depends upon.  The example
        session in iPython would look like this:

        .. code-block:: python
           
            Enter 'redhat_release.' and tab to get a list of properties
            Example:
            In [1]: redhat_release.<property_name>
            Out[1]: <property value>

            To exit iPython enter 'exit' and hit enter or use 'CTL D'

            Python 3.6.8 (default, Jan 27 2019, 09:00:23)
            Type 'copyright', 'credits' or 'license' for more information
            IPython 7.3.0 -- An enhanced Interactive Python. Type '?' for help.

            In [1]: redhat_release
            Out[1]: TextFileProvider("'/etc/redhat-release'")

            In [2]: redhat_release.content
            Out[2]: ['Fedora release 29 (Twenty Nine)']

    insights-inspect insights.parsers.hostname.Hostname
        Executes insights-core and opens an iPython session with a
        parser object populated for
        :py:class:`insights.parsers.hostname.Hostname` and
        all objects that the parser depends upon. The example session
        in iPython would look like this:

        .. code-block:: python

            IPython Console Usage Info:

            Enter 'Hostname.' and tab to get a list of properties
            Example:
            In [1]: Hostname.<property_name>
            Out[1]: <property value>

            To exit iPython enter 'exit' and hit enter or use 'CTL D'

            Python 3.6.8 (default, Jan 27 2019, 09:00:23)
            Type 'copyright', 'credits' or 'license' for more information
            IPython 7.3.0 -- An enhanced Interactive Python. Type '?' for help.

            In [1]: Hostname
            Out[1]: <insights.parsers.hostname.Hostname at 0x7f64e81fef60>

            In [2]: Hostname.fqdn
            Out[2]: 'myhostname.mydomainname.com'

            In [3]: Hostname.domain
            Out[3]: 'mydomainname.com'

    insights-inspect insights.plugins.always_runs.report
        Executes insights-core and opens an iPython session with a
        rule object populated for
        :py:func:`insights.plugins.always_runs.report` and
        all objects that the rule depends upon. The example session
        in iPython would look like this:

        .. code-block:: python

            IPython Console Usage Info:

            Enter 'report.' and tab to get a list of properties 
            Example:
            In [1]: report.<property_name>
            Out[1]: <property value>

            To exit iPython enter 'exit' and hit enter or use 'CTL D'

            Python 3.6.8 (default, Jan 27 2019, 09:00:23) 
            Type 'copyright', 'credits' or 'license' for more information
            IPython 7.3.0 -- An enhanced Interactive Python. Type '?' for help.

            In [1]: report
            Out[1]: {'kernel': 'this is junk', 'type': 'pass', 'pass_key': 'ALWAYS_FIRES'}

    insights-inspect -c configfile.yaml insights.specs.Specs.redhat_release
        Inspects the information collected by the COMPONENT using the configuration
        information
        provided in configfile.yaml.  See :doc:`CONFIG(5) <./config>` for more information
        on the specifics of the configuration file options and format.

    insights-inspect -D insights.specs.Specs.redhat_release
        The -D option will produce a trace of the operations performed by insights-core as
        the COMPONENT is executed.  The COMPONENT data will be output following all of
        the debugging output.

SEE ALSO
========

    :doc:`insights-cat(1) <./insights-cat>`, :doc:`insights-info(1) <./insights-info>`, :doc:`insights-run(1) <./insights-run>`,
    :doc:`config(5) <./config>`
