####
Fava
####

:Version: 0.1
:Date: Oct 27, 2016

.. contents:: Table of Contents
    :depth: 6

**************
Fava Rationale
**************


Third Party Rule Plugins
========================

We would like to make it possible/easier for third-parties to develop insights rules.

Their are several advantages to implementing rule plugins as a Domain Specific Language (DSL):
  * sandboxing: the language and its implementation can limit what a rule developer can do.
  * framework independence: the DSL and the insights framework are less tightly coupled; rule developers and framework developers are more insulated from each other.

Another often stated advantage of a DSL is that it is (can be) easier to learn.  There is some truth in this.  In order to develop a Rule in Insights currently you are required to know (or learn) both Python and the Insights Framework.  One the other hand, how easy it is to learn a DSL is entirely dependent upon the quality and quantity of its documentation.  If you don't have complete reference material for every language construct, and lots of useful examples and blog posts ..., the language just won't be easy to learn.

DSL's can be developed entirely from scratch: choose a syntax, write a parser, win.  But inventing and implementing a syntax from scratch is actually really hard, often ends up looking alot like some other language's syntax, but is subtly different because of implementation differences.

Usefully a bunch of Data Languages (... XML, JSON, YAML, ...) have come along which, as a side effect of their normal purpose (shipping data across space and/or time), provide both a well defined syntax and usable implementation of that syntax.  For a while, every DSL was implemented as an XML language: using XML's syntax, and providing symantics for specific patterns in that syntax.  Then every one used JSON....  Now we are at YAML.  I don't think YAML is the end of this, but I think it is where we are now.

Ansible (ansible playbooks) is a DSL based on YAML.  Actually it's based on both YAML and Jinja2's templateing language.   YAML provides the outer syntax, the overall format of playbooks, while Jinja2 provides the syntax for expressions and variable references.

I think we should build a DSL for rules, and that it should be based, abstractly, on Ansible playbooks combination of YAML and Jinja2.  *Not* implement Insights rules as Ansible playbooks, rules and playbooks are too different.  But reuse Ansibile's combination of YAML and Jinja2 as if it were a new Data Language underlying both Ansible playbooks and Insights Rules.  Complete conceptual reuse, actual code reuse only as much as is practically possible.

The important parts of a rule plugin:
  * a set of parsers used by this rule plugin
  * a name, identifier
  * a condition, a Boolean expression of the data from the parsers
  * a set of pydata, a set of key/value pairs giving additional,
    machine specific details about the rule-hit using data from the parsers
    The output of a rule plugin is either nothing (None) indicating that the condition evaluated to false,
    or a combination of the identifiers name and the pydata.

For example:

.. code-block:: yaml

  rule:
    name: "UNAME_TEST"
    pydata:
      kernel: "{{ Uname.kernel }}"
    when: Uname.fixed_by('2.6.32-431.11.2.el6', introduced_in='2.6.32-431.el6')

The overall document is a dictionary. This document only has one rule.  Each top level dictionary can currently only have one element which must have the key ``rule``.  While superfluous now, it will allow us to add things other than rules if we should want to later.

The value associated with the ``rule`` key defines a rule.  It must have a ``name``, ``when``, and ``pydata`` members.  It may have a ``vars`` key.


The value of the ``when`` key is a Jinja2 expression which determines when the rule fires.  If the value of the ``when`` key evaluates to true, then this rule fires.  In this case the Jinja2 expression is a call to the ``fixed_by`` member function on the value of the Uname mapper.  In Python this would be:

.. code-block:: python

  if shared['Uname'].fixed_by('2.6.32-431.11.2.el6', introduced_in='2.6.32-431.el6'):
   return ...

In terms of Jinja2, ``Uname`` is defined (by fava) to be the value ``shared['Uname']``, and if this variable is used in the rule, then the Uname Shared parser is declared to be a dependency of this rule.

The value of the ``name`` key is the name of the rule to return if the rule fires. In this case it is ``UNAME_TEST``, in general it is the same string one passes as the first argument to ``make_result``.

The value of the pydata key is a dictionary of the pydata to be added to the result if the rule fires.  In this case there is only one member of the pydata, ``kernel``, but in general it can contain multiple members.  The values of each of these members is a Jinja2 expression, that are evaluated to determine the values of the members of the returned pydata mapping.

Fava and Loops
==============

There are no loops in Fava (no for-loop, no while-loop, ...).   These kinds of loops are a major pain to implement, and are a major source of bugs for both implementers and users.  All loops that a rule writer might want to write can be written as an expression on lists (a transformation of one list to another, or a transformation of a list to a single value).  Expressions on lists are easy to implement, and easy to use once you know how.  So expressions on lists is what Fava has.

