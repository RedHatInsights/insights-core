import yaml
from insights.core.plugins import datasource
from insights.specs import Specs
from insights.specs.openshift import (openshift_resource, OpenshiftClient,
        OpenshiftOutputProvider)


class OpenshiftSpecs(Specs):
    openshift_namespaces = openshift_resource(kind="Namespace")
    openshift_nodes = openshift_resource(kind="Node")
    openshift_crds = openshift_resource(kind="CustomResourceDefinition", api_version="apiextensions.k8s.io/v1beta1")

    @datasource(openshift_crds, OpenshiftClient)
    def k8s_crs(broker):
        client = broker[OpenshiftClient]
        cr_list = []
        for crd in yaml.safe_load(broker[OpenshiftSpecs.openshift_crds].content)["items"]:
            group = crd["spec"]["group"]
            version = crd["spec"]["version"]
            kind = crd["spec"]["names"]["kind"]
            cr_list.append(OpenshiftOutputProvider(client, api_version="%s/%s" % (group, version), kind=kind))
        return cr_list
