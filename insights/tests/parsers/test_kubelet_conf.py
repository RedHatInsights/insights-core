from insights.tests import context_wrap
from insights.parsers.kubelet_conf import KubeletConf


KUBELET_CONF = """
{
  "kind": "KubeletConfiguration",
  "apiVersion": "kubelet.config.k8s.io/v1beta1",
  "staticPodPath": "/etc/kubernetes/manifests",
  "syncFrequency": "0s",
  "fileCheckFrequency": "0s",
  "httpCheckFrequency": "0s",
  "tlsCipherSuites": [
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
  ],
  "tlsMinVersion": "VersionTLS12",
  "rotateCertificates": true,
  "serverTLSBootstrap": true,
  "authentication": {
    "x509": {
      "clientCAFile": "/etc/kubernetes/kubelet-ca.crt"
    },
    "webhook": {
      "cacheTTL": "0s"
    },
    "anonymous": {
      "enabled": false
    }
  },
  "authorization": {
    "webhook": {
      "cacheAuthorizedTTL": "0s",
      "cacheUnauthorizedTTL": "0s"
    }
  },
  "clusterDomain": "cluster.local",
  "clusterDNS": [
    "xx.xx.xx.xx"
  ],
  "streamingConnectionIdleTimeout": "0s",
  "nodeStatusUpdateFrequency": "10s",
  "nodeStatusReportFrequency": "5m0s",
  "imageMinimumGCAge": "2m0s",
  "imageGCHighThresholdPercent": 80,
  "imageGCLowThresholdPercent": 75,
  "volumeStatsAggPeriod": "0s",
  "systemCgroups": "/system.slice",
  "cgroupRoot": "/",
  "cgroupDriver": "systemd",
  "cpuManagerReconcilePeriod": "0s",
  "runtimeRequestTimeout": "0s",
  "maxPods": 500,
  "podPidsLimit": 4096,
  "kubeAPIQPS": 50,
  "kubeAPIBurst": 100,
  "serializeImagePulls": false,
  "evictionHard": {
    "imagefs.available": "2%",
    "imagefs.inodesFree": "2%",
    "memory.available": "200Mi",
    "nodefs.available": "2%",
    "nodefs.inodesFree": "2%"
  },
  "evictionSoft": {
    "imagefs.available": "5%",
    "imagefs.inodesFree": "5%",
    "memory.available": "500Mi",
    "nodefs.available": "5%",
    "nodefs.inodesFree": "5%"
  },
  "evictionSoftGracePeriod": {
    "imagefs.available": "1m30s",
    "imagefs.inodesFree": "1m30s",
    "memory.available": "1m30s",
    "nodefs.available": "1m30s",
    "nodefs.inodesFree": "1m30s"
  },
  "evictionPressureTransitionPeriod": "0s",
  "protectKernelDefaults": true,
  "featureGates": {
    "APIPriorityAndFairness": true,
    "DownwardAPIHugePages": true,
    "RetroactiveDefaultStorageClass": false,
    "RotateKubeletServerCertificate": true
  },
  "memorySwap": {},
  "containerLogMaxSize": "50Mi",
  "logging": {
    "flushFrequency": 0,
    "verbosity": 0,
    "options": {
      "json": {
        "infoBufferSize": "0"
      }
    }
  },
  "shutdownGracePeriod": "0s",
  "shutdownGracePeriodCriticalPods": "0s"
}
""".strip()


def test_kubelet_conf():
    conf = KubeletConf(context_wrap(KUBELET_CONF))
    assert conf.data['kind'] == "KubeletConfiguration"
    assert len(conf.data.keys()) == 42
    assert conf.data['featureGates']['DownwardAPIHugePages'] is True
