Plan out your Rule
------------------

Determine rule logic
====================

The most effective way to get started in developing a rule is first to identify the
problem you want to address.

For the purposes of this tutorial we'll look at a very simple scenario. Sometimes when
researching an issue one of the things that we might need to know is which Red Hat OS the
host is running. For simplicity sake, in this example we will concentrate only on
determining if the red hat release is ``Fedora``.

For this case there is one thing we need to check:

1. Is the Red Hat release ``Fedora``:


Identify Parsers
================

- We can check Red Hat Release using the ``RedhatRelease`` parser.

