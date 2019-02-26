import yaml
from insights.core.plugins import datasource
from insights.core.spec_factory import SpecSet
from insights.specs.kubernetes import (kube_resource, KubeClient,
        KubeOutputProvider)


class KubeSpecs(SpecSet):
    ns_info = kube_resource(kind="Namespace")
    nodes = kube_resource(kind="Node")
    crds = kube_resource(kind="CustomResourceDefinition", api_version="apiextensions.k8s.io/v1beta1")

    @datasource(crds, KubeClient)
    def crs(broker):
        client = broker[KubeClient]
        cr_list = []
        for crd in yaml.safe_load(broker[KubeSpecs.crds].content)["items"]:
            group = crd["spec"]["group"]
            version = crd["spec"]["version"]
            kind = crd["spec"]["names"]["kind"]
            cr_list.append(KubeOutputProvider(client, api_version="%s/%s" % (group, version), kind=kind))
        return cr_list
