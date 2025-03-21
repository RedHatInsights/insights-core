"""
Container logs
==============

Module for parsing the log files for Openshift kubelet container logs.


ControllerManagerLog - file ``/var/log/pods/openshift-kube-controller-manager*/*/*.log``
----------------------------------------------------------------------------------------

ApiServerLog - file ``/var/log/pods/openshift-kube-apiserver*/*/*.log``
-----------------------------------------------------------------------

.. note::
    Please refer to the super-class :class:`insights.core.LogFileOutput`
"""

from insights import LogFileOutput, parser
from insights.specs import Specs


@parser(Specs.controller_manager_log)
class ControllerManagerLog(LogFileOutput):
    """Class for parsing ``/var/log/pods/openshift-kube-controller-manager*/*/*.log`` file.

    Typical content of ``*.log`` file is::

        2023-12-18T06:13:36.831359143+00:00 stderr F I1218 06:13:36.831274      16 aggregator.go:115] Building initial OpenAPI spec
        2023-12-18T06:13:36.846052152+00:00 stderr F I1218 06:13:36.845970      16 aggregator.go:118] Finished initial OpenAPI spec generation after 14.671324ms
        2024-12-18T06:13:37.031688793+00:00 stderr F I1218 06:13:37.031622      16 genericapiserver.go:535] "[graceful-termination] using HTTP Server shutdown timeout" ShutdownTimeout="2s"
        2024-12-18T06:13:37.031809098+00:00 stderr F I1218 06:13:37.031766      16 dynamic_cafile_content.go:157] "Starting controller" name="client-ca-bundle::/etc/kubernetes/static-pod-certs/configmaps/client-ca/ca-bundle.crt"
        2023-12-18T06:13:37.031901208+00:00 stderr F I1218 06:13:37.031766      16 dynamic_cafile_content.go:157] "Starting controller" name="request-header::/etc/kubernetes/static-pod-certs/configmaps/aggregator-client-ca/ca-bundle.crt"
    """
    time_format = '%Y-%m-%dT%H:%M:%S.%f'


@parser(Specs.api_server_log)
class ApiServerLog(LogFileOutput):
    """Class for parsing ``var/log/pods/openshift-kube-apiserver*/*/*.log`` file.

    Typical content of ``*.log`` file is::

        2023-12-18T06:13:36.831359143+00:00 stderr F I1218 06:13:36.831274      16 aggregator.go:115] Building initial OpenAPI spec
        2023-12-18T06:13:36.846052152+00:00 stderr F I1218 06:13:36.845970      16 aggregator.go:118] Finished initial OpenAPI spec generation after 14.671324ms
        2024-12-18T06:13:37.031688793+00:00 stderr F I1218 06:13:37.031622      16 genericapiserver.go:535] "[graceful-termination] using HTTP Server shutdown timeout" ShutdownTimeout="2s"
        2024-12-18T06:13:37.031809098+00:00 stderr F I1218 06:13:37.031766      16 dynamic_cafile_content.go:157] "Starting controller" name="client-ca-bundle::/etc/kubernetes/static-pod-certs/configmaps/client-ca/ca-bundle.crt"
        2023-12-18T06:13:37.031901208+00:00 stderr F I1218 06:13:37.031766      16 dynamic_cafile_content.go:157] "Starting controller" name="request-header::/etc/kubernetes/static-pod-certs/configmaps/aggregator-client-ca/ca-bundle.crt"
    """
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
