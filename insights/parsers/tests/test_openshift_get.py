from insights.parsers import openshift_get
from insights.tests import context_wrap
import datetime
import doctest

OC_GET_POD = """
apiVersion: v1
items:
- apiVersion: v1
  kind: Pod
  metadata:
    annotations:
      openshift.io/scc: anyuid
    creationTimestamp: 2017-02-10T16:33:46Z
    labels:
      name: hello-openshift
    name: hello-pod
    namespace: default
  spec:
    containers:
    - image: openshift/hello-openshift
      imagePullPolicy: IfNotPresent
      name: hello-openshift
      ports:
      - containerPort: 8080
        protocol: TCP
      resources: {}
      securityContext:
        capabilities:
          drop:
          - MKNOD
          - SYS_CHROOT
        privileged: false
        seLinuxOptions:
          level: s0:c5,c0
      terminationMessagePath: /dev/termination-log
      volumeMounts:
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: default-token-yk69f
        readOnly: true
    dnsPolicy: ClusterFirst
    host: node2.ose.com
    imagePullSecrets:
    - name: default-dockercfg-h7sl1
    nodeName: node2.ose.com
    restartPolicy: Always
    securityContext:
      seLinuxOptions:
        level: s0:c5,c0
    serviceAccount: default
    serviceAccountName: default
    terminationGracePeriodSeconds: 30
    volumes:
    - name: default-token-yk69f
      secret:
        secretName: default-token-yk69f
  status:
    conditions:
    - lastProbeTime: null
      lastTransitionTime: 2017-02-10T16:33:46Z
      status: "True"
      type: Initialized
    containerStatuses:
    - containerID: docker://a172a6945e207c0fd1c391cad31ccb76bc8323f3f024a50b5ba287034302853f
      image: openshift/hello-openshift
      imageID: docker-pullable://docker.io/openshift/hello-openshift@sha256:9b1b29dc4ed029220b2d87fce57fab43f450fa6521ab86f22ddbc5ecc978752a
      lastState:
        terminated:
          containerID: docker://9ea5647da89302437630e96728f9f65593c07d0e65a1b275854fcb4c738c8c46
          exitCode: 2
          finishedAt: 2017-02-13T18:59:47Z
          reason: Error
          startedAt: 2017-02-10T16:33:56Z
      name: hello-openshift
      ready: true
      restartCount: 1
      state:
        running:
          startedAt: 2017-02-13T19:00:49Z
    hostIP: 10.66.208.105
    phase: Running
    podIP: 10.1.0.3
    startTime: 2017-02-10T16:33:46Z
- apiVersion: v1
  kind: Pod
  metadata:
    annotations:
      kubernetes.io/created-by: |
        {"kind":"SerializedReference","apiVersion":"v1","reference":{"kind":"ReplicationController","namespace":"zjj-project","name":"router-1-1","uid":"12c1a374-f75a-11e6-80d0-001a4a0100d2","apiVersion":"v1","resourceVersion":"1638409"}}
      openshift.io/deployment-config.latest-version: "1"
      openshift.io/deployment-config.name: router-1
      openshift.io/deployment.name: router-1-1
      openshift.io/scc: hostnetwork
    creationTimestamp: 2017-02-20T10:48:14Z
    generateName: router-1-1-
    labels:
      deployment: router-1-1
      deploymentconfig: router-1
      router: router-1
    name: router-1-1-w27o2
  spec:
    containers:
    - env:
      - name: DEFAULT_CERTIFICATE_DIR
        value: /etc/pki/tls/private
      - name: ROUTER_EXTERNAL_HOST_HOSTNAME
      - name: ROUTER_EXTERNAL_HOST_HTTPS_VSERVER
      - name: ROUTER_EXTERNAL_HOST_HTTP_VSERVER
      - name: ROUTER_EXTERNAL_HOST_INSECURE
        value: "false"
      - name: ROUTER_EXTERNAL_HOST_PARTITION_PATH
      - name: ROUTER_EXTERNAL_HOST_PASSWORD
      - name: ROUTER_EXTERNAL_HOST_PRIVKEY
        value: /etc/secret-volume/router.pem
      - name: ROUTER_EXTERNAL_HOST_USERNAME
      - name: ROUTER_SERVICE_HTTPS_PORT
        value: "443"
      - name: ROUTER_SERVICE_HTTP_PORT
        value: "80"
      - name: ROUTER_SERVICE_NAME
        value: router-1
      - name: ROUTER_SERVICE_NAMESPACE
        value: zjj-project
      - name: ROUTER_SUBDOMAIN
      - name: STATS_PASSWORD
        value: password
      - name: STATS_PORT
        value: "1936"
      - name: STATS_USERNAME
        value: admin
      image: openshift3/ose-haproxy-router:v3.3.1.7
      imagePullPolicy: IfNotPresent
      livenessProbe:
        failureThreshold: 3
        httpGet:
          host: localhost
          path: /healthz
          port: 1936
          scheme: HTTP
        initialDelaySeconds: 10
        periodSeconds: 10
        successThreshold: 1
        timeoutSeconds: 1
      name: router
      ports:
      - containerPort: 80
        hostPort: 80
        protocol: TCP
      - containerPort: 443
        hostPort: 443
        protocol: TCP
      - containerPort: 1936
        hostPort: 1936
        name: stats
        protocol: TCP
      readinessProbe:
        failureThreshold: 3
        httpGet:
          host: localhost
          path: /healthz
          port: 1936
          scheme: HTTP
        initialDelaySeconds: 10
        periodSeconds: 10
        successThreshold: 1
        timeoutSeconds: 1
      resources:
        requests:
          cpu: 100m
          memory: 256Mi
      securityContext:
        capabilities:
          drop:
          - KILL
          - MKNOD
          - SETGID
          - SETUID
          - SYS_CHROOT
        privileged: false
        runAsUser: 1000070000
        seLinuxOptions:
          level: s0:c8,c7
      terminationMessagePath: /dev/termination-log
      volumeMounts:
      - mountPath: /etc/pki/tls/private
        name: server-certificate
        readOnly: true
      - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
        name: router-token-0j7an
        readOnly: true
    dnsPolicy: ClusterFirst
    host: node1.ose.com
    hostNetwork: true
    imagePullSecrets:
    - name: router-dockercfg-dlu6n
    nodeName: node1.ose.com
    restartPolicy: Always
    securityContext:
      fsGroup: 1000070000
      seLinuxOptions:
        level: s0:c8,c7
      supplementalGroups:
      - 1000070000
    serviceAccount: router
    serviceAccountName: router
    terminationGracePeriodSeconds: 30
    volumes:
    - name: server-certificate
      secret:
        secretName: router-1-certs
    - name: router-token-0j7an
      secret:
        secretName: router-token-0j7an
  status:
    conditions:
    - lastProbeTime: null
      lastTransitionTime: 2017-02-20T10:48:14Z
      status: "True"
      type: Initialized
    containerStatuses:
    - containerID: docker://aa4348a647e0f3186e70a0ce9837f84a25060b4daebab370c1fc093cf8af3349
      image: openshift3/ose-haproxy-router:v3.3.1.7
      imageID: docker-pullable://registry.access.redhat.com/openshift3/ose-haproxy-router@sha256:f2f75cfd2b828c3143ca8022e26593a7491ca040dab6d6472472ed040d1c1b83
      lastState: {}
      name: router
      ready: true
      restartCount: 0
      state:
        running:
          startedAt: 2017-02-20T10:48:16Z
    hostIP: 10.66.208.229
    phase: Running
    podIP: 10.66.208.229
    startTime: 2017-02-20T10:48:14Z
kind: List
metadata: {}
""".strip()

