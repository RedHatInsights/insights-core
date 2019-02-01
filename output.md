# Insights Core Run

## Arguments


## Rules Executed
### [META] telemetry.rules.plugins.container.docker_container_metadata.report
```
None

```

### [META] telemetry.rules.plugins.container.docker_host_metadata.report
```
None:
    docker_container_count: u'1'
    docker_containers     : {u'a0cc530e34772e7254ed1c90f0dda428b8a227f8feb57255188366dd70014b5e': u'dbb0a'}
    docker_image_count    : u'13'
    docker_images         : {u'sha256:074cb770042a0c09547d80a279e1549890796b5e57d3e22722c7b4abee772d8d': [u'docker.io/jenkinsci/blueocean:latest'],
                             u'sha256:31a8ca8e9063a1ee527141959c9cd00f6cc496b4467206a7dfbe211201b55a4a': [],
                             u'sha256:5182e96772bf11f4b912658e265dfe0db8bd314475443b6434ea708784192892': [u'docker.io/centos:latest'],
                             u'sha256:5cf75c4cd4cb4e8f0224efc5b45fc68443988a66f5ade00f688940333154190e': [u'bfahr/centos:latest'],
                             u'sha256:60b509e2d71414ad8760aa503380bd165ec22242d0bd83342938fd1ea562c116': [u'docker.io/cdrx/pyinstaller-linux:python2'],
                             u'sha256:7c306adf1b3d63769c93ac0b3b90e1dacd1ab4312d90f47872f4c55a97d8056c': [u'docker.io/python:2-alpine'],
                             u'sha256:a60d7041669c086ecde92d190fe7d7b4343485c6d06ae18ebf083dd3fc5443b1': [],
                             u'sha256:ae5c51b9a8c5c56e46411f7df20e663990dc06e3941131bb9fa23db97309b6f3': [u'docker.io/qnib/pytest:latest'],
                             u'sha256:b90d3f1fb616a83e800e9c20201bc52069fe413581c8c05e9ba9fd0e7f4c405e': [],
                             u'sha256:cd14cecfdb3a657ba7d05bea026e7ac8b9abafc6e5c66253ab327c7211fa6281': [u'docker.io/jenkins:latest'],
                            <...3 more lines...>

```

### [META] telemetry.rules.plugins.container.docker_image_metadata.report
```
None:
    docker_image_id: u'sha256:a60d7041669c086ecde92d190fe7d7b4343485c6d06ae18ebf083dd3fc5443b1'

```

### [META] telemetry.rules.plugins.networking.listening_processes_on_ports_metadata.report
```
None:
    listening_processes: [{'ip_addr': u'127.0.0.1', 'port': u'6942', 'process_name': u'java'},
                          {'ip_addr': u'', 'port': u'::39355', 'process_name': u'java'}]

```

### [META] telemetry.rules.plugins.non_kernel.timezone_metadata.report
```
None:
    timezone_information: {'timezone': u'CST', 'utcoffset': -21600}

```

### [META] telemetry.rules.plugins.release_metadata.report
```
None:
    rhel_version: '-1.-1'

```

### [META] telemetry.rules.plugins.non_kernel.rpm_listing.report
```
Number of packages installed: 5362
```

### [FAIL] telemetry.rules.plugins.container.docker_loopback_convert.report
```
LOOPBACK_USED:
    Data_loop_file: u'/var/lib/docker/devicemapper/devicemapper/data'

```

### [FAIL] telemetry.rules.plugins.kernel.other_linux_system.report
```
OTHER_LINUX_SYSTEM:
    build_info : u'[    0.000000] Linux version 4.18.17-200.fc28.x86_64 (mockbuild@bkernel03.phx2.fedoraproject.org) (gcc version 8.2.1 20181011 (Red Hat 8.2.1-4) (GCC)) #1 SMP Mon Nov 5 18:04:28 UTC 2018'
    kernel     : u'4.18.17-200.fc28.x86_64'
    other_linux: 'Fedora'
    release    : u'fedora-release-28-3.noarch'

```

### [FAIL] telemetry.rules.plugins.service.ntp_peers.report
```
NTP_TWO_CLOCKS_CONFIGURED:
    clock_source: 'Chrony'
    clocks      : ['clock01.util.phx2.redhat.com iburst', 'clock02.util.phx2.redhat.com iburst']
    daemon      : 'chronyd'
    kcs         : 'https://access.redhat.com/solutions/58025'
    message     : 'Two clocks configured - impossible to tell which source is correct'

```


## Rule Execution Summary
```
 Exceptions  : 0
 Missing Deps: 318
 Metadata Key: 1
 Failed      : 3
 Passed      : 0
 Metadata    : 6
```
