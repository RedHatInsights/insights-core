import json
from insights.core.plugins import datasource
from insights import specs
from . import (resource, OpenshiftClient,
        OpenshiftOutputProvider)


class OpenshiftSpecsImpl(specs.Openshift):
    namespaces = resource(kind="Namespace")
    nodes = resource(kind="Node")
    pods = resource(kind="Pod")
    cluster_operators = resource(kind="ClusterOperator", api_version="config.openshift.io/v1")
    machines = resource(kind="Machine", api_version="machine.openshift.io/v1beta1")
    machine_configs = resource(kind="MachineConfig", api_version="machineconfiguration.openshift.io/v1")
    crds = resource(kind="CustomResourceDefinition", api_version="apiextensions.k8s.io/v1beta1")

    @datasource(crds)
    def crs(broker):
        client = OpenshiftClient()
        cr_list = []
        for crd in json.loads(broker[OpenshiftSpecsImpl.crds].content)["items"]:
            group = crd["spec"]["group"]
            version = crd["spec"]["version"]
            kind = crd["spec"]["names"]["kind"]
            cr_list.append(OpenshiftOutputProvider(client, api_version="%s/%s" % (group, version), kind=kind))
        return cr_list
