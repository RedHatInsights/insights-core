Plan out your Rule
------------------

Determine rule logic
====================

The most effective way to get started in developing a rule is identifying the
problem you want to address as well as a succinct solution to that problem.

For the purposes of this tutorial we'll identify a very simple problem with
the rpm database getting corrupted. The RPM Database is critical for managing
packages on a system. It's possible for this databse to become corrupt therefore
making updates and software installs impossible.

For this case there is one thing we need to check:

1. the rpm database does not contain `rpmdbNextIterator:`

For this problem let's declare that the solution is to rebuild rpm database or
restore from backup.


Identify Parsers
================

- We can check the contents o the rpm database by using the ``InstalledRpms`` parser.