Take this Python for loop for example:

.. code-block:: python

  up = []
  for e in eth:
    if e.link_detected:
      up.append(e)

This creates a list, up, which contains every member of the list eth for which the member link_detectedis true.  It transforms the list eth to the list up.

In Fava we write this:

.. code-block:: yaml

  ---
  rule:
    # stuff skipped....
    vars:
      up: "{{ eth|selectattr('link_detected')|list }}"
    # stuff skipped....

This is a Jinja2 expression, it says to apply the selectattr filter to eth, and then to apply the list filter to its result.  The selectattr filter selects items from its argument (the thing it is filtering), including in its result only those for which the given attribute (link_detected) is true.  The list filter converts its argument to an actual list if it isn't already.  Jinja2 will optimize a series of fiters to avoid creating intermediate lists for each step.

Other Jinja2 filters for transforming lists are: map, select, reject, rejectattr, and join.


Rule Plugins and Content
========================


What rule plugins don't include, and insights-core itself doesn't address is giving meaning to this result.  That is addressed by another part of Insights, the face of the Insights application, which contains content for each rule identifier and associated pydata.

As we consider how to allow third parties to develop Insights rules, we must also how third parties are going to develop content and associate it with the rules they develop.

In our minds, we have a tight coupling between rule plugins and the content associated with that rule.  But in our code, the coupling is very fragile.  Plugins and content are developed in separate repos, and kept in sync by convention, testing, and a good bit of human effort.  There are both advantages and disadvantages tight coupling as well as clear separation, but this dicotomy of how we think verses how we have implemented has led us to a situation where we are getting more of the disadvantages of both than the advantages.

One possibility would be to combine content and plugins, include content into the definition of the rule: more fields in the YAML description of a rule which include the content we currently keep separate.

Another possibility is to clean up the separation between the two:
  * rule plugins, and insights-core in general, just produces rule hits: abstractly no different from what shared parsers and combiners do: just some more facts associated with a system.
  * other tools, insights-engine most importantly, but also other arbitrary systems can take those rule hits

Some analogies for what I mean by this insights-core 'just outputs rule hits' thing are Ansible Facts and Linux Environment variables.  If you run the Ansible setup module on a host (run 'ansible localhost -m setup'), you get back a JSON dictionary, called 'ansible_facts', containing a bunch of bits of data about the host you ran it on.  *But* there is nothing except the keys to tell you the meaning of those bits; no *Content*; nothing to tell you what the key 'ansible_interfaces' or the key 'ansible_virbr0_nic' actually means.  But this is *OK*, because we got the google, and there is documentation out there.  The same goes for environment variables (run 'set'); no *Content* to tell you what 'PATH' or 'PPID' means.

Such a separation will require us to think more about our choice of rule identifiers and pydata content.  They will no longer just be keys and arguments into the insights-content data, but will need to stand on their own, for longer periods of time.  We won't be able to just change the pydata because we thought of a better way to display the content.  It's not that changes to rule ids and their associated data will be impossible, but we will have to approach them more carefully because that interface will now be more public, and an unstable interface is worse than no interface at all.


**************
Fava Reference
**************

Fava is YAML plus Jinja2 expressions
====================================

Fava (like Ansible Playbooks) is a combination of YAML (yaml.org) and `Jinja2 Expressions`_.

.. _Jinja2 Expressions: http://jinja.pocoo.org/docs/2.9/templates/#expressions

The overall syntax is YAML, a Fava Rule is a YAML document.  A Fava Rule is loaded/deserialized
as a YAML document.

Certian parts of a Fava Rule can be Jinja2 Expressions (not any Jinja2 template, just Jinja2 Expressions).  In most of these parts the Jinja2 Expressions must be surrounded by double curly braces, {{ and }}, and those must be surrounded by double quotes to keep YAML happy.  Contrary to most parts, in the ``when`` pair, the Jinja2 Expression must not be surrounded double curly braces.  This is confusing till you get used to it.  It is done this way to be as much like Ansible as possible without reusing Ansible, and still get YAML and Jinja2 to work together.

When a YAML document is loaded, we loose the order in which the individual key/value pairs of a dictionary are defined.  Generally this is not a problem, but there can be an issue for the ``vars`` pair.  There may be a temptation to assume the variables in the ``vars`` pair (see below) are evaluated and defined in the order specified in the file, they are not.  You can not use a variable defined in the ``vars`` pair in the same ``vars`` pair.  See below for more information, and for how to resolve issues related to this.




The value of the ``rule`` pair, the ``name``/``pydata``/``when`` dictionary
===========================================================================

