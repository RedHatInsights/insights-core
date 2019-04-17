################
INSIGHTS-INFO(1)
################

NAME
====

    insights-info - interrogate components to get info (source, docs, dependencies, etc.)

SYNOPSIS
========

    **insights-info** [OPTIONS] SPEC [ARCHIVE]

DESCRIPTION
===========

The *insights-info* command provides a tool to interrogate insights-core components
and any components added using the command options.  *Insights-info* can be used to
display embedded documentation and source code for components as well as showing
the a component's dependency information.

OPTIONS
=======

    -c COMPONENTS --components COMPONENTS
        Comma separated list of components that have already
        executed. Names without '.' are assumed to be in
        insights.specs.Specs.

    -d COMPONENT --pydoc COMPONENT
        Show pydoc for the given object. E.g.: insights-info -d insights.rule.

    -h --help
        Show the command line help and exit.

    -i COMPONENT --info COMPONENT
        Comma separated list of components to get dependency info about.

    -p PLUGINS --preload PLUGINS
        Comma separated list of packages or modules to preload.

    -s COMPONENT --source COMPONENT
        Show source for the given component. E.g.: insights-info -s insights.parsers.redhat_release

    -S NAME --specs NAME
        Show specs for the given name. E.g.: insights-info -S uname

    -t TYPES --types TYPES
        Filter results based on component type; e.g. 'rule,parser'. Names without '.'
        are assumed to be in insights.core.plugins.

    -v --verbose
        Print component dependencies.

EXAMPLES
========

    insights-info foo bar baz
        Search for all datasources that might handle foo, bar, or baz files
        or commands along with all components that could be activated if they
        were present and valid.

    insights-info -i insights.specs.Specs.hosts
        Display dependency information about the hosts datasource.

    insights-info -d insights.parsers.hosts.Hosts
        Display the pydoc information about the Hosts parser.

SEE ALSO
========

    :doc:`insights-cat(1) <./insights-cat>`, :doc:`insights-inspect(1) <./insights-inspect>`,
    :doc:`insights-run(1) <./insights-run>`, :doc:`config(5) <./config>`