OC_GET_SERVICE = """
apiVersion: v1
items:
- apiVersion: v1
  kind: Service
  metadata:
    creationTimestamp: 2016-12-27T03:24:03Z
    labels:
      component: apiserver
      provider: kubernetes
    name: kubernetes
    namespace: default
    resourceVersion: "9"
    selfLink: /api/v1/namespaces/default/services/kubernetes
    uid: ea9d8fb4-cbe3-11e6-b3c1-001a4a0100d2
  spec:
    clusterIP: 172.30.0.1
    portalIP: 172.30.0.1
    ports:
    - name: https
      port: 443
      protocol: TCP
      targetPort: 443
    - name: dns
      port: 53
      protocol: UDP
      targetPort: 8053
    - name: dns-tcp
      port: 53
      protocol: TCP
      targetPort: 8053
    sessionAffinity: ClientIP
    type: ClusterIP
  status:
    loadBalancer: {}
- apiVersion: v1
  kind: Service
  metadata:
    annotations:
      service.alpha.openshift.io/serving-cert-secret-name: router-1-certs
      service.alpha.openshift.io/serving-cert-signed-by: openshift-service-serving-signer@1480042702
    creationTimestamp: 2017-02-20T10:48:11Z
    labels:
      router: router-1
    name: router-1
    namespace: zjj-project
    resourceVersion: "1638401"
    selfLink: /api/v1/namespaces/zjj-project/services/router-1
    uid: 12bdf634-f75a-11e6-80d0-001a4a0100d2
  spec:
    clusterIP: 172.30.210.0
    portalIP: 172.30.210.0
    ports:
    - name: 80-tcp
      port: 80
      protocol: TCP
      targetPort: 80
    - name: 443-tcp
      port: 443
      protocol: TCP
      targetPort: 443
    - name: 1936-tcp
      port: 1936
      protocol: TCP
      targetPort: 1936
    selector:
      router: router-1
    sessionAffinity: None
    type: ClusterIP
  status:
    loadBalancer: {}
kind: List
metadata: {}
""".strip()

OC_GET_CONFIGMAP = """
apiVersion: v1
items:
- apiVersion: v1
  data:
    node-config.yaml: |
      apiVersion: v1
      authConfig:
        authenticationCacheSize: 1000
        authenticationCacheTTL: 5m
        authorizationCacheSize: 1000
        authorizationCacheTTL: 5m
      dnsBindAddress: 127.0.0.1:53
      dnsDomain: cluster.local
      dnsIP: 0.0.0.0
      dnsNameservers: null
      dnsRecursiveResolvConf: /etc/origin/node/resolv.conf
      dockerConfig:
        dockerShimRootDirectory: /var/lib/dockershim
        dockerShimSocket: /var/run/dockershim.sock
        execHandlerName: native
      enableUnidling: true
      imageConfig:
        format: registry.access.redhat.com/openshift3/ose-${component}:${version}
        latest: false
      iptablesSyncPeriod: 30s
      kind: NodeConfig
      kubeletArguments:
        bootstrap-kubeconfig:
        - /etc/origin/node/bootstrap.kubeconfig
        cert-dir:
        - /etc/origin/node/certificates
        cloud-config:
        - /etc/origin/cloudprovider/openstack.conf
        cloud-provider:
        - openstack
        container-runtime:
        - remote
        container-runtime-endpoint:
        - /var/run/crio/crio.sock
        enable-controller-attach-detach:
        - 'true'
        feature-gates:
        - RotateKubeletClientCertificate=true,RotateKubeletServerCertificate=true
        image-service-endpoint:
        - /var/run/crio/crio.sock
        node-labels:
        - node-role.kubernetes.io/infra=true,node-role.kubernetes.io/master=true,node-role.kubernetes.io/compute=true
        pod-manifest-path:
        - /etc/origin/node/pods
        rotate-certificates:
        - 'true'
        runtime-request-timeout:
        - 10m
      masterClientConnectionOverrides:
        acceptContentTypes: application/vnd.kubernetes.protobuf,application/json
        burst: 40
        contentType: application/vnd.kubernetes.protobuf
        qps: 20
      masterKubeConfig: node.kubeconfig
      networkConfig:
        mtu: 1450
        networkPluginName: redhat/openshift-ovs-networkpolicy
      servingInfo:
        bindAddress: 0.0.0.0:10250
        bindNetwork: tcp4
        clientCA: client-ca.crt
      volumeConfig:
        localQuota:
          perFSGroup: null
      volumeDirectory: /var/lib/origin/openshift.local.volumes
    volume-config.yaml: |
      apiVersion: kubelet.config.openshift.io/v1
      kind: VolumeConfig
      localQuota:
        perFSGroup: 512Mi
  kind: ConfigMap
  metadata:
    creationTimestamp: 2018-08-07T14:56:15Z
    name: node-config-all-in-one
    namespace: openshift-node
    resourceVersion: "1057"
    selfLink: /api/v1/namespaces/openshift-node/configmaps/node-config-all-in-one
    uid: 0856aa7e-9a52-11e8-b4f0-fa163e0d4482
- apiVersion: v1
  data:
    fluent.conf: |
      # This file is the fluentd configuration entrypoint. Edit with care.

      @include configs.d/openshift/system.conf

      # In each section below, pre- and post- includes don't include anything initially;
      # they exist to enable future additions to openshift conf as needed.

      ## sources
      ## ordered so that syslog always runs last...
      @include configs.d/openshift/input-pre-*.conf
      @include configs.d/dynamic/input-docker-*.conf
      @include configs.d/dynamic/input-syslog-*.conf
      @include configs.d/openshift/input-post-*.conf
      ##

      <label @INGRESS>
      ## filters
        @include configs.d/openshift/filter-pre-*.conf
        @include configs.d/openshift/filter-retag-journal.conf
        @include configs.d/openshift/filter-k8s-meta.conf
        @include configs.d/openshift/filter-kibana-transform.conf
        @include configs.d/openshift/filter-k8s-flatten-hash.conf
        @include configs.d/openshift/filter-k8s-record-transform.conf
        @include configs.d/openshift/filter-syslog-record-transform.conf
        @include configs.d/openshift/filter-viaq-data-model.conf
        @include configs.d/openshift/filter-post-*.conf
      ##
      </label>

      <label @OUTPUT>
      ## matches
        @include configs.d/openshift/output-pre-*.conf
        @include configs.d/openshift/output-operations.conf
        @include configs.d/openshift/output-applications.conf
        # no post - applications.conf matches everything left
      ##
      </label>
    secure-forward.conf: |
      # <store>
      # @type secure_forward

      # self_hostname ${hostname}
      # shared_key <SECRET_STRING>

      # secure yes
      # enable_strict_verification yes

      # ca_cert_path /etc/fluent/keys/your_ca_cert
      # ca_private_key_path /etc/fluent/keys/your_private_key
        # for private CA secret key
      # ca_private_key_passphrase passphrase

      # <server>
        # or IP
      #   host server.fqdn.example.com
      #   port 24284
      # </server>
      # <server>
        # ip address to connect
      #   host 203.0.113.8
        # specify hostlabel for FQDN verification if ipaddress is used for host
      #   hostlabel server.fqdn.example.com
      # </server>
      # </store>
    throttle-config.yaml: |
      # Logging example fluentd throttling config file

      #example-project:
      #  read_lines_limit: 10
      #
      #.operations:
      #  read_lines_limit: 100
  kind: ConfigMap
  metadata:
    creationTimestamp: 2018-08-07T15:36:51Z
    name: logging-fluentd
    namespace: openshift-logging
    resourceVersion: "8922"
    selfLink: /api/v1/namespaces/openshift-logging/configmaps/logging-fluentd
    uid: b4b8f35c-9a57-11e8-b5ba-fa163e0d4482
kind: List
metadata:
  resourceVersion: ""
  selfLink: ""
""".strip()

