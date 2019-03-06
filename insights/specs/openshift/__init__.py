import os
import json

from kubernetes import config
from kubernetes.client import ApiClient, Configuration
from openshift.dynamic import DynamicClient

from insights.core.context import ExecutionContext
from insights.core.plugins import component, datasource
from insights.core.serde import deserializer, serializer
from insights.core.spec_factory import ContentProvider, SerializedRawOutputProvider
from insights.util import fs


class OpenshiftOutputProvider(ContentProvider):
    def __init__(self, client, **client_kwargs):
        super(OpenshiftOutputProvider, self).__init__()
        name = "%s/%s" % (client_kwargs["api_version"], client_kwargs["kind"])
        self.gvk = name.split("/")
        self.relative_path = name
        self.root = "/"
        self.client_kwargs = client_kwargs
        self.k8s = client.k8s

    def load(self):
        doc = self.k8s.resources.get(**self.client_kwargs).get().to_dict()
        return json.dumps(doc)

    def write(self, dst):
        fs.ensure_path(os.path.dirname(dst))
        with open(dst, "w") as f:
            f.write(self.content)

        # we're done with it if we're writing it down.
        # reset _content so we don't build up memory
        self.loaded = False
        self._content = None


@serializer(OpenshiftOutputProvider)
def serialize_openshift_output(obj, root):
    rel = os.path.join("k8s", *obj.gvk)
    dst = os.path.join(root, rel)
    fs.ensure_path(os.path.dirname(dst))
    obj.write(dst)
    return {"relative_path": rel}


@deserializer(OpenshiftOutputProvider)
def deserialize_openshift_output(_type, data, root):
    rel = data["relative_path"]
    res = SerializedRawOutputProvider(rel, root)
    return res


class OpenshiftContext(ExecutionContext):
    pass


@component(OpenshiftContext)
class OpenshiftClient(object):
    def __init__(self, ctx=None, cfg=None):
        cfg = cfg or os.environ.get("KUBECONFIG")
        if cfg:
            k8s_client = config.new_client_from_config(cfg)
        else:
            config.load_incluster_config()  # makes a singleton config behind the scenes
            k8cfg = Configuration()  # gets a copy from what was populated in the line above
            # NOTE this is required due to https://github.com/openshift/origin/issues/22125
            k8cfg.verify_ssl = False
            k8s_client = ApiClient(configuration=k8cfg)  # this should use the singleton produced above
        self.k8s = DynamicClient(k8s_client)  # stole this from config.new_client_from_config


class resource(object):
    def __init__(self, kind, api_version="v1", **kwargs):
        # encode group into the api_version string if necessary
        self.client_kwargs = kwargs
        self.client_kwargs["kind"] = kind
        self.client_kwargs["api_version"] = api_version
        self.__name__ = self.__class__.__name__
        datasource(OpenshiftClient)(self)

    def __call__(self, broker):
        client = broker[OpenshiftClient]
        return OpenshiftOutputProvider(client, **self.client_kwargs)
