Component Configuration
=======================

Insights core components can be loaded, configured, and run with a yaml
file passed to `insights-run -c <config.yaml>`.

The file contains three top level keys: ``default_component_enabled``,
``packages``, and ``configs``.

default_component_enabled
-------------------------

``default_component_enabled`` controls the enabled state of all components that
are loaded either by default or with entries in the ``packages`` section.
Defaults to ``true``. If ``false``, enable components by giving them entries in
the ``configs`` section with an ``enabled`` key set to ``true``.

packages
--------

``packages`` is a simple list of packages or modules to recursively load. The
following example will load all modules beneath ``insights.parsers``

.. code:: yaml

    packages:
        - insights.parsers

configs
-------

``configs`` contains a list of dictionaries, each of which holds some
configuration for a given component or set of components.

Each entry has the following keys.

-  name: the prefix to the name of a component or set of components to
   which this configuration should apply. For example, a name of
   ``insights`` would apply the configuration to all components with
   names beginning with insights. ``insights.combiners`` would scope the
   configuration to just the components beneath the combiners package.
   You can specify the exact name of a component if you wish. For
   example, ``name: examples.rules.stand_alone.report`` applies to just
   that report component in the stand_alone module.
-  enabled: can be ``true`` or ``false``. Defaults to the value of
   ``default_component_enabled``.
-  timeout: will set the timeout of any command-based datasource defined using
   the helper classes like ``simple_command`` and ``foreach_command``.
-  tags: a list of strings you want to associate with the component. If
   the component has default tags already, they are overridden by what
   you specify here.
-  metadata: an arbitrary dictionary of data to associate with the
   component. If the component is a class and has class level attributes
   with the same names as the metadata keys, those attributes will be
   updated to the corresponding values. If the component is a function
   or doesn't have a corresponding attribute for a metadata key, it can
   still access the metadata dictionary with
   ``meta = dr.get_metadata(component)``. This provides a way to
   configure components and parameterize rules with the configuration
   file instead of code changes.

Entries are applied from top to bottom, so you can have overall
configuration for many components at the top and then specialize
particular ones further down.

Examples
========

Load and run the stand_alone rules module
-----------------------------------------

.. code:: yaml

    packages:
        - examples.rules.stand_alone

Load and run all of the example rules
-------------------------------------

.. code:: yaml

    packages:
        - examples.rules

Load and run all of the example rules with ``default_component_enabled`` set to ``false``
-----------------------------------------------------------------------------------------

Notice you have to explicitly enable all dependencies if
``default_component_enabled`` is ``false``. We'd use this if generating
a configuration to send to a client to execute so we have complete
control over what gets run.

Note that we can even specify a particular class containing datasources
to enable (``insights.specs.Specs``).

.. code:: yaml

    default_component_enabled: false

    packages:
        - examples.rules

    configs:
        - name: examples.rules
          enabled: true

        - name: insights.parsers
          enabled: true

        - name: insights.specs.Specs
          enabled: true

        - name: insights.specs.default
          enabled: true

        - name: insights.core.spec_factory
          enabled: true

Parameterize a rule
-------------------

Say we had a rule like this

.. code:: python

    # example.py

    from insights import dr, rule, make_fail, make_pass
    from insights.parsers.df import DiskFree_AL


    @rule(DiskFree_AL)
    def report(disks):
        meta = dr.get_metadata(report)
        threshold = meta.get("threshold", 85.0)

        bad = {}
        for disk in disks:
            try:
                used, total = float(disk.used), float(disk.total)
                if total > 0.0:
                    usage = (used / total) * 100
                    if usage >= threshold:
                        bad[disk.mounted_on] = usage
            except:
                pass
        if bad:
            return make_fail("DISK_FULL_WARNING", bad=bad)
        return make_pass("DISK_FULL_WARNING")

we could parameterize threshold like this:

.. code:: yaml

    packages:
     - example

    configs:
        - name: example.report
        - metadata:
            threshold: 50.0

Parameterize a class
--------------------

Say we had a class like this

.. code:: python

    # example.py

    from insights import parser, Parser, rule, make_pass
    from insights.specs import Specs


    @parser(Specs.hostname)
    class Hostname(Parser):
        upcase = False

        def parse_content(self, content):
            self.data = []
            for line in content:
                self.data.append((line.upper() if self.upcase else line).strip())


    @rule(Hostname)
    def show_hostname(hn):
        return make_pass("HOSTNAME", host=hn.data[0])

we can set the ``upcase`` class attribute from the yaml like this

.. code:: yaml

    packages:
     - example

    configs:
        - name: example.Hostname
        - metadata:
            upcase: true

