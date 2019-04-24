###############
INSIGHTS-CAT(1)
###############

NAME
====

    insights-cat - execute insights datasources on a system or archives

SYNOPSIS
========

    **insights-cat** [OPTIONS] SPEC [ARCHIVE]

DESCRIPTION
===========

The *insights-cat* command provides a tool to investigate information as it is
collected by insights-core.  When the insights client runs it uses the datasources
(often referred to as a SPEC) to collect information from a system or an archive.

The SPECs for system collection are located in
:py:mod:`insights.specs.default`.  *Insights-cat* executes
the SPEC to either collect from the system, or if **ARCHIVE**
is provided it will collect from the archive.  Archive datasources are documented
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

    \-\-no-header
        Don't print command or path headers.

    -p PLUGINS --plugins PLUGINS
        Comma-separated list without spaces of package(s) or module(s) containing plugins.

    -q --quiet
        Only show commands or paths.

EXAMPLES
========

    insights-cat redhat_release
        Outputs the information collected by the SPEC
        :py:attr:`insights.specs.default.DefaultSpecs.redhat_release`, including the header
        describing the SPEC type and value.

    insights-cat --no-header redhat_release
        Outputs the information collected by the SPEC
        :py:attr:`insights.specs.default.DefaultSpecs.redhat_release` with no header.  This
        is appropriate when you want to collect the data in the form as seen by a parser.

    insights-cat -c configfile.yaml redhat_release
        Outputs the information collected by the SPEC using the configuration information
        provided in configfile.yaml.  See :doc:`CONFIG(5) <./config>` for more information
        on the specifics of the configuration file options and format.

    insights-cat -D redhat_release
        The -D option will produce a trace of the operations performed by insights-core as
        the SPEC is executed.  The SPEC data will be output following all of the debugging
        output.

    insights-cat -D -p examples.rules.stand_alone examples.rules.stand_alone.Specs.hosts
        The -p option allows inclusion of additional modules by insights-core.  By default
        the insights-core cat command will only load the insights-core modules.  In this
        example the file *examples/rules/stand_alone.py* includes a spec ``Specs.hosts``.
        This command will execute the ``hosts`` spec in the examples file and not the
        insights spec ``hosts``.

        The -D option will show each module as it is loaded and the actual spec used for
        the command.

    insights-cat -D -p module1,module2,module3 spec_name
        Multiple modules can be loaded with the -p option by separating them with commas.

    insights-cat -q installed_rpms
        The -q switch will inhibit output of the command or file, and only show the spec
        type and the command to be executed or file to be collected.  Use this switch when
        you are interested in the details of the spec and don't care about the data.

SEE ALSO
========

    :doc:`insights-info(1) <./insights-info>`, :doc:`insights-inspect(1) <./insights-inspect>`,
    :doc:`insights-run(1) <./insights-run>`, :doc:`config(5) <./config>`
