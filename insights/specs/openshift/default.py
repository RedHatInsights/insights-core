from insights import specs
from . import GVK, foreach_resource, resource


def cr_gvk(crd):
    group = crd["spec"]["group"]
    version = crd["spec"]["version"]
    kind = crd["spec"]["names"]["kind"]
    return GVK(kind=kind, api_version="%s/%s" % (group, version))


class OpenshiftSpecsImpl(specs.Openshift):
    namespaces = resource(kind="Namespace")
    nodes = resource(kind="Node")
    pods = resource(kind="Pod", field_selector="status.phase!=Succeeded")
    cluster_operators = resource(kind="ClusterOperator", api_version="config.openshift.io/v1")
    machines = resource(kind="Machine", api_version="machine.openshift.io/v1beta1")
    machine_configs = resource(kind="MachineConfig", api_version="machineconfiguration.openshift.io/v1")
    crds = resource(kind="CustomResourceDefinition", api_version="apiextensions.k8s.io/v1beta1")

    crs = foreach_resource(crds, cr_gvk)
