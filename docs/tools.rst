#####
Tools
#####

Insights Cat
############

The cat module allows you to execute an insights datasource and write its
output to stdout. A string representation of the datasource is written to
stderr before the output.

Options::

   -c CONFIG --config  CONFIG      Configure components
   -p PLUGINS --plugins PLUGINS    Comma-separated  list without spaces of package(s) or module(s) containing plugins.
   -q --quite                      Only show commands or paths.
   --no-header                     Don’t print command or path headers
   -D --debug                      Show debug level information
   spec                            Spec to dump
   archive                         Archive or directory to analyze

Examples:

Outputs the information collected by the SPEC :py:attr:`insights.specs.default.DefaultSpecs.redhat_release`,
including the header describing the SPEC type and value.

.. code-block:: python
   :linenos:

    insights-cat redhat_release

Outputs the information collected by the SPEC :py:attr:`insights.specs.default.DefaultSpecs.redhat_release`
with no header. This is appropriate when you want to collect the data in the form as seen by a parser.

.. code-block:: python
   :linenos:

    insights-cat --no-header redhat_release

Outputs the information collected by the SPEC using the configuration information provided in configfile.yaml.
See :doc:``CONFIG(5)  <./config>`` for more information on the specifics of the configuration file options and format.

.. code-block:: python
   :linenos:

    insights-cat -c configfile.yaml redhat_release

The -D option will produce a trace of the operations performed by insights-core as the SPEC is executed.
The SPEC data will be output  following all of the debugging output.

.. code-block:: python
   :linenos:

    insights-cat -D redhat_release

The -p option allows inclusion of additional modules by insights-core. By default the insights-core cat command will
only load the insights-core modules. In this example the file examples/rules/stand_alone.py includes a spec Specs.hosts.
This command will execute the hosts spec in the examples file and not the insights spec hosts.The -D option will show
each module as it is loaded and the actual spec used for the command.

.. code-block:: python
   :linenos:

    insights-cat -D -p examples.rules.stand_alone examples.rules.stand_alone.Specs.hosts

Multiple modules can be loaded with the -p option by separating them with commas.

.. code-block:: python
   :linenos:

    insights-cat -D -p module1,module2,module3 spec_name

The -q switch will inhibit output of the command or file, and only show the spec type and the command to be executed or
file to be collected. Use this switch when you are interested in the details of the spec and don't care about the data.

.. code-block:: python
   :linenos:

    insights-cat -q installed_rpms


More insights-cat examples can be fund here :py:mod:`insights.tools.cat`


Insights Info
#############

Allow users to interrogate components.

Options::

   -c COMPONENTS  --components COMPONENTS     Comma separated list of components to get info about
   -i --info                                  Comma separated list to get dependency info about
   -p PLUGINS --preload PLUGINS               Comma separated list of packages or modules to preload
   -d --pydoc                                 Show pydoc for the given object. E.g.: insights-info -d insights.rule
   -s --source                                Show source for the given object. E.g.:
                                              Insights-info  -s Insights.core.plugins.rule
   -S --specs                                 Show specs for the given  name. E.g.: insights-info -S uname
   -t TYPES --types TYPES                     Filter results based on component type; e.g. 'rule,parser'.
                                              Names without  '.'  are assumed to be in Insights.core.plugins.
   -v --verbose                               Print component  dependencies.

Examples:

Search for all datasources that might handle foo, bar, or baz files or commands along with all components that could be
activated if they were present and valid.

.. code-block:: python
   :linenos:

   insights-info foo bar baz

Search for all datasources that might handle foo, bar, or baz files or commands along with all components that could
be activated if they were present and valid.

Display dependency information about the hosts datasource.

.. code-block:: python
   :linenos:

   insights-info -i insights.specs.Specs.hosts

Display the pydoc information about the Hosts parser.

.. code-block:: python
   :linenos:

   insights-info -d insights.parsers.hosts.Hosts


Insights Inspect
################

The inspect module allows you to execute an insights component
(parser, combiner, rule or datasource) dropping you into an
ipython session where you can inspect the outcome.

Options::

   -c CONFIG --config  CONFIG      Configure components
   -D --debug                      Show debug level information
   component                       Component to inspect
   archive                         Archive or directory to analyze

Examples:

Creates an ipython session to explore the Hostname parser

.. code-block:: python
   :linenos:

      insights-inspect insights.parsers.hostname.Hostname

Creates an ipython session to explore the hostname combiner

.. code-block:: python
   :linenos:

      insights-inspect insights.combiners.hostname.hostname

Creates an ipython session to explore the hostname spec

.. code-block:: python
   :linenos:

   insights-inspect insights.specs.Specs.hostname

Creates an ipython session to explore the bash_version rule

.. code-block:: python
   :linenos:

   insights-inspect examples.rules.bash_version.report

More insights-inspect examples can be found here :py:mod:`insights.tools.insights_inspect`