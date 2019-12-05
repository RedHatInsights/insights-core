Openshift 4 Analysis
====================
OpenShift 4 can generate diagnostic archives with a component called the
``insights-operator``.  They are automatically uploaded to Red Hat for analysis.

The openshift-must-gather_ CLI tool produces more comprehensive archives than
the operator. ``insights-core`` recognizes them as well.

If you have an insights-operator or must-gather archive, you can write rules
for it by using the :py:func:`insights.ocp.ocp` component, which gives you a
top level view of **all** of the collected cluster configuration in a form
that's easy to `navigate and query`_.

You can access the entire configuration iteractively with ``insights inspect
insights.ocp.ocp <archive>`` or ``insights ocpshell <archive>``.

.. _openshift-must-gather: https://github.com/openshift/must-gather
.. _navigate and query: https://insights-core.readthedocs.io/en/latest/notebooks/Parsr%20Query%20Tutorial.html

.. automodule:: insights.ocp
   :members:
   :show-inheritance:
