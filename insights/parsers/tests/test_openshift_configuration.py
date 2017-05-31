from insights.parsers import openshift_configuration
from insights.tests import context_wrap

NODE_CONFIG = """
allowDisabledDocker: false
apiVersion: v1
dnsDomain: cluster.local
dnsIP: 10.66.208.145
dockerConfig:
  execHandlerName: ""
iptablesSyncPeriod: "30s"
imageConfig:
  format: openshift3/ose-${component}:${version}
  latest: false
kind: NodeConfig
kubeletArguments:
  node-labels: []
masterClientConnectionOverrides:
  acceptContentTypes: application/vnd.kubernetes.protobuf,application/json
  contentType: application/vnd.kubernetes.protobuf
  burst: 200
  qps: 100
masterKubeConfig: system:node:master.ose.com.kubeconfig
networkPluginName: redhat/openshift-ovs-subnet
# networkConfig struct introduced in origin 1.0.6 and OSE 3.0.2 which
# deprecates networkPluginName above. The two should match.
networkConfig:
   mtu: 1450
   networkPluginName: redhat/openshift-ovs-subnet
nodeName: master.ose.com
podManifestConfig:
servingInfo:
  bindAddress: 0.0.0.0:10250
  certFile: server.crt
  clientCA: ca.crt
  keyFile: server.key
volumeDirectory: /var/lib/origin/openshift.local.volumes
proxyArguments:
  proxy-mode:
     - iptables
volumeConfig:
  localQuota:
    perFSGroup:
"""

MASTER_CONFIG = """
admissionConfig:
apiLevels:
- v1
apiVersion: v1
assetConfig:
  logoutURL: ""
  masterPublicURL: https://master.ose.com:8443
  publicURL: https://master.ose.com:8443/console/
  servingInfo:
    bindAddress: 0.0.0.0:8443
    bindNetwork: tcp4
    certFile: master.server.crt
    clientCA: ""
    keyFile: master.server.key
    maxRequestsInFlight: 0
    requestTimeoutSeconds: 0
controllerConfig:
  serviceServingCert:
    signer:
      certFile: service-signer.crt
      keyFile: service-signer.key
controllers: '*'
corsAllowedOrigins:
  - 127.0.0.1
  - localhost
  - 10.66.208.145
  - kubernetes.default
  - kubernetes.default.svc.cluster.local
  - kubernetes
  - openshift.default
  - openshift.default.svc
  - 172.30.0.1
  - master.ose.com
  - openshift.default.svc.cluster.local
  - kubernetes.default.svc
  - openshift
dnsConfig:
  bindAddress: 0.0.0.0:8053
  bindNetwork: tcp4
etcdClientInfo:
  ca: master.etcd-ca.crt
  certFile: master.etcd-client.crt
  keyFile: master.etcd-client.key
  urls:
    - https://master.ose.com:2379
etcdStorageConfig:
  kubernetesStoragePrefix: kubernetes.io
  kubernetesStorageVersion: v1
  openShiftStoragePrefix: openshift.io
  openShiftStorageVersion: v1
imageConfig:
  format: openshift3/ose-${component}:${version}
  latest: false
kind: MasterConfig
kubeletClientInfo:
  ca: ca.crt
  certFile: master.kubelet-client.crt
  keyFile: master.kubelet-client.key
  port: 10250
kubernetesMasterConfig:
  apiServerArguments:
  controllerArguments:
  masterCount: 1
  masterIP: 10.66.208.145
  podEvictionTimeout:
  proxyClientInfo:
    certFile: master.proxy-client.crt
    keyFile: master.proxy-client.key
  schedulerArguments:
  schedulerConfigFile: /etc/origin/master/scheduler.json
  servicesNodePortRange: ""
  servicesSubnet: 172.30.0.0/16
  staticNodeNames: []
masterClients:
  externalKubernetesClientConnectionOverrides:
    acceptContentTypes: application/vnd.kubernetes.protobuf,application/json
    contentType: application/vnd.kubernetes.protobuf
    burst: 400
    qps: 200
  externalKubernetesKubeConfig: ""
  openshiftLoopbackClientConnectionOverrides:
    acceptContentTypes: application/vnd.kubernetes.protobuf,application/json
    contentType: application/vnd.kubernetes.protobuf
    burst: 600
    qps: 300
  openshiftLoopbackKubeConfig: openshift-master.kubeconfig
masterPublicURL: https://master.ose.com:8443
networkConfig:
  clusterNetworkCIDR: 10.128.0.0/14
  hostSubnetLength: 9
  networkPluginName: redhat/openshift-ovs-subnet
# serviceNetworkCIDR must match kubernetesMasterConfig.servicesSubnet
  serviceNetworkCIDR: 172.30.0.0/16
  externalIPNetworkCIDRs:
  - 0.0.0.0/0
oauthConfig:
  assetPublicURL: https://master.ose.com:8443/console/
  grantConfig:
    method: auto
  identityProviders:
  - challenge: true
    login: true
    mappingMethod: claim
    name: deny_all
    provider:
      apiVersion: v1
      kind: DenyAllPasswordIdentityProvider
  masterCA: ca-bundle.crt
  masterPublicURL: https://master.ose.com:8443
  masterURL: https://master.ose.com:8443
  sessionConfig:
    sessionMaxAgeSeconds: 3600
    sessionName: ssn
    sessionSecretsFile: /etc/origin/master/session-secrets.yaml
  tokenConfig:
    accessTokenMaxAgeSeconds: 86400
    authorizeTokenMaxAgeSeconds: 500
pauseControllers: false
policyConfig:
  bootstrapPolicyFile: /etc/origin/master/policy.json
  openshiftInfrastructureNamespace: openshift-infra
  openshiftSharedResourcesNamespace: openshift
projectConfig:
  defaultNodeSelector: ""
  projectRequestMessage: ""
  projectRequestTemplate: ""
  securityAllocator:
    mcsAllocatorRange: "s0:/2"
    mcsLabelsPerProject: 5
    uidAllocatorRange: "1000000000-1999999999/10000"
routingConfig:
  subdomain:  ""
serviceAccountConfig:
  limitSecretReferences: false
  managedNames:
  - default
  - builder
  - deployer
  masterCA: ca-bundle.crt
  privateKeyFile: serviceaccounts.private.key
  publicKeyFiles:
  - serviceaccounts.public.key
servingInfo:
  bindAddress: 0.0.0.0:8443
  bindNetwork: tcp4
  certFile: master.server.crt
  clientCA: ca.crt
  keyFile: master.server.key
  maxRequestsInFlight: 500
  requestTimeoutSeconds: 3600
volumeConfig:
  dynamicProvisioningEnabled: True
"""


def test_ose_node_config():
    result = openshift_configuration.OseMasterConfig(context_wrap(MASTER_CONFIG))
    assert result.data['assetConfig']['masterPublicURL'] == 'https://master.ose.com:8443'
    assert result.data['corsAllowedOrigins'][1] == 'localhost'
    assert result.data['projectConfig']['defaultNodeSelector'] == ""


def test_ose_master_config():
    result = openshift_configuration.OseNodeConfig(context_wrap(NODE_CONFIG))
    assert result.data['apiVersion'] == "v1"
    assert result.data['masterClientConnectionOverrides']['burst'] == 200
