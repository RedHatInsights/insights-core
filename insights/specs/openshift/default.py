import json
from insights import specs, datasource
from insights.core.spec_factory import DatasourceProvider
from . import GVK, foreach_resource, resource


def cr_gvk(crd):
    group = crd["spec"]["group"]
    version = crd["spec"]["version"]
    kind = crd["spec"]["names"]["kind"]
    return GVK(kind=kind, api_version="%s/%s" % (group, version))


class OpenshiftSpecsImpl(specs.Openshift):
    cluster_operators = resource(kind="ClusterOperator", api_version="config.openshift.io/v1")
    crds = resource(kind="CustomResourceDefinition", api_version="apiextensions.k8s.io/v1beta1")
    crs = foreach_resource(crds, cr_gvk)
    machine_configs = resource(kind="MachineConfig", api_version="machineconfiguration.openshift.io/v1")
    machines = resource(kind="Machine", api_version="machine.openshift.io/v1beta1")
    namespaces = resource(kind="Namespace")
    nodes = resource(kind="Node")
    pods = resource(kind="Pod", field_selector="status.phase!=Succeeded")
    pvcs = resource(kind="PersistentVolumeClaim")
    storage_classes = resource(kind="StorageClass")

    @datasource(namespaces)
    def machine_id(broker):
        doc = json.loads(broker[OpenshiftSpecsImpl.namespaces].content)
        v = next(o["metadata"]["uid"] for o in doc["items"] if o["metadata"]["name"] == "kube-system")
        return DatasourceProvider(content=v, relative_path="/etc/insights-client/machine-id")