OC_GET_BC = """
apiVersion: v1
items:
- apiVersion: v1
  kind: BuildConfig
  metadata:
    annotations:
      openshift.io/generated-by: OpenShiftWebConsole
    creationTimestamp: 2017-11-28T09:02:19Z
    labels:
      app: tom
    name: tom
    namespace: ci
    resourceVersion: "8922062"
    selfLink: /oapi/v1/namespaces/ci/buildconfigs/tom
    uid: d6a0364c-d41a-11e7-aef1-001a4a010222
  spec:
    nodeSelector: null
    output:
      to:
        kind: ImageStreamTag
        name: tom:latest
    postCommit: {}
    resources:
      limits:
        cpu: "1"
        memory: 512m
      requests:
        cpu: 100m
        memory: 256m
    runPolicy: Serial
    source:
      contextDir: tomcat-websocket-chat
      git:
        ref: master
        uri: https://github.com/jboss-openshift/openshift-quickstarts.git
      type: Git
    strategy:
      sourceStrategy:
        from:
          kind: ImageStreamTag
          name: jboss-webserver30-tomcat7-openshift:1.3
          namespace: openshift
      type: Source
    triggers:
    - generic:
        secret: 222545c18370f300
      type: Generic
    - github:
        secret: a75ac7b89f8afc22
      type: GitHub
    - imageChange:
        lastTriggeredImageID: registry.access.redhat.com/jboss-webserver-3/webserver30-tomcat7-openshift@sha256:6ee8de68a744d820e249f784b5ba41d059f91a5554fce47c7e0b998aa88c97cb
      type: ImageChange
    - type: ConfigChange
  status:
    lastVersion: 2
- apiVersion: v1
  kind: BuildConfig
  metadata:
    annotations:
      openshift.io/generated-by: OpenShiftWebConsole
    creationTimestamp: 2017-11-28T09:05:26Z
    labels:
      app: mybank
    name: mybank
    namespace: mybank
    resourceVersion: "8961033"
    selfLink: /oapi/v1/namespaces/mybank/buildconfigs/mybank
    uid: 46711668-d41b-11e7-aef1-001a4a010222
  spec:
    nodeSelector: null
    output:
      to:
        kind: ImageStreamTag
        name: mybank:latest
    postCommit: {}
    resources:
      limits:
        cpu: "1"
        memory: 512m
      requests:
        cpu: 100m
        memory: 256M
    runPolicy: Serial
    source:
      git:
        ref: master
        uri: https://github.com/shzhou12/mybank-demo-maven
      type: Git
    strategy:
      sourceStrategy:
        from:
          kind: ImageStreamTag
          name: jboss-eap70-openshift:1.5
          namespace: openshift
      type: Source
    triggers:
    - generic:
        secret: 3bf9b0f9eda5bcc3
      type: Generic
    - github:
        secret: a1cea7fe7310d6df
      type: GitHub
    - imageChange:
        lastTriggeredImageID: registry.access.redhat.com/jboss-eap-7/eap70-openshift@sha256:b1b664a9b6f797d530bf12c29123947c1feb4590336ecc9d118b3f2e44000524
      type: ImageChange
    - type: ConfigChange
  status:
    lastVersion: 11
kind: List
metadata: {}
resourceVersion: ""
selfLink: ""
""".strip()

