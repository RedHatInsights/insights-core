############
INVENTORY(5)
############

NAME
====

    inventory - inventory configuration file for insights-run execution

SYNOPSIS
========

    **filename.yaml**

DESCRIPTION
===========

The inventory file provides configuration of information for a collection of
systems.  The format of the file is `Ansible Host File`_ format.

EXAMPLES
========

A complete example of a configuration file in YAML format::

    # Insights core cluster rules topology file
    # in Ansible host file format
    # See: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#hosts-and-groups
    #
    # machine id's are listed under each [category] of systems
    [master]
    11111111


    [infra]
    2222222

    [nodes]
    3333333
    4444444

SEE ALSO
========

    :doc:`insights-run(1) <./insights-run>`

.. Reference links

.. _Ansible Host File: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#hosts-and-groups