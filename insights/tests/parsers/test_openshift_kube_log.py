from insights.parsers.openshift_kube_log import ControllerManagerLog
from insights.parsers.openshift_kube_log import ApiServerLog
from insights.tests import context_wrap


OPENSHIFT_KUBE_LOG = """
2023-12-18T06:13:36.831359143+00:00 stderr F I1218 06:13:36.831274      16 aggregator.go:115] Building initial OpenAPI spec
2023-12-18T06:13:36.846052152+00:00 stderr F I1218 06:13:36.845970      16 aggregator.go:118] Finished initial OpenAPI spec generation after 14.671324ms
2024-12-18T06:13:37.031688793+00:00 stderr F I1218 06:13:37.031622      16 genericapiserver.go:535] "[graceful-termination] using HTTP Server shutdown timeout" ShutdownTimeout="2s"
2024-12-18T06:13:37.031809098+00:00 stderr F I1218 06:13:37.031766      16 dynamic_cafile_content.go:157] "Starting controller" name="client-ca-bundle::/etc/kubernetes/static-pod-certs/configmaps/client-ca/ca-bundle.crt"
2023-12-18T06:13:37.031901208+00:00 stderr F I1218 06:13:37.031766      16 dynamic_cafile_content.go:157] "Starting controller" name="request-header::/etc/kubernetes/static-pod-certs/configmaps/aggregator-client-ca/ca-bundle.crt"
"""


def test_openshift_kube_controller_manager_log():
    log = ControllerManagerLog(context_wrap(OPENSHIFT_KUBE_LOG))
    assert "HTTP Server shutdown timeout" in log


def test_openshift_kube_api_server_log():
    log = ApiServerLog(context_wrap(OPENSHIFT_KUBE_LOG))
    assert "Building initial OpenAPI spec" in log
