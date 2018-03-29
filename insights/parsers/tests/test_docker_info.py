from insights.parsers import dockerinfo
from insights.tests import context_wrap


docker_info1 = """
Containers: 0
Images: 1
Server Version: 1.9.1
Storage Driver: devicemapper
 Pool Name: docker-253:0-10499681-pool
 Pool Blocksize: 65.54 kB
 Base Device Size: 107.4 GB
 Backing Filesystem:
 Data file: /dev/loop0
 Metadata file: /dev/loop1
 Data Space Used: 295.9 MB
 Data Space Total: 107.4 GB
 Data Space Available: 3.611 GB
 Metadata Space Used: 716.8 kB
 Metadata Space Total: 2.147 GB
 Metadata Space Available: 2.147 GB
 Udev Sync Supported: true
 Deferred Removal Enabled: false
 Deferred Deletion Enabled: false
 Deferred Deleted Device Count: 0
 Data loop file: /var/lib/docker/devicemapper/devicemapper/data
 Metadata loop file: /var/lib/docker/devicemapper/devicemapper/metadata
 Library Version: 1.02.107-RHEL7 (2015-12-01)
Execution Driver: native-0.2
Logging Driver: json-file
Kernel Version: 3.10.0-327.el7.x86_64
Operating System: Employee SKU
CPUs: 1
Total Memory: 993 MiB
Name: dhcp.example.com
ID: QPOX:46K6:RZK5:GPBT:DEUD:QM6H:5LRE:R63D:42DI:4BH3:6ZOZ:5EUM
"""

docker_info2 = """
Containers: 0
Images: 0
Server Version: 1.9.1
Storage Driver: devicemapper
 Pool Name: rhel-docker--pool
 Pool Blocksize: 524.3 kB
 Base Device Size: 107.4 GB
 Backing Filesystem: xfs
 Data file:
 Metadata file:
 Data Space Used: 62.39 MB
 Data Space Total: 3.876 GB
 Data Space Available: 3.813 GB
 Metadata Space Used: 40.96 kB
 Metadata Space Total: 8.389 MB
 Metadata Space Available: 8.348 MB
 Udev Sync Supported: true
 Deferred Removal Enabled: true
 Deferred Deletion Enabled: true
 Deferred Deleted Device Count: 0
 Library Version: 1.02.107-RHEL7 (2015-12-01)
Execution Driver: native-0.2
Logging Driver: json-file
Kernel Version: 3.10.0-327.el7.x86_64
Operating System: Employee SKU
CPUs: 1
Total Memory: 993 MiB
Name: dhcp.example.com
ID: QPOX:46K6:RZK5:GPBT:DEUD:QM6H:5LRE:R63D:42DI:4BH3:6ZOZ:5EUM
"""

docker_info3 = """
Cannot connect to the Docker daemon. Is the docker daemon running on this host?
"""


def test_docker_info():
    result = dockerinfo.DockerInfo(context_wrap(docker_info1)).data
    sub_key = ["Data loop file", "Server Version", "Data file"]
    sub_result = dict([(key, result[key]) for key in sub_key])
    expected = {'Data loop file': '/var/lib/docker/devicemapper/devicemapper/data', 'Data file': '/dev/loop0', 'Server Version': '1.9.1'}
    assert expected == sub_result

    result = dockerinfo.DockerInfo(context_wrap(docker_info2)).data
    assert result.get("Data loop file") is None

    result = dockerinfo.DockerInfo(context_wrap(docker_info3)).data
    assert result == {}