OC_GET_DC = """
apiVersion: v1
items:
- apiVersion: v1
  kind: DeploymentConfig
  metadata:
    creationTimestamp: 2017-02-14T15:21:51Z
    generation: 3
    labels:
      docker-registry: default
    name: docker-registry
    namespace: openshift
    resourceVersion: "1439616"
    selfLink: /oapi/v1/namespaces/openshift/deploymentconfigs/docker-registry
    uid: 4f1cf726-f2c9-11e6-8c0e-001a4a0100d2
  spec:
    replicas: 1
    selector:
      docker-registry: default
    strategy:
      resources: {}
      rollingParams:
        intervalSeconds: 1
        maxSurge: 25%
        maxUnavailable: 25%
        timeoutSeconds: 600
        updatePeriodSeconds: 1
      type: Rolling
    template:
      metadata:
        creationTimestamp: null
        labels:
          docker-registry: default
      spec:
        containers:
        - env:
          - name: REGISTRY_HTTP_ADDR
            value: :5000
          - name: REGISTRY_HTTP_NET
            value: tcp
          - name: REGISTRY_HTTP_SECRET
            value: mysupersecrethttpsecret
          - name: REGISTRY_MIDDLEWARE_REPOSITORY_OPENSHIFT_ENFORCEQUOTA
            value: "false"
          image: registry.access.redhat.com/openshift3/ose-docker-registry
          imagePullPolicy: Always
          livenessProbe:
            failureThreshold: 3
            httpGet:
              path: /healthz
              port: 5000
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          name: registry
          ports:
          - containerPort: 5000
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /healthz
              port: 5000
              scheme: HTTP
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 5
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
          securityContext:
            privileged: false
          terminationMessagePath: /dev/termination-log
          volumeMounts:
          - mountPath: /registry
            name: registry-storage
        dnsPolicy: ClusterFirst
        terminationGracePeriodSeconds: 30
        volumes:
        - name: registry-storage
          persistentVolumeClaim:
            claimName: registry-claim-test1
    test: false
    triggers:
    - type: ConfigChange
  status:
    availableReplicas: 1
    details:
      causes:
      - type: ConfigChange
      message: caused by a config change
    latestVersion: 3
    observedGeneration: 3
    replicas: 1
    updatedReplicas: 1
- apiVersion: v1
  kind: DeploymentConfig
  metadata:
    creationTimestamp: 2017-02-20T10:48:11Z
    generation: 1
    labels:
      router: router-1
    name: router-1
    namespace: zjj-project
    resourceVersion: "1638435"
    selfLink: /oapi/v1/namespaces/zjj-project/deploymentconfigs/router-1
    uid: 12b9b90f-f75a-11e6-80d0-001a4a0100d2
  spec:
    replicas: 1
    selector:
      router: router-1
    strategy:
      resources: {}
      rollingParams:
        intervalSeconds: 1
        maxSurge: 0
        maxUnavailable: 25%
        timeoutSeconds: 600
        updatePercent: -25
        updatePeriodSeconds: 1
      type: Rolling
    template:
      metadata:
        creationTimestamp: null
        labels:
          router: router-1
      spec:
        containers:
        - env:
          - name: DEFAULT_CERTIFICATE_DIR
            value: /etc/pki/tls/private
          - name: ROUTER_EXTERNAL_HOST_HOSTNAME
          - name: ROUTER_EXTERNAL_HOST_HTTPS_VSERVER
          - name: ROUTER_EXTERNAL_HOST_HTTP_VSERVER
          - name: ROUTER_EXTERNAL_HOST_INSECURE
            value: "false"
          - name: ROUTER_EXTERNAL_HOST_PARTITION_PATH
          - name: ROUTER_EXTERNAL_HOST_PASSWORD
          - name: ROUTER_EXTERNAL_HOST_PRIVKEY
            value: /etc/secret-volume/router.pem
          - name: ROUTER_EXTERNAL_HOST_USERNAME
          - name: ROUTER_SERVICE_HTTPS_PORT
            value: "443"
          - name: ROUTER_SERVICE_HTTP_PORT
            value: "80"
          - name: ROUTER_SERVICE_NAME
            value: router-1
          - name: ROUTER_SERVICE_NAMESPACE
            value: zjj-project
          - name: ROUTER_SUBDOMAIN
          - name: STATS_PASSWORD
            value: password
          - name: STATS_PORT
            value: "1936"
          - name: STATS_USERNAME
            value: admin
          image: openshift3/ose-haproxy-router:v3.3.1.7
          imagePullPolicy: IfNotPresent
          livenessProbe:
            failureThreshold: 3
            httpGet:
              host: localhost
              path: /healthz
              port: 1936
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          name: router
          ports:
          - containerPort: 1936
            hostPort: 1936
            name: stats
            protocol: TCP
          readinessProbe:
            failureThreshold: 3
            httpGet:
              host: localhost
              path: /healthz
              port: 1936
              scheme: HTTP
            initialDelaySeconds: 10
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 1
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
          terminationMessagePath: /dev/termination-log
          volumeMounts:
          - mountPath: /etc/pki/tls/private
            name: server-certificate
            readOnly: true
        dnsPolicy: ClusterFirst
        volumes:
        - name: server-certificate
          secret:
            secretName: router-1-certs
    test: false
    triggers:
    - type: ConfigChange
  status:
    availableReplicas: 1
    details:
      causes:
      - type: ConfigChange
      message: caused by a config change
    latestVersion: 1
    observedGeneration: 1
    replicas: 1
    updatedReplicas: 1
kind: List
metadata: {}
""".strip()

OC_GET_ROLEBINDING = """
apiVersion: v1
items:
- apiVersion: v1
  groupNames: null
  kind: RoleBinding
  metadata:
    creationTimestamp: 2017-03-07T09:00:56Z
    name: admin
    namespace: foo
    resourceVersion: "11803596"
    selfLink: /oapi/v1/namespaces/foo/rolebindings/admin
    uid: 93256034-0314-11e7-b98e-001a4a0101f0
  roleRef:
    name: admin
  subjects:
  - kind: SystemUser
    name: system:admin
  userNames:
  - system:admin
- apiVersion: v1
  groupNames: null
  kind: RoleBinding
  metadata:
    creationTimestamp: 2017-03-07T09:00:56Z
    name: system:image-builders
    namespace: foo
    resourceVersion: "11803603"
    selfLink: /oapi/v1/namespaces/foo/rolebindings/system:image-builders
    uid: 93709567-0314-11e7-b98e-001a4a0101f0
  roleRef:
    name: system:image-builder
  subjects:
  - kind: ServiceAccount
    name: builder
    namespace: foo
  userNames:
  - system:serviceaccount:foo:builder
- apiVersion: v1
  groupNames: null
  kind: RoleBinding
  metadata:
    creationTimestamp: null
    name: myrole
    namespace: foo
    resourceVersion: "415"
    selfLink: /oapi/v1/namespaces/foo/rolebindings/myrole
  roleRef:
    name: myrole
    namespace: foo
  subjects: null
  userNames: null
kind: List
metadata: {}
""".strip()

OC_GET_PROJECT = """
apiVersion: v1
items:
- apiVersion: v1
  kind: Project
  metadata:
    annotations:
      openshift.io/description: ""
      openshift.io/display-name: ""
      openshift.io/requester: testuser
      openshift.io/sa.scc.mcs: s0:c8,c2
      openshift.io/sa.scc.supplemental-groups: 1000060000/10000
      openshift.io/sa.scc.uid-range: 1000060000/10000
    creationTimestamp: 2017-02-13T03:01:30Z
    name: zjj-project
    resourceVersion: "11040756"
    selfLink: /oapi/v1/projects/zjj-project
    uid: b83cdc59-f198-11e6-b98e-001a4a0101f0
  spec:
    finalizers:
    - openshift.io/origin
    - kubernetes
  status:
    phase: Active
- apiVersion: v1
  kind: Project
  metadata:
    annotations:
      openshift.io/description: ""
      openshift.io/display-name: ""
      openshift.io/requester: testuser
      openshift.io/sa.scc.mcs: s0:c11,c0
      openshift.io/sa.scc.supplemental-groups: 1000110000/10000
      openshift.io/sa.scc.uid-range: 1000110000/10000
    creationTimestamp: 2016-12-27T07:49:13Z
    name: test
    resourceVersion: "9401953"
    selfLink: /oapi/v1/projects/test
    uid: f5f2a52c-cc08-11e6-8b9b-001a4a0101f0
  spec:
    finalizers:
    - openshift.io/origin
    - kubernetes
  status:
    phase: Active
kind: List
metadata: {}
""".strip()

OC_GET_ROLE = """
apiVersion: v1
items:
- apiVersion: v1
  kind: Role
  metadata:
    creationTimestamp: 2016-08-30T16:13:03Z
    name: shared-resource-viewer
    namespace: openshift
    resourceVersion: "94"
    selfLink: /oapi/v1/namespaces/openshift/roles/shared-resource-viewer
    uid: a10c3f88-6ecc-11e6-83c6-001a4a0101f0
  rules:
  - apiGroups: null
    attributeRestrictions: null
    resources:
    - imagestreamimages
    - imagestreamimports
    - imagestreammappings
    - imagestreams
    - imagestreamtags
    - templates
    verbs:
    - get
    - list
  - apiGroups: null
    attributeRestrictions: null
    resources:
    - imagestreams/layers
    verbs:
    - get
kind: List
metadata: {}
""".strip()


