from insights.parsers import openshift_get_with_config, ParseException
from insights.parsers.openshift_get_with_config import OcGetClusterRoleWithConfig, OcGetClusterRoleBindingWithConfig
from insights.tests import context_wrap
import doctest
import pytest

OC_GET_CLUSTER_ROLE = """
NAME
admin
asb-access
asb-auth
basic-user
cluster-admin
cluster-debugger
cluster-reader
cluster-status
edit
hawkular-metrics-admin
management-infra-admin
namespace-viewer
registry-admin
registry-editor
registry-viewer
rolebinding-reader
sar-creator
self-access-reviewer
self-provisioner
service-catalog-controller
servicecatalog-serviceclass-viewer
storage-admin
sudoer
system:aggregate-to-admin
system:aggregate-to-edit
system:aggregate-to-view
system:auth-delegator
system:aws-cloud-provider
system:basic-user
system:build-controller
system:build-strategy-custom
system:build-strategy-docker
system:build-strategy-jenkinspipeline
system:build-strategy-source
system:certificate-signing-controller
system:certificates.k8s.io:certificatesigningrequests:nodeclient
system:certificates.k8s.io:certificatesigningrequests:selfnodeclient
system:controller:attachdetach-controller
system:controller:certificate-controller
system:controller:clusterrole-aggregation-controller
system:controller:cronjob-controller
system:controller:daemon-set-controller
system:controller:deployment-controller
system:controller:disruption-controller
system:controller:endpoint-controller
system:controller:generic-garbage-collector
system:controller:horizontal-pod-autoscaler
system:controller:job-controller
system:controller:namespace-controller
system:controller:node-controller
system:controller:persistent-volume-binder
system:controller:pod-garbage-collector
system:controller:replicaset-controller
system:controller:replication-controller
system:controller:resourcequota-controller
system:controller:route-controller
system:controller:service-account-controller
system:controller:service-controller
system:controller:statefulset-controller
system:controller:ttl-controller
system:daemonset-controller
system:deployer
system:deployment-controller
system:deploymentconfig-controller
system:discovery
system:disruption-controller
system:endpoint-controller
system:garbage-collector-controller
system:gc-controller
system:heapster
system:hpa-controller
system:image-auditor
system:image-builder
system:image-pruner
system:image-puller
system:image-pusher
system:image-signer
system:job-controller
system:kube-aggregator
system:kube-controller-manager
system:kube-dns
system:kube-scheduler
system:master
system:namespace-controller
system:node
system:node-admin
system:node-bootstrapper
system:node-problem-detector
system:node-proxier
system:node-reader
system:oauth-token-deleter
system:openshift:aggregate-to-admin
system:openshift:aggregate-to-edit
system:openshift:aggregate-to-view
system:openshift:controller:build-config-change-controller
system:openshift:controller:build-controller
system:openshift:controller:cluster-quota-reconciliation-controller
system:openshift:controller:deployer-controller
system:openshift:controller:deploymentconfig-controller
system:openshift:controller:horizontal-pod-autoscaler
system:openshift:controller:image-import-controller
system:openshift:controller:image-trigger-controller
system:openshift:controller:origin-namespace-controller
system:openshift:controller:pv-recycler-controller
system:openshift:controller:resourcequota-controller
system:openshift:controller:sdn-controller
system:openshift:controller:service-ingress-ip-controller
system:openshift:controller:service-serving-cert-controller
system:openshift:controller:serviceaccount-controller
system:openshift:controller:serviceaccount-pull-secrets-controller
system:openshift:controller:template-instance-controller
system:openshift:controller:template-service-broker
system:openshift:controller:unidling-controller
system:openshift:templateservicebroker-client
system:persistent-volume-provisioner
system:registry
system:replicaset-controller
system:replication-controller
system:router
system:scope-impersonation
system:sdn-manager
system:sdn-reader
system:service-catalog:aggregate-to-admin
system:service-catalog:aggregate-to-edit
system:service-catalog:aggregate-to-view
system:statefulset-controller
system:webhook
view
""".strip()

OC_GET_CLUSTERROLEBINDING = """
NAME                                                                  ROLE                                                                   USERS                            GROUPS                                         SERVICE ACCOUNTS                                                                   SUBJECTS
admin                                                                 /admin                                                                                                                                                 openshift-infra/template-instance-controller
admin-0                                                               /admin                                                                                                                                                 kube-service-catalog/default
admin-1                                                               /admin                                                                                                                                                 openshift-ansible-service-broker/asb
asb-access                                                            /asb-access                                                                                                                                            openshift-ansible-service-broker/asb-client
asb-auth                                                              /asb-auth                                                                                                                                              openshift-ansible-service-broker/asb
auth-delegator-openshift-template-service-broker                      /system:auth-delegator                                                                                                                                 openshift-template-service-broker/apiserver
basic-users                                                           /basic-user                                                                                             system:authenticated
cluster-admin                                                         /cluster-admin                                                                                          system:masters
cluster-admin-0                                                       /cluster-admin                                                                                                                                         insights-scan/insights-scan
cluster-admins                                                        /cluster-admin
""".strip()

