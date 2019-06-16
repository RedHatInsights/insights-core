#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Module to interact with Satellite Based Certificates
"""
from __future__ import print_function
import os
import logging

logger = logging.getLogger(__name__)

# RHSM and Subscription Manager
RHSM_CONFIG = None
try:
    from rhsm.config import initConfig
    from rhsm.certificate import create_from_pem
    RHSM_CONFIG = initConfig()
except ImportError:
    logger.debug("Could not load RHSM modules")


# Class for dealing with rhsmCertificates
class rhsmCertificate:

    try:
        PATH = RHSM_CONFIG.get('rhsm', 'consumerCertDir')
    except:
        pass

    KEY = 'key.pem'
    CERT = 'cert.pem'

    @classmethod
    def keypath(cls):
        return os.path.join(cls.PATH, cls.KEY)

    @classmethod
    def certpath(cls):
        return os.path.join(cls.PATH, cls.CERT)

    @classmethod
    def read(cls):
        f = open(cls.keypath())
        key = f.read()
        f.close()
        f = open(cls.certpath())
        cert = f.read()
        f.close()
        return rhsmCertificate(key, cert)

    @classmethod
    def exists(cls):
        return (os.path.exists(cls.keypath()) and
                os.path.exists(cls.certpath()))

    @classmethod
    def existsAndValid(cls):
        if cls.exists():
            try:
                cls.read()
                return True
            except Exception as e:
                print(e)
        return False

    def __init__(self, keystring, certstring):
        self.key = keystring
        self.cert = certstring
        self.x509 = create_from_pem(certstring)

    def getConsumerId(self):
        subject = self.x509.subject
        return subject.get('CN')

    def getConsumerName(self):
        altName = self.x509.alt_name
        return altName.replace("DirName:/CN=", "")

    def getSerialNumber(self):
        return self.x509.serial

    def __str__(self):
        return 'consumer: name="%s", uuid%s' % \
               (self.getConsumerName(),
                self.getConsumerId())
