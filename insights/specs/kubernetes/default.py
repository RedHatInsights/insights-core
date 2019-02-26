import yaml
from insights.core.plugins import datasource
from insights.specs import Specs
from insights.specs.kubernetes import (kube_resource, KubeClient,
        KubeOutputProvider)


class KubeSpecs(Specs):
    k8s_namespaces = kube_resource(kind="Namespace")
    k8s_nodes = kube_resource(kind="Node")
    k8s_crds = kube_resource(kind="CustomResourceDefinition", api_version="apiextensions.k8s.io/v1beta1")

    @datasource(crds, KubeClient)
    def k8s_crs(broker):
        client = broker[KubeClient]
        cr_list = []
        for crd in yaml.safe_load(broker[KubeSpecs.crds].content)["items"]:
            group = crd["spec"]["group"]
            version = crd["spec"]["version"]
            kind = crd["spec"]["names"]["kind"]
            cr_list.append(KubeOutputProvider(client, api_version="%s/%s" % (group, version), kind=kind))
        return cr_list
