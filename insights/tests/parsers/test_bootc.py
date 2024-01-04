import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import bootc
from insights.parsers.bootc import BootcStatus
from insights.tests import context_wrap

BOOTC_STATUS = '''
{
   "apiVersion":"org.containers.bootc/v1alpha1",
   "kind":"BootcHost",
   "metadata":{
      "name":"host"
   },
   "spec":{
      "image":{
         "image":"192.168.124.1:5000/bootc-insights:latest",
         "transport":"registry"
      }
   },
   "status":{
      "staged":null,
      "booted":{
         "image":{
            "image":{
               "image":"192.168.124.1:5000/bootc-insights:latest",
               "transport":"registry"
            },
            "version":"stream9.20231213.0",
            "timestamp":null,
            "imageDigest":"sha256:806d77394f96e47cf99b1233561ce970c94521244a2d8f2affa12c3261961223"
         },
         "incompatible":false,
         "pinned":false,
         "ostree":{
            "checksum":"6aa32a312c832e32a2dbfe006f05e5972d9f2b86df54e747128c24e6c1fb129a",
            "deploySerial":0
         }
      },
      "rollback":{
         "image":{
            "image":{
               "image":"quay.io/centos-boot/fedora-boot-cloud:eln",
               "transport":"registry"
            },
            "version":"39.20231109.3",
            "timestamp":null,
            "imageDigest":"sha256:92e476435ced1c148350c660b09c744717defbd300a15d33deda5b50ad6b21a0"
         },
         "incompatible":false,
         "pinned":false,
         "ostree":{
            "checksum":"56612a5982b7f12530988c970d750f89b0489f1f9bebf9c2a54244757e184dd8",
            "deploySerial":0
         }
      },
      "type":"bootcHost"
   }
}
'''.strip()


def test_bootc_doc_examples():
    env = {
        "bootc_status": BootcStatus(context_wrap(BOOTC_STATUS)),
    }
    failed, total = doctest.testmod(bootc, globs=env)
    assert failed == 0


def test_bootc_status_skip():
    with pytest.raises(SkipComponent) as ex:
        BootcStatus(context_wrap(""))
    assert "Empty output." in str(ex)


def test_bootc_status():
    bs = BootcStatus(context_wrap(BOOTC_STATUS))
    assert bs['apiVersion'] == 'org.containers.bootc/v1alpha1'
    assert bs['status']['booted']['image']['version'] == 'stream9.20231213.0'