OC_GET_ROUTE = """
apiVersion: v1
items:
- apiVersion: v1
  kind: Route
  metadata:
    creationTimestamp: 2018-02-23T04:26:01Z
    name: docker-registry
    namespace: default
    resourceVersion: "4166"
    selfLink: /oapi/v1/namespaces/default/routes/docker-registry
    uid: a72a9680-1851-11e8-82e4-001a4a0102eb
  spec:
    host: docker-registry-default.router.default.svc.cluster.local
    tls:
      termination: passthrough
    to:
      kind: Service
      name: docker-registry
      weight: 100
    wildcardPolicy: None
  status:
    ingress:
    - conditions:
      - lastTransitionTime: 2018-02-23T06:24:02Z
        status: "True"
        type: Admitted
      host: docker-registry-default.router.default.svc.cluster.local
      routerName: router
      wildcardPolicy: None
kind: List
metadata: {}
resourceVersion: ""
selfLink: ""
""".strip()


OC_GET_PV = """
apiVersion: v1
items:
- apiVersion: v1
  kind: PersistentVolume
  metadata:
    annotations:
      pv.kubernetes.io/bound-by-controller: "yes"
    creationTimestamp: 2017-03-09T15:23:17Z
    name: registry-volume
    resourceVersion: "745"
    selfLink: /api/v1/persistentvolumes/registry-volume
    uid: 52394d79-04dc-11e7-ab1f-001a4a0101d2
  spec:
    accessModes:
    - ReadWriteMany
    capacity:
      storage: 5Gi
    claimRef:
      apiVersion: v1
      kind: PersistentVolumeClaim
      name: registry-claim
      namespace: default
      resourceVersion: "743"
      uid: 52c44068-04dc-11e7-ab1f-001a4a0101d2
    nfs:
      path: /exports/registry
      server: master.ose33.com
    persistentVolumeReclaimPolicy: Retain
  status:
    phase: Bound
- apiVersion: v1
  kind: PersistentVolume
  metadata:
    creationTimestamp: 2017-04-05T10:44:54Z
    name: registry-volume-zjj
    resourceVersion: "934892"
    selfLink: /api/v1/persistentvolumes/registry-volume-zjj
    uid: e7519f6c-19ec-11e7-ab1f-001a4a0101d2
  spec:
    accessModes:
    - ReadWriteMany
    capacity:
      storage: 10Gi
    nfs:
      path: /nfs
      server: 10.66.208.147
    persistentVolumeReclaimPolicy: Recycle
  status:
    phase: Available
kind: List
metadata: {}
""".strip()

OC_GET_PVC = """
apiVersion: v1
items:
- apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    annotations:
      pv.kubernetes.io/bind-completed: "yes"
      pv.kubernetes.io/bound-by-controller: "yes"
    creationTimestamp: 2017-03-09T15:23:18Z
    name: registry-claim
    namespace: default
    resourceVersion: "747"
    selfLink: /api/v1/namespaces/default/persistentvolumeclaims/registry-claim
    uid: 52c44068-04dc-11e7-ab1f-001a4a0101d2
  spec:
    accessModes:
    - ReadWriteMany
    resources:
      requests:
        storage: 5Gi
    volumeName: registry-volume
  status:
    accessModes:
    - ReadWriteMany
    capacity:
      storage: 5Gi
    phase: Bound
- apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    annotations:
      pv.kubernetes.io/bind-completed: "yes"
    creationTimestamp: 2017-04-12T18:40:43Z
    name: registry-claim-test1
    namespace: default
    resourceVersion: "1084833"
    selfLink: /api/v1/namespaces/default/persistentvolumeclaims/registry-claim-test1
    uid: 89169428-1faf-11e7-b236-001a4a0101d2
  spec:
    accessModes:
    - ReadWriteMany
    resources:
      requests:
        storage: 5Gi
    volumeName: registry-volume-zjj
  status:
    accessModes:
    - ReadWriteMany
    capacity:
      storage: 10Gi
    phase: Bound
kind: List
metadata: {}
""".strip()

OC_GET_ENDPOINTS = """
apiVersion: v1
items:
- apiVersion: v1
  kind: Endpoints
  metadata:
    creationTimestamp: 2017-06-15T05:53:47Z
    name: gluster-cluster
    namespace: default
    resourceVersion: "35151"
    selfLink: /api/v1/namespaces/default/endpoints/gluster-cluster
    uid: ffaf2c59-518e-11e7-a93b-001a4a01010c
  subsets:
  - addresses:
    - ip: 10.64.221.124
    - ip: 10.64.221.126
    ports:
    - port: 1
      protocol: TCP
- apiVersion: v1
  kind: Endpoints
  metadata:
    creationTimestamp: 2017-06-14T05:55:59Z
    name: kubernetes
    namespace: default
    resourceVersion: "449"
    selfLink: /api/v1/namespaces/default/endpoints/kubernetes
    uid: 240884a8-50c6-11e7-aae8-001a4a01010c
  subsets:
  - addresses:
    - ip: 10.66.219.113
    ports:
    - name: https
      port: 8443
      protocol: TCP
    - name: dns-tcp
      port: 8053
      protocol: TCP
    - name: dns
      port: 8053
      protocol: UDP
- apiVersion: v1
  kind: Endpoints
  metadata:
    creationTimestamp: 2017-06-14T07:32:51Z
    labels:
      app: registry-console
      createdBy: registry-console-template
      name: registry-console
    name: registry-console
    namespace: default
    resourceVersion: "2858"
    selfLink: /api/v1/namespaces/default/endpoints/registry-console
    uid: ac78a94e-50d3-11e7-aae8-001a4a01010c
  subsets:
  - addresses:
    - ip: 10.128.0.3
      nodeName: node1.ose35.com
      targetRef:
        kind: Pod
        name: registry-console-1-jckp2
        namespace: default
        resourceVersion: "2854"
        uid: d5baeab5-50d3-11e7-aae8-001a4a01010c
    ports:
    - name: registry-console
      port: 9090
      protocol: TCP
kind: List
metadata: {}
resourceVersion: ""
selfLink: ""
""".strip()

