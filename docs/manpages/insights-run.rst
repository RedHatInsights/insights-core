###############
INSIGHTS-RUN(1)
###############

NAME
====

    insights-run - execute insights-core with a set of components on a system or archives

SYNOPSIS
========

    **insights-run** [OPTIONS] [ARCHIVE]

DESCRIPTION
===========

The *insights-run* command provides a tool to execute a set of components including
datasources (SPECs), parsers, combiners and rules on a host system, or on one or more
archive files.

OPTIONS
=======

    -b "spec=input_file[,spec=input_file,...]" --bare  "spec=input_file[,spec=input_file,...]"
        Specify that a particular input file should be used for a spec.  This allows you to
        use specific files for input to a run.  For example to use your own *messages.log* file
        as input instead of the *messages.log* file in an archive::

            insights-run -b "messages=$HOME/data/messages.log" -p myinsights.myrules

        The short name can be used for insights-core specs. If custom specs are used you must
        specify the full module path for the spec::

            -b "myinsights.myspecs.specs.custom_messages=$HOME/data/messages.log"

        When ``-b`` is used, [ARCHIVE] is ignored.

    -c CONFIG --config CONFIG
        Configure components.

    \-\-context CONTEXT
        Execution Context. Defaults to HostContext if an archive isn't passed.
        See :ref:`context-label` for additional information.

    -D --debug
        Show debug level information.

    -d --dropped
        Show collected files that weren't processed.

    -F --fail-only
        Show FAIL results only. Conflict with '-m' or '-f', will be dropped when using them together.

    -f FORMAT --format FORMAT
        Output format to an alternative format.  The default format is 'text'.  Alternative
        formats are '_json', '_yaml' and '_markdown'.

    -h --help
        Show the command line help and exit.

    -i INVENTORY --inventory INVENTORY
        Ansible inventory file for cluster analysis.  See INVENTORY(5) for more information
        about the options for format of the inventory file.

    -m --missing
        Show missing requirements.

    -p PLUGINS --plugins PLUGINS
        Comma-separated list without spaces of package(s) or module(s) containing plugins.

    -s --syslog
        Sends all log results to syslog.  This is normally used when insights-core is run
        in other applications, or in a non-interactive process.

    -t --tracebacks
        Show stack traces when there are errors in components.

    -v --verbose
        Verbose output.

EXAMPLES
========

    insights-run -p examples.rules
        Runs all of the rules that are implemented in the module example.rules and sub-modules
        by executing all required datasources against the local host system.

    insights-run -p examples.rules insights-archive.tar.gz
        Runs all of the rules that are implemented in the module example.rules and sub-modules
        by executing all required datasources against the insights archive.

    insights-run -p examples.rules sosreport.tar.xz
        Runs all of the rules that are implemented in the module example.rules and sub-modules
        by executing all required datasources against the sosreport.

SEE ALSO
========

    :doc:`insights-cat(1) <./insights-cat>`, :doc:`insights-info(1) <./insights-info>`, :doc:`insights-inspect(1) <./insights-inspect>`,
    :doc:`config(5) <./config>`, :doc:`inventory(5) <./inventory>`
