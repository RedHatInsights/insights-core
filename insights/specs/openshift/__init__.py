import json
import logging
import os

from kubernetes import config
from kubernetes.client import ApiClient, Configuration
from openshift.dynamic import DynamicClient

from insights.core.context import ExecutionContext
from insights.core.plugins import datasource
from insights.core.serde import deserializer, serializer
from insights.core.spec_factory import ContentProvider, SerializedRawOutputProvider
from insights.util import fs

log = logging.getLogger(__name__)


class GVK(object):
    def __init__(self, kind, api_version="v1", kwargs=None):
        self.kind = kind
        self.api_version = api_version
        self.kwargs = kwargs or {}


class OpenshiftOutputProvider(ContentProvider):
    def __init__(self, client, kind=None, api_version=None, **kwargs):
        super(OpenshiftOutputProvider, self).__init__()
        self.kind = kind
        self.api_version = api_version
        name = "%s/%s" % (self.api_version, self.kind)
        self.gvk = name.split("/")
        self.relative_path = name
        self.root = "/"
        self.kwargs = kwargs
        self.k8s = client.k8s

    def load(self):
        return self.k8s.resources.get(kind=self.kind, api_version=self.api_version).get(serialize=False, **self.kwargs).data

    def write(self, dst):
        fs.ensure_path(os.path.dirname(dst))
        with open(dst, "wb") as f:
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


client = OpenshiftClient()


class resource(object):
    client_kwargs = None
    timeout = None

    def __init__(self, kind, api_version="v1", **kwargs):
        # encode group into the api_version string if necessary
        self.static_kwargs = kwargs
        self.kind = kind
        self.api_version = api_version
        self.__name__ = self.__class__.__name__
        datasource(OpenshiftContext)(self)

    def __call__(self, broker):
        # allow manifest to override what's in the resource definition
        ctx = broker[OpenshiftContext]
        timeout = self.timeout or ctx.timeout
        kwargs = dict(self.client_kwargs if self.client_kwargs is not None else self.static_kwargs)
        if timeout:
            kwargs["timeout_seconds"] = timeout
        return OpenshiftOutputProvider(client, kind=self.kind, api_version=self.api_version, **kwargs)


class foreach_resource(object):
    client_kwargs = None
    timeout = None

    def __init__(self, dep, func):
        self.dep = dep
        self.func = func
        self.__name__ = self.__class__.__name__
        datasource(OpenshiftContext, dep)(self)

    def __call__(self, broker):
        # allow manifest to override what's in the resource definition
        ctx = broker[OpenshiftContext]
        timeout = self.timeout or ctx.timeout
        crds = broker[self.dep]
        _lst = []
        for crd in json.loads(crds.content)["items"]:
            gvk = self.func(crd)
            kwargs = dict(self.client_kwargs if self.client_kwargs is not None else gvk.kwargs)
            if timeout:
                kwargs["timeout_seconds"] = timeout
            _lst.append(OpenshiftOutputProvider(client, kind=gvk.kind, api_version=gvk.api_version, **kwargs))
        return _lst
