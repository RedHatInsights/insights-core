Plan out your Rule
------------------

Determine rule logic
====================

The most effective way to get started in developing a rule is identifying the
problem you want to address as well as a succinct solution to that problem.

For the purposes of this tutorial we'll identify a fictitious security problem
with a commonly shared library.  Let's imagine that this is a highly publicized
CVE, and, therefore, it deserves a catchy name; let's call it Heartburn.

For this case let's check three things:

1. the shared library is installed on the system
2. the shared library is in use by a running process
3. the running process is accepting possibly external network connections

For this problem let's declare that the solution is to upgrade the shared
library and restart the system.


Identify Parsers
================

- For RPM-based distributions, we can identify the installed version of the
  library by using the ``installed-rpms`` parser.

- We can use the ``lsof`` parser to identify if a running process is using the
  shared library.

- We can use the ``netstat`` parser to identify if a running process is
  possibly listening on an external address.