OC_GET_NODE = """
apiVersion: v1
items:
- apiVersion: v1
  kind: Node
  metadata:
    annotations:
      volumes.kubernetes.io/controller-managed-attach-detach: "true"
    creationTimestamp: 2018-01-09T02:04:15Z
    labels:
      beta.kubernetes.io/arch: amd64
      beta.kubernetes.io/os: linux
      kubernetes.io/hostname: master37
      openshift-infra: apiserver
    name: master37
    namespace: ""
    resourceVersion: "4414367"
    selfLink: /api/v1/nodes/master37
    uid: 64ce06a1-f4e1-11e7-aa53-001a4a0102af
  spec:
    externalID: master37
    unschedulable: true
  status:
    addresses:
    - address: 10.66.208.248
      type: InternalIP
    - address: master37
      type: Hostname
    allocatable:
      cpu: "8"
      memory: 20587320Ki
      pods: "80"
    capacity:
      cpu: "8"
      memory: 20689720Ki
      pods: "80"
    conditions:
    - lastHeartbeatTime: 2018-02-02T09:46:46Z
      lastTransitionTime: 2018-01-09T02:04:15Z
      message: kubelet has sufficient disk space available
      reason: KubeletHasSufficientDisk
      status: "False"
      type: OutOfDisk
    - lastHeartbeatTime: 2018-02-02T09:46:46Z
      lastTransitionTime: 2018-01-09T02:04:15Z
      message: kubelet has sufficient memory available
      reason: KubeletHasSufficientMemory
      status: "False"
      type: MemoryPressure
    - lastHeartbeatTime: 2018-02-02T09:46:46Z
      lastTransitionTime: 2018-01-09T02:04:15Z
      message: kubelet has no disk pressure
      reason: KubeletHasNoDiskPressure
      status: "False"
      type: DiskPressure
    daemonEndpoints:
      kubeletEndpoint:
        Port: 10250
    images:
    - names:
      - registry.access.redhat.com/openshift3/ose@sha256:c4fe334182030e0878a462998aef2ae48536eb8966c570ddb2710a11b8e9ac82
      - registry.access.redhat.com/openshift3/ose:v3.7
      sizeBytes: 1059063314
    - names:
      - registry.access.redhat.com/openshift3/ose-service-catalog@sha256:e06e609d21f1df6ff396a4d95caade01149e3ee706490b9665708fd95ba84ad0
      - registry.access.redhat.com/openshift3/ose-service-catalog:v3.7
      sizeBytes: 268789707
    - names:
      - registry.access.redhat.com/openshift3/ose-pod@sha256:5b397b3fd1bb98e53e829b8938f853364d3ff85d85f2e011fae3f67757e9cf96
      - registry.access.redhat.com/openshift3/ose-pod:v3.7.14
      sizeBytes: 208847376
    nodeInfo:
      architecture: amd64
      bootID: e998fc70-8d7d-47ac-81c6-72a662c68424
      containerRuntimeVersion: docker://1.12.6
      kernelVersion: 3.10.0-693.11.6.el7.x86_64
      kubeProxyVersion: v1.7.6+a08f5eeb62
      kubeletVersion: v1.7.6+a08f5eeb62
      machineID: 897d22c8a60d434b9b5857ffa80064e4
      operatingSystem: linux
      osImage: Employee SKU
      systemUUID: 897D22C8-A60D-434B-9B58-57FFA80064E4
""".strip()

OC_GET_RC = """
apiVersion: v1
items:
- apiVersion: v1
  kind: ReplicationController
  metadata:
    annotations:
      openshift.io/deployer-pod.name: jenkins-1-deploy
      openshift.io/deployment-config.latest-version: "1"
      openshift.io/deployment-config.name: jenkins
      openshift.io/deployment.phase: Complete
      openshift.io/deployment.replicas: "1"
      openshift.io/deployment.status-reason: image change
    creationTimestamp: 2017-11-28T08:24:39Z
    generation: 2
    labels:
      app: jenkins-ephemeral
      openshift.io/deployment-config.name: jenkins
      template: jenkins-ephemeral-template
    name: jenkins-1
    namespace: ci
    resourceVersion: "9998736"
    selfLink: /api/v1/namespaces/ci/replicationcontrollers/jenkins-1
    uid: 93a12b07-d415-11e7-aef1-001a4a010222
  spec:
    replicas: 1
    selector:
      deployment: jenkins-1
      deploymentconfig: jenkins
      name: jenkins
    template:
      metadata:
        annotations:
          openshift.io/deployment-config.latest-version: "1"
          openshift.io/deployment-config.name: jenkins
          openshift.io/deployment.name: jenkins-1
          openshift.io/generated-by: OpenShiftNewApp
        creationTimestamp: null
        labels:
          app: jenkins-ephemeral
          deployment: jenkins-1
          deploymentconfig: jenkins
          name: jenkins
      spec:
        containers:
        - env:
          - name: JENKINS_PASSWORD
            value: welcome1
          - name: KUBERNETES_MASTER
            value: https://kubernetes.default:443
          - name: KUBERNETES_TRUST_CERTIFICATES
            value: "true"
          - name: JNLP_SERVICE_NAME
            value: jenkins-jnlp
          name: jenkins
          readinessProbe:
            failureThreshold: 3
            httpGet:
              path: /login
              port: 8080
              scheme: HTTP
            initialDelaySeconds: 3
            periodSeconds: 10
            successThreshold: 1
            timeoutSeconds: 3
          resources:
            limits:
              memory: 512Mi
          securityContext:
            capabilities: {}
            privileged: false
          terminationMessagePath: /dev/termination-log
          volumeMounts:
          - mountPath: /var/lib/jenkins
            name: jenkins-data
        dnsPolicy: ClusterFirst
        restartPolicy: Always
        securityContext: {}
        serviceAccount: jenkins
        serviceAccountName: jenkins
        terminationGracePeriodSeconds: 30
        volumes:
        - emptyDir: {}
          name: jenkins-data
  status:
    availableReplicas: 1
    fullyLabeledReplicas: 1
    observedGeneration: 2
    readyReplicas: 1
    replicas: 1
""".strip()