A rule consists of a dictionary containing three manditory keys: ``name``, ``pydata``, ``when``, and one optional key: ``vars``.  The keys can be in any order.

.. code-block:: yaml

  ---
  rule:
    name: "BROKEN_FLUX_CAPACITOR"
    pydata:
      kernel: "{{ Uname.kernel }}"
      fluxlevel: "{{ FluxCapacitor.level }}"
    when: FluxCapacitor.level < 42 and fluxbrand == "FarFutureInc"
    vars:
      fluxbrand: "{{ FluxCapacitor.brandname }}"

The ``name`` (the value associated with the ``name`` key) must be a string.  If the rule fires it will be passed to the ``make_result`` function.  In this example the name of the rule is ``BROKEN_FLUX_CAPACITOR``.

The ``pydata`` (the value ...) must be a dictionary.  If the rule fires, the key/value pairs will be passed as keyword arguments to the ``make_result`` function.   The keys must be strings, the values may be arbitrarys YAML values, and may contain Jinja2 expressions.  In this example, the pydata consists of two pairs, ``kernel`` and ``fluxlevel``.

The ``when`` must be a Jinja2 expression.  Its value will be treated as a boolean, exactly as Python does.  This determines when the rule fires.

The ``vars`` must be a dictionary.  The keys must be strings, the values may be arbitrarys YAML values, and may contain Jinja2 expressions.  If the values are Jinja2 expressions they will be evaluated before any other parts of the rule are evaluated.  The keys are then defined as local variables, usable in other parts of the rule.  In this example, there is only one var, ``fluxbrand``.  It is defined in the ``vars`` pair, and used in the ``when`` pair.



The ``vars``/``in`` dictionary
==============================

The ``vars``/``in`` dictionary can be used anywhere a Jinja2 expression can be used, instead of the Jinja2 expression.  It allows you to define new variables that will be available within a Jinja2 expression.

Replace the Jinja2 expression with a dictionary with two keys, ``in`` and ``vars``.  The ``vars`` pair is like the top level ``vars`` pair in a rule definition, but the variables defined in a
``vars``/``in`` dictionary are only available within the assiciated ``in`` pair.

The value of ``in`` pair must be a Jinja2 expression or another ``vars``/``in`` dictionary.

When YAML documents are loaded, the order of the key/value pairs of a dictionary is lost; dictionaries don`t have an order.

But sometimes you want to define a variable, and then use that variable to define another variable.

So in Python you might write:

.. code-block:: python

  versions_to_check = [ 'bash-3.0-19.7.el4_7.1', 'bash-3.0-21.el4', 'bash-3.0-21.el4_8.1', AND SO ON ]
  vulnerable = InstalledRpms.check_versions_installed(versions_to_check)

The ``versions_to_check`` variable is defined first, and then used in the definition of ``vulnerable``.

But in YAML we don't know the order in which the vars in a single dictionary are defined.

The following *will not* work, because the variable ``version_to_check`` is used in the same ``vars`` pair
as it is defined:

.. code-block:: yaml

  ---
  rule:
    name: "VULNERABLE_BASH_DETECTED"
    pydata:
      package: "{{ vulnerable['PACKAGES'][0] }}"
    when: vulnerable
    vars:
      versions_to_check:
        - bash-3.0-19.7.el4_7.1
        - bash-3.0-21.el4
        - bash-3.0-21.el4_8.1
        - AND SO ON
      vulnerable: '{{ InstalledRpms.check_versions_installed(versions_to_check) }}'

Instead, anytime you need to define a variable before it is used in the definition of
another variable, you need to use a ``vars``/``in`` dictionary:

.. code-block:: yaml

  ---
  rule:
    name: "VULNERABLE_BASH_DETECTED"
    pydata:
      package: "{{ vulnerable['PACKAGES'][0] }}"
    when: vulnerable
    vars:
      vulnerable:
        in: '{{ InstalledRpms.check_versions_installed(versions_to_check) }}'
        vars:
          versions_to_check:
            - bash-3.0-19.7.el4_7.1
            - bash-3.0-21.el4
            - bash-3.0-21.el4_8.1
            - AND SO ON

In the above example there is a ``vars``/``in`` dictionary nested with the toplevel ``vars`` pair.  The toplevel ``vars`` pair only defines ``vulnerable``, and the nested ``vars``/``in`` dictionary only defines the variable ``versions_to_check``.  The value of ``versions_to_check`` is evaluated first, in this case it is an array of constant strings.  The variable ``versions_to_check`` is only valid within the ``in`` pair.


.. LocalWords:  pydata
