#########
CONFIG(5)
#########

NAME
====

    config - configuration file for insights-core tools

SYNOPSIS
========

    **filename.yaml**

DESCRIPTION
===========

The insights-core tools allow a configuration options file to be specified
that provides more detailed control over the execution of insights-core by
each tool.  Any filename may be used, but the format of the file must be
YAML.

EXAMPLES
========

A complete example of a configuration file in YAML format::

    # disable everything by default
    # defaults to false if not specified.
    default_component_enabled: false

    # packages and modules to load
    packages:
        - insights.specs.default
        - another.plugins.module

    # configuration of loaded components. names are prefixes, so any component with
    # a fully qualified name that starts with a key will get the associated
    # configuration applied. Can specify timeout, which will apply to command
    # datasources. Can specify metadata, which must be a dictionary and will be
    # merged with the components' default metadata.
    configs:
        - name: another.plugins.module
          enabled: true

        - name: insights.specs.Specs
          enabled: true

        - name: insights.specs.default.DefaultSpecs
          enabled: false

        - name: insights.parsers.hostname
          enabled: true

        - name: insights.parsers.facter
          enabled: true

        - name: insights.parsers.systemid
          enabled: true

        - name: insights.combiners.hostname
          enabled: true

    # needed because some specs aren't given names before they're used in DefaultSpecs
        - name: insights.core.spec_factory
          enabled: true


SEE ALSO
========

    :doc:`insights-cat(1) <./insights-cat>`, :doc:`insights-run(1) <./insights-run>`