OC_GET_EVENT = """
apiVersion: v1
items:
- apiVersion: v1
  count: 5613
  firstTimestamp: 2018-01-12T02:38:19Z
  involvedObject:
    apiVersion: v1
    fieldPath: spec.containers{busybox}
    kind: Pod
    name: busybox
    namespace: ci
    resourceVersion: "10897114"
    uid: 69f22749-f1da-11e7-989a-001a4a010222
  kind: Event
  lastTimestamp: 2018-02-02T09:49:42Z
  message: pulling image "busybox"
  metadata:
    creationTimestamp: 2018-01-12T02:38:19Z
    name: busybox.1508ef957b1935a4
    namespace: ci
    resourceVersion: "12356614"
    selfLink: /api/v1/namespaces/ci/events/busybox.1508ef957b1935a4
    uid: a648ed7c-f741-11e7-989a-001a4a010222
  reason: Pulling
  source:
    component: kubelet
    host: node2
  type: Normal
- apiVersion: v1
  count: 1
  firstTimestamp: 2018-02-05T01:55:35Z
  involvedObject:
    apiVersion: v1
    kind: Pod
    name: ruby-ex-2-htczn
    namespace: test-ruby
    resourceVersion: "4892941"
    uid: a82ecd0f-0a17-11e8-97fa-001a4a0102af
  kind: Event
  lastTimestamp: 2018-02-05T01:55:35Z
  message: Successfully assigned ruby-ex-2-htczn to node237
  metadata:
    creationTimestamp: 2018-02-05T01:55:35Z
    name: ruby-ex-2-htczn.15104b2e14a7ffc7
    namespace: test-ruby
    resourceVersion: "4892946"
    selfLink: /api/v1/namespaces/test-ruby/events/ruby-ex-2-htczn.15104b2e14a7ffc7
    uid: a831518d-0a17-11e8-97fa-001a4a0102af
  reason: Scheduled
  source:
    component: default-scheduler
  type: Normal
- apiVersion: v1
  count: 1
  firstTimestamp: 2018-02-05T01:55:35Z
  involvedObject:
    apiVersion: v1
    kind: ReplicationController
    name: ruby-ex-2
    namespace: test-ruby
    resourceVersion: "4892939"
    uid: a57f2d52-0a17-11e8-97fa-001a4a0102af
  kind: Event
  lastTimestamp: 2018-02-05T01:55:35Z
  message: 'Created pod: ruby-ex-2-htczn'
  metadata:
    creationTimestamp: 2018-02-05T01:55:35Z
    name: ruby-ex-2.15104b2e13fcd0ca
    namespace: test-ruby
    resourceVersion: "4892945"
    selfLink: /api/v1/namespaces/test-ruby/events/ruby-ex-2.15104b2e13fcd0ca
    uid: a82fc0ed-0a17-11e8-97fa-001a4a0102af
  reason: SuccessfulCreate
  source:
    component: replication-controller
  type: Normal
- apiVersion: v1
  count: 1
  firstTimestamp: 2018-02-05T01:55:31Z
  involvedObject:
    apiVersion: apps.openshift.io
    kind: DeploymentConfig
    name: ruby-ex
    namespace: test-ruby
    resourceVersion: "4892911"
    uid: dafbf582-04a4-11e8-97fa-001a4a0102af
  kind: Event
  lastTimestamp: 2018-02-05T01:55:31Z
  message: Created new replication controller "ruby-ex-2" for version 2
  metadata:
    creationTimestamp: 2018-02-05T01:55:31Z
    name: ruby-ex.15104b2d079675f7
    namespace: test-ruby
    resourceVersion: "4892913"
    selfLink: /api/v1/namespaces/test-ruby/events/ruby-ex.15104b2d079675f7
    uid: a580c543-0a17-11e8-97fa-001a4a0102af
  reason: DeploymentCreated
  source:
    component: deploymentconfig-controller
  type: Normal
kind: List
metadata:
  resourceVersion: ""
  selfLink: ""
""".strip()

OC_GET_EGRESS_NETWORK_POLICY = """
apiVersion: v1
items:
- apiVersion: v1
  kind: EgressNetworkPolicy
  metadata:
    creationTimestamp: 2018-01-29T03:31:59Z
    name: policy-test
    namespace: test-ruby
    resourceVersion: "3649310"
    selfLink: /oapi/v1/namespaces/test-ruby/egressnetworkpolicies/policy-test
    uid: f6b065cc-04a4-11e8-97fa-001a4a0102af
  spec:
    egress:
    - to:
        dnsName: www.baidu.com
      type: Allow
    - to:
        cidrSelector: 0.0.0.0/0
      type: Deny
kind: List
metadata:
  resourceVersion: ""
  selfLink: ""
""".strip()

OC_GET_BUILD = """
apiVersion: v1
items:
- apiVersion: build.openshift.io/v1
  kind: Build
  metadata:
    annotations:
      openshift.io/build-config.name: sample-app
      openshift.io/build.number: "2"
      openshift.io/build.pod-name: sample-app-2-build
    creationTimestamp: 2018-05-08T13:25:35Z
    labels:
      app: sample-app
      buildconfig: sample-app
      openshift.io/build-config.name: sample-app
      openshift.io/build.start-policy: Serial
    name: sample-app-2
    namespace: default
    ownerReferences:
    - apiVersion: build.openshift.io/v1
      controller: true
      kind: BuildConfig
      name: sample-app
      uid: 014c30d6-52c3-11e8-8f2a-001a4a16016f
    resourceVersion: "38277"
    selfLink: /apis/build.openshift.io/v1/namespaces/default/builds/sample-app-2
    uid: 4a656a4e-52c3-11e8-8f2a-001a4a16016f
  spec:
    nodeSelector: null
    output:
      pushSecret:
        name: builder-dockercfg-hwnx4
      to:
        kind: ImageStreamTag
        name: sample-app:latest
    postCommit: {}
    resources: {}
    serviceAccount: builder
    source:
      git:
        uri: https://example.com/mfojtik/sample-app.git
      type: Git
    strategy:
      sourceStrategy:
        from:
          kind: DockerImage
          name: registry.access.example.com/rhscl/ruby-24-rhel7@sha256:da812edc2a0c0c8c28854daeb7629c733dcc5672c33d44f920ea8f1f2d6a058d
      type: Source
    triggeredBy:
    - message: Manually triggered
  status:
    config:
      kind: BuildConfig
      name: sample-app
      namespace: default
    output: {}
    outputDockerImageReference: docker-registry.example.svc:5000/default/sample-app:latest
    phase: Pending
kind: List
metadata:
  resourceVersion: ""
  selfLink: ""
"""


def test_oc_get_pod_yml():
    result = openshift_get.OcGetPod(context_wrap(OC_GET_POD))
    assert result.data['items'][0]['metadata']['annotations']['openshift.io/scc'] == 'anyuid'
    ct = result.data['items'][0]['metadata']['creationTimestamp'].replace(tzinfo=None)
    assert ct == datetime.datetime(2017, 2, 10, 16, 33, 46, tzinfo=None)
    assert result.data['items'][0]['spec']['host'] == 'node2.ose.com'
    assert result.get("items")[0]['spec']['host'] == 'node2.ose.com'
    assert result.pods["router-1-1-w27o2"]["metadata"]["labels"]["deploymentconfig"] == "router-1"


def test_oc_get_service_yml():
    result = openshift_get.OcGetService(context_wrap(OC_GET_SERVICE))
    assert result.data['items'][0]['kind'] == 'Service'
    assert result.data['items'][0]['spec']['clusterIP'] == '172.30.0.1'
    assert result.data['items'][0]['metadata']['name'] == 'kubernetes'
    assert result.data['items'][1]['metadata']['name'] == 'router-1'
    assert result.data['items'][1]['spec']['ports'][0]['port'] == 80
    assert result.data['kind'] == 'List'
    assert result.data['metadata'] == {}
    assert result.get("items")[0]['spec']['clusterIP'] == '172.30.0.1'
    assert "zjj-project" in result.data['items'][1]['metadata']['namespace']
    assert result.services["router-1"]["metadata"]["resourceVersion"] == "1638401"


def test_oc_get_configmap_yml():
    result = openshift_get.OcGetConfigmap(context_wrap(OC_GET_CONFIGMAP))
    assert result.data['items'][0]['kind'] == 'ConfigMap'
    assert result.data['items'][0]['metadata']['name'] == 'node-config-all-in-one'