OC_GET_CLUSTERROLEBINDING_INVALID = """
NAME                                                                  ROLE                                                                   USERS                            GROUPS                                         SERVICE ACCOUNTS                                                                   SUBJECTS
admin
admin-0                                                               /admin                                                                                                                                                 kube-service-catalog/default
admin-1                                                               /admin                                                                                                                                                 openshift-ansible-service-broker/asb
asb-access                                                            /asb-access                                                                                                                                            openshift-ansible-service-broker/asb-client
asb-auth                                                              /asb-auth                                                                                                                                              openshift-ansible-service-broker/asb
auth-delegator-openshift-template-service-broker                      /system:auth-delegator                                                                                                                                 openshift-template-service-broker/apiserver
basic-users                                                           /basic-user                                                                                             system:authenticated
cluster-admin                                                         /cluster-admin                                                                                          system:masters
cluster-admin-0                                                       /cluster-admin                                                                                                                                         insights-scan/insights-scan
cluster-admins                                                        /cluster-admin
""".strip()

OC_GET_CLUSTERROLEBINDING_INVALID2 = """
admin-0                                                               /admin                                                                                                                                                 kube-service-catalog/default
admin-1                                                               /admin                                                                                                                                                 openshift-ansible-service-broker/asb
asb-access                                                            /asb-access                                                                                                                                            openshift-ansible-service-broker/asb-client
asb-auth                                                              /asb-auth                                                                                                                                              openshift-ansible-service-broker/asb
auth-delegator-openshift-template-service-broker                      /system:auth-delegator                                                                                                                                 openshift-template-service-broker/apiserver
basic-users                                                           /basic-user                                                                                             system:authenticated
cluster-admin                                                         /cluster-admin                                                                                          system:masters
cluster-admin-0                                                       /cluster-admin                                                                                                                                         insights-scan/insights-scan
cluster-admins                                                        /cluster-admin
""".strip()

OC_GET_CLUSTER_ROLE_INVALID = """
name
admin
""".strip()


def test_oc_get_cluster_role_with_config():
    result = openshift_get_with_config.OcGetClusterRoleWithConfig(context_wrap(OC_GET_CLUSTER_ROLE))
    assert result.data[0] == "admin"
    assert "admin" in result
    assert result[0] == "admin"


def test_oc_get_cluster_role_with_config_2():
    with pytest.raises(ParseException) as e:
        openshift_get_with_config.OcGetClusterRoleWithConfig(context_wrap(OC_GET_CLUSTER_ROLE_INVALID))
    assert "invalid" in str(e)


def test_oc_get_clusterrolebinding_with_config():
    result = openshift_get_with_config.OcGetClusterRoleBindingWithConfig(context_wrap(OC_GET_CLUSTERROLEBINDING))
    assert result.rolebinding["admin"] == "/admin"
    assert result.data == [{'NAME': 'admin', 'ROLE': '/admin', 'USERS': '', 'GROUPS': '',
                            'SERVICE_ACCOUNTS': 'openshift-infra/template-instance-controller', 'SUBJECTS': ''},
                           {'NAME': 'admin-0', 'ROLE': '/admin', 'USERS': '', 'GROUPS': '',
                            'SERVICE_ACCOUNTS': 'kube-service-catalog/default', 'SUBJECTS': ''},
                           {'NAME': 'admin-1', 'ROLE': '/admin', 'USERS': '', 'GROUPS': '',
                            'SERVICE_ACCOUNTS': 'openshift-ansible-service-broker/asb', 'SUBJECTS': ''},
                           {'NAME': 'asb-access', 'ROLE': '/asb-access', 'USERS': '', 'GROUPS': '',
                            'SERVICE_ACCOUNTS': 'openshift-ansible-service-broker/asb-client', 'SUBJECTS': ''},
                           {'NAME': 'asb-auth', 'ROLE': '/asb-auth', 'USERS': '', 'GROUPS': '',
                            'SERVICE_ACCOUNTS': 'openshift-ansible-service-broker/asb', 'SUBJECTS': ''},
                           {'NAME': 'auth-delegator-openshift-template-service-broker',
                            'ROLE': '/system:auth-delegator', 'USERS': '', 'GROUPS': '',
                            'SERVICE_ACCOUNTS': 'openshift-template-service-broker/apiserver', 'SUBJECTS': ''},
                           {'NAME': 'basic-users', 'ROLE': '/basic-user', 'USERS': '', 'GROUPS': 'system:authenticated',
                            'SERVICE_ACCOUNTS': '', 'SUBJECTS': ''},
                           {'NAME': 'cluster-admin', 'ROLE': '/cluster-admin', 'USERS': '', 'GROUPS': 'system:masters',
                            'SERVICE_ACCOUNTS': '', 'SUBJECTS': ''},
                           {'NAME': 'cluster-admin-0', 'ROLE': '/cluster-admin', 'USERS': '', 'GROUPS': '',
                            'SERVICE_ACCOUNTS': 'insights-scan/insights-scan', 'SUBJECTS': ''},
                           {'NAME': 'cluster-admins', 'ROLE': '/cluster-admin', 'USERS': '', 'GROUPS': '',
                            'SERVICE_ACCOUNTS': '', 'SUBJECTS': ''}]


def test_oc_get_clusterrolebinding_with_config_3():
    with pytest.raises(ParseException) as e:
        openshift_get_with_config.OcGetClusterRoleBindingWithConfig(context_wrap(OC_GET_CLUSTERROLEBINDING_INVALID2))
    assert "invalid content" in str(e)


def test_doc():
    env = {
        'oc_get_cluster_role_with_config': OcGetClusterRoleWithConfig(
            context_wrap(OC_GET_CLUSTER_ROLE)),
        'oc_get_clusterrolebinding_with_config': OcGetClusterRoleBindingWithConfig(
            context_wrap(OC_GET_CLUSTERROLEBINDING)),
    }
    failed, total = doctest.testmod(openshift_get_with_config, globs=env)
    assert failed == 0