def test_oc_get_bc_yml():
    result = openshift_get.OcGetBc(context_wrap(OC_GET_BC))
    assert result['items'][0]['kind'] == 'BuildConfig'
    assert result['items'][1]['metadata']['name'] == 'mybank'
    assert result.build_configs['mybank']['status']['lastVersion'] == 11
    assert result.build_configs['tom']['metadata']['namespace'] == 'ci'


def test_oc_get_dc_yml():
    result = openshift_get.OcGetDc(context_wrap(OC_GET_DC))
    assert result.data['items'][0]['kind'] == 'DeploymentConfig'
    assert result.data['items'][0]['metadata']['generation'] == 3
    assert result.get("items")[0]['metadata']['generation'] == 3
    assert result.deployment_configs["router-1"]["metadata"]["namespace"] == "zjj-project"


def test_oc_get_rolebinding_yml():
    result = openshift_get.OcGetRolebinding(context_wrap(OC_GET_ROLEBINDING))
    assert result.data['items'][0]['kind'] == 'RoleBinding'
    assert result.data['items'][0]['metadata']['resourceVersion'] == "11803596"
    assert result.get("items")[0]['metadata']['resourceVersion'] == "11803596"
    assert result.rolebindings["myrole"]["roleRef"]["namespace"] == "foo"


def test_oc_get_project_yml():
    result = openshift_get.OcGetProject(context_wrap(OC_GET_PROJECT))
    assert result.data['items'][0]['kind'] == 'Project'
    assert result.data['items'][0]['metadata']['resourceVersion'] == "11040756"
    assert result.get('items')[0]['metadata']['resourceVersion'] == "11040756"
    assert result.projects["test"]["status"]["phase"] == "Active"


def test_oc_get_role_yml():
    result = openshift_get.OcGetRole(context_wrap(OC_GET_ROLE))
    assert result.data['items'][0]['kind'] == 'Role'
    assert result.data['items'][0]['metadata']['resourceVersion'] == "94"
    assert result.get('items')[0]['metadata']['resourceVersion'] == "94"
    assert result.roles["shared-resource-viewer"]["metadata"]["uid"] == "a10c3f88-6ecc-11e6-83c6-001a4a0101f0"


def test_oc_get_pv_yml():
    result = openshift_get.OcGetPv(context_wrap(OC_GET_PV))
    assert result.data['items'][0]['kind'] == 'PersistentVolume'
    assert result.data['items'][0]['metadata']['name'] == 'registry-volume'
    assert result.get('items')[0]['metadata']['name'] == 'registry-volume'
    assert result.persistent_volumes['registry-volume-zjj']['spec']['capacity']['storage'] == '10Gi'


def test_oc_get_pvc_yml():
    result = openshift_get.OcGetPvc(context_wrap(OC_GET_PVC))
    assert result.data['items'][0]['kind'] == 'PersistentVolumeClaim'
    assert result.data['items'][0]['metadata']['name'] == 'registry-claim'
    assert result.get('items')[0]['metadata']['name'] == 'registry-claim'
    assert result.persistent_volume_claims['registry-claim-test1']['spec']['volumeName'] == 'registry-volume-zjj'


def test_oc_get_endpoints_yml():
    result = openshift_get.OcGetEndPoints(context_wrap(OC_GET_ENDPOINTS))
    assert result.data['items'][0]['kind'] == 'Endpoints'
    assert result.data['items'][0]['metadata']['name'] == 'gluster-cluster'
    assert result.get('items')[0]['metadata']['name'] == 'gluster-cluster'
    assert result.endpoints['kubernetes']['subsets'][0]["addresses"][0]["ip"] == '10.66.219.113'


def test_oc_get_node():
    result = openshift_get.OcGetNode(context_wrap(OC_GET_NODE))
    assert result.data['items'][0]['kind'] == 'Node'
    assert result.data['items'][0]['metadata']['name'] == 'master37'
    assert result.get('items')[0]['metadata']['uid'] == '64ce06a1-f4e1-11e7-aa53-001a4a0102af'
    assert result.nodes['master37']['spec']['unschedulable'] is True


def test_oc_get_rc():
    result = openshift_get.OcGetRc(context_wrap(OC_GET_RC))
    assert result.data['items'][0]['kind'] == 'ReplicationController'
    assert result.data['items'][0]['metadata']['selfLink'] == '/api/v1/namespaces/ci/replicationcontrollers/jenkins-1'
    assert result.get('items')[0]['spec']['replicas'] == 1
    assert result.replication_controllers['jenkins-1']['spec']['selector']['deployment'] == 'jenkins-1'


def test_oc_get_event():
    result = openshift_get.OcGetEvent(context_wrap(OC_GET_EVENT))
    assert result.data['items'][0]['kind'] == 'Event'
    assert result.data['items'][2]['involvedObject']['kind'] == 'ReplicationController'
    assert result.get('items')[1]['message'] == 'Successfully assigned ruby-ex-2-htczn to node237'
    assert result.events['busybox.1508ef957b1935a4']['type'] == 'Normal'


def test_oc_get_egressnetworkpolicy_yml():
    result = openshift_get.OcGetEgressNetworkPolicy(context_wrap(OC_GET_EGRESS_NETWORK_POLICY))
    assert result.data['items'][0]['kind'] == 'EgressNetworkPolicy'
    ct = result.data['items'][0]['metadata']['creationTimestamp'].replace(tzinfo=None)
    assert ct == datetime.datetime(2018, 1, 29, 3, 31, 59, tzinfo=None)
    assert result.get('items')[0]['metadata']['name'] == 'policy-test'
    assert result.egress_network_policies['policy-test']['spec']['egress'][0]['to']['dnsName'] == 'www.baidu.com'


def test_oc_get_services_doc_example():
    env = {
        'OcGetService': openshift_get.OcGetService,
        'setting_dic': openshift_get.OcGetService(context_wrap(OC_GET_SERVICE))
    }
    failed, total = doctest.testmod(openshift_get, globs=env)
    assert failed == 0


def test_oc_get_route():
    result = openshift_get.OcGetRoute(context_wrap(OC_GET_ROUTE))
    assert result.data['items'][0]['kind'] == 'Route'
    assert result.data['items'][0]['metadata']['name'] == 'docker-registry'
    assert result.get('items')[0]['spec']['host'] == 'docker-registry-default.router.default.svc.cluster.local'
    assert result.routes['docker-registry']['spec']['wildcardPolicy'] == 'None'


def test_oc_get_build():
    result = openshift_get.OcGetBuild(context_wrap(OC_GET_BUILD))
    assert result.data['items'][0]['kind'] == 'Build'
    assert result.data['items'][0]['metadata']['annotations']['openshift.io/build.pod-name'] == 'sample-app-2-build'
    assert result.get('items')[0]['status']['phase'] == 'Pending'
    assert result.started_builds['sample-app-2']['status']['config']['kind'] == 'BuildConfig'
