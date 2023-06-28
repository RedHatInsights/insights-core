import doctest
from insights.parsers import eap_json_reports
from insights.parsers.eap_json_reports import EAPJSONReports
from insights.tests import context_wrap

EAP_JSON_DATA_1 = """
{
    "version": "1.0.0",
    "idHash": "e38277334d0f6b6fdc6f3b831fb102cdd70f04faab5c38b0be36fb1aacb4236eca86643d3e88fac6f47fabda8f9990e80436afa5a0e071890fd572238e727d2e",
    "basic": {
        "app.user.dir": "/opt/t_eap/jboss-eap-7.4",
        "java.specification.version": "1.8",
        "java.runtime.version": "1.8.0_362-b09",
        "jvm.args": [
            "-D[Standalone]",
            "-verbose:gc"
        ],
        "java.vm.name": "OpenJDK 64-Bit Server VM",
        "java.vm.specification.version": "1.8",
        "system.cores.logical": 2
    },
    "jars": {
        "version": "1.0.0",
        "jars": [
            {
                "name": "jboss-modules.jar",
                "version": "1.12.0.Final-redhat-00001",
                "attributes": {
                    "sha1Checksum": "82a8c99551533f4448675f273665cb6d7b750511",
                    "version": "1.12.0.Final-redhat-00001"
                }
            }
        ]
    },
    "eap": {
        "name": "Red Hat JBoss EAP",
        "version": "1.0.0",
        "eap-modules": {
            "version": "1.0.0",
            "jars": [
                {
                    "name": "activemq-artemis-native-1.0.2.redhat-00004.jar",
                    "version": "1.0.2.redhat-00004",
                    "attributes": {
                        "sha1Checksum": "1aaf77fa3aed8377c375770529fa66d5faa5c9c1",
                        "overridden": "unknown",
                        "version": "1.0.2.redhat-00004"
                    }
                },
                {
                    "name": "yasson-1.0.10.redhat-00001.jar",
                    "version": "1.0.10.redhat-00001",
                    "attributes": {
                        "sha1Checksum": "75b7dedb6d33b1ed26598a6cc57b75491adba959",
                        "Implementation-Vendor": "Oracle Corporation",
                        "path": "system/layers/base/org/eclipse/yasson/main/yasson-1.0.10.redhat-00001.jar",
                        "groupId": "org.eclipse",
                        "sha256Checksum": "88609252b5a89c11618a78365c04c8335ce7be8cc33629a9f53ee42eff7f4567",
                        "artifactId": "yasson",
                        "sha512Checksum": "1afdbc109d2e5738f5c9f9fcf1e2090214d2beb50f48f2b1ed084f7fa895aeb63035452eb0242a7a234aa38799c9ab3166381cd2a799fb6e2273823fa30861bf",
                        "Implementation-Vendor-Id": "org.eclipse",
                        "overridden": "unknown",
                        "version": "1.0.10.redhat-00001"
                    }
                }
            ]
        },
        "eap-configuration": {
            "version": "16.0.0",
            "configuration": {
                "launch-type": "STANDALONE",
                "server-state": "running",
                "suspend-state": "RUNNING",
                "uuid": "254d541c-a9ab-4df4-8bb7-2bc84447beb7",
                "core-service": {
                    "management": {
                        "access": {
                            "authorization": {
                                "provider": null
                            }
                        },
                        "ldap-connection": null,
                        "management-interface": {
                            "http-interface": {
                                "allowed-origins": null,
                                "console-enabled": true,
                                "constant-headers": null,
                                "http-authentication-factory": null,
                                "http-upgrade": null,
                                "http-upgrade-enabled": true,
                                "sasl-protocol": "remote",
                                "secure-socket-binding": null,
                                "security-realm": null,
                                "server-name": null,
                                "socket-binding": "management-http",
                                "ssl-context": null
                            }
                        },
                        "security-realm": null,
                        "service": {
                            "management-operations": {
                                "active-operation": {
                                    "-1638739660": {
                                        "access-mechanism": null,
                                        "address": [],
                                        "caller-thread": "ServerService Thread Pool -- 1",
                                        "cancelled": false,
                                        "domain-rollout": false,
                                        "domain-uuid": null,
                                        "exclusive-running-time": -1,
                                        "execution-status": "executing",
                                        "operation": "read-resource",
                                        "running-time": 141095723
                                    }
                                }
                            }
                        }
                    },
                    "service-container": {},
                    "module-loading": {
                        "module-roots": [
                            "/opt/t_eap/jboss-eap-7.4/modules",
                            "/opt/t_eap/jboss-eap-7.4/modules/system/layers/base"
                        ]
                    },
                    "server-environment": {
                        "base-dir": "/opt/t_eap/jboss-eap-7.4/standalone",
                        "config-dir": "/opt/t_eap/jboss-eap-7.4/standalone/configuration",
                        "config-file": "/opt/t_eap/jboss-eap-7.4/standalone/configuration/standalone.xml",
                        "content-dir": "/opt/t_eap/jboss-eap-7.4/standalone/data/content",
                        "data-dir": "/opt/t_eap/jboss-eap-7.4/standalone/data",
                        "deploy-dir": "/opt/t_eap/jboss-eap-7.4/standalone/data/content",
                        "ext-dirs": [
                            "/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.362.b09-2.el8_7.x86_64/jre/lib/ext",
                            "/usr/java/packages/lib/ext"
                        ],
                        "home-dir": "/opt/t_eap/jboss-eap-7.4",
                        "host-name": "rhel8testing",
                        "initial-running-mode": "NORMAL",
                        "launch-type": "STANDALONE",
                        "log-dir": "/opt/t_eap/jboss-eap-7.4/standalone/log",
                        "modules-dir": "/opt/t_eap/jboss-eap-7.4/modules",
                        "node-name": "rhel8testing",
                        "qualified-host-name": "rhel8testing",
                        "server-name": "rhel8testing",
                        "start-gracefully": true,
                        "start-suspended": false,
                        "temp-dir": "/opt/t_eap/jboss-eap-7.4/standalone/tmp"
                    },
                    "patching": {
                        "cumulative-patch-id": "base",
                        "patches": [],
                        "version": "7.4.11.GA",
                        "addon": null,
                        "layer": {
                            "base": {
                                "cumulative-patch-id": "base",
                                "patches": []
                            }
                        },
                        "patch-stream": {
                            "JBoss EAP": {
                                "cumulative-patch-id": "base",
                                "patches": [],
                                "version": "7.4.11.GA",
                                "addon": null,
                                "layer": {
                                    "base": {
                                        "cumulative-patch-id": "base",
                                        "patches": []
                                    }
                                }
                            }
                        }
                    }
                },
                "deployment": {
                    "helloworld.war": {
                        "content": [
                            {
                                "hash": {
                                    "BYTES_VALUE": "y/AofkRXxfZVXaEY/HeBXBQ+LSo="
                                }
                            }
                        ],
                        "disabled-time": null,
                        "disabled-timestamp": null,
                        "enabled": true,
                        "enabled-time": 1686660031851,
                        "enabled-timestamp": "2023-06-13 12:40:31,851 UTC",
                        "managed": true,
                        "name": "helloworld.war",
                        "owner": [
                            {
                                "subsystem": "deployment-scanner"
                            },
                            {
                                "scanner": "default"
                            }
                        ],
                        "persistent": false,
                        "runtime-name": "helloworld.war",
                        "status": "OK",
                        "subdeployment": null,
                        "subsystem": {
                            "undertow": {
                                "active-sessions": 0,
                                "servlet": null,
                                "websocket": null
                            },
                            "logging": {
                                "configuration": {
                                    "default": {
                                        "error-manager": null,
                                        "logger": {
                                            "ROOT": {
                                                "filter": null,
                                                "handlers": [
                                                    "FILE",
                                                    "CONSOLE"
                                                ],
                                                "level": "INFO",
                                                "use-parent-handlers": null
                                            },
                                            "com.arjuna": {
                                                "filter": null,
                                                "handlers": [],
                                                "level": "WARN",
                                                "use-parent-handlers": true
                                            }
                                        },
                                        "pojo": null
                                    }
                                }
                            }
                        }
                    }
                },
                "deployment-overlay": null,
                "extension": {
                    "org.jboss.as.clustering.infinispan": {
                        "module": "org.jboss.as.clustering.infinispan",
                        "subsystem": {
                            "infinispan": {
                                "management-major-version": 14,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.undertow": {
                        "module": "org.wildfly.extension.undertow",
                        "subsystem": {
                            "undertow": {
                                "management-major-version": 11,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    }
                },
                "interface": {
                    "management": {
                        "any": null,
                        "any-address": null,
                        "inet-address": {
                            "EXPRESSION_VALUE": "${jboss.bind.address.management:127.0.0.1}"
                        },
                        "link-local-address": null,
                        "up": null,
                        "virtual": null
                    },
                    "public": {
                        "any": null,
                        "any-address": null,
                        "inet-address": {
                            "EXPRESSION_VALUE": "${jboss.bind.address:127.0.0.1}"
                        },
                        "link-local-address": null,
                        "up": null,
                        "virtual": null
                    }
                },
                "path": {
                    "jboss.server.log.dir": {
                        "name": "jboss.server.log.dir",
                        "path": "/opt/t_eap/jboss-eap-7.4/standalone/log",
                        "read-only": true,
                        "relative-to": null
                    },
                    "java.home": {
                        "name": "java.home",
                        "path": "/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.362.b09-2.el8_7.x86_64/jre",
                        "read-only": true,
                        "relative-to": null
                    }
                },
                "socket-binding-group": {
                    "standard-sockets": {
                        "default-interface": "public",
                        "name": "standard-sockets",
                        "port-offset": {
                            "EXPRESSION_VALUE": "${jboss.socket.binding.port-offset:0}"
                        },
                        "local-destination-outbound-socket-binding": null,
                        "remote-destination-outbound-socket-binding": {
                            "mail-smtp": {
                                "fixed-source-port": false,
                                "host": {
                                    "EXPRESSION_VALUE": "${jboss.mail.server.host:localhost}"
                                },
                                "port": {
                                    "EXPRESSION_VALUE": "${jboss.mail.server.port:25}"
                                },
                                "source-interface": null,
                                "source-port": null
                            }
                        },
                        "socket-binding": {
                            "ajp": {
                                "bound": false,
                                "bound-address": null,
                                "bound-port": null,
                                "client-mappings": null,
                                "fixed-port": false,
                                "interface": null,
                                "multicast-address": null,
                                "multicast-port": null,
                                "name": "ajp",
                                "port": {
                                    "EXPRESSION_VALUE": "${jboss.ajp.port:8009}"
                                }
                            },
                            "txn-status-manager": {
                                "bound": false,
                                "bound-address": null,
                                "bound-port": null,
                                "client-mappings": null,
                                "fixed-port": false,
                                "interface": null,
                                "multicast-address": null,
                                "multicast-port": null,
                                "name": "txn-status-manager",
                                "port": 4713
                            }
                        }
                    }
                },
                "subsystem": {
                    "core-management": {
                        "process-state-listener": null,
                        "service": null
                    },


                    "jca": {
                        "archive-validation": {
                            "archive-validation": {
                                "enabled": true,
                                "fail-on-error": true,
                                "fail-on-warn": false
                            }
                        },
                        "workmanager": {
                            "default": {
                                "elytron-enabled": false,
                                "name": "default",
                                "long-running-threads": {
                                    "default": {
                                        "allow-core-timeout": false,
                                        "keepalive-time": {
                                            "time": 10,
                                            "unit": "SECONDS"
                                        },
                                        "largest-thread-count": 0,
                                        "thread-factory": null
                                    }
                                },
                                "short-running-threads": {
                                    "default": {
                                        "allow-core-timeout": false,
                                        "thread-factory": null
                                    }
                                },
                                "statistics": {
                                    "local": {
                                        "dowork-accepted": 0,
                                        "workmanager-statistics-enabled": true
                                    }
                                }
                            }
                        }
                    },
                    "jdr": {},
                    "jmx": {
                        "non-core-mbean-sensitivity": null,
                        "remoting-connector": {
                            "jmx": {
                                "use-management-endpoint": true
                            }
                        }
                    },
                    "jpa": {
                        "default-datasource": null,
                        "default-extended-persistence-inheritance": "DEEP"
                    },
                    "jsf": {
                        "default-jsf-impl-slot": "main",
                        "disallow-doctype-decl": null
                    },
                    "mail": {
                        "mail-session": {
                            "default": {
                                "debug": false,
                                "from": null,
                                "jndi-name": "java:jboss/mail/Default",
                                "custom": null,
                                "server": {
                                    "smtp": {
                                        "credential-reference": null,
                                        "outbound-socket-binding-ref": "mail-smtp",
                                        "password": null,
                                        "ssl": false,
                                        "tls": false,
                                        "username": null
                                    }
                                }
                            }
                        }
                    },

                    "pojo": {},
                    "security": {
                        "deep-copy-subject-mode": null,
                        "vault": null
                    },
                    "security-manager": {
                        "deployment-permissions": {
                            "default": {
                                "maximum-permissions": [
                                    {
                                        "class": "java.security.AllPermission"
                                    }
                                ],
                                "minimum-permissions": null
                            }
                        }
                    },
                    "transactions": {
                        "average-commit-time": 0,
                        "commit-markable-resource": null,
                        "log-store": {
                            "log-store": {
                                "expose-all-logs": false,
                                "type": "default",
                                "transactions": null
                            }
                        }
                    },
                    "undertow": {
                        "default-security-domain": null,
                        "buffer-cache": {
                            "default": {
                                "buffer-size": 1024,
                                "buffers-per-region": 1024,
                                "max-regions": 10
                            }
                        },
                        "byte-buffer-pool": null,
                        "configuration": {
                            "filter": {
                                "custom-filter": null,
                                "rewrite": null
                            },
                            "handler": {
                                "file": {
                                    "welcome-content": {
                                        "cache-buffer-size": 1024,
                                        "path": {
                                            "EXPRESSION_VALUE": "${jboss.home.dir}/welcome-content"
                                        },
                                        "safe-symlink-paths": null
                                    }
                                },
                                "reverse-proxy": null
                            }
                        },
                        "server": {
                            "default-server": {
                                "default-host": "default-host",
                                "servlet-container": "default",
                                "ajp-listener": null,
                                "host": {
                                    "default-host": {
                                        "alias": [
                                            "localhost"
                                        ],
                                        "default-response-code": 404,
                                        "setting": {
                                            "http-invoker": {
                                                "http-authentication-factory": null,
                                                "path": "wildfly-services",
                                                "security-realm": null
                                            }
                                        }
                                    }
                                },
                                "http-listener": {
                                    "default": {
                                        "allow-encoded-slash": false,
                                        "bytes-sent": 0,
                                        "certificate-forwarding": false,
                                        "decode-url": true,
                                        "disallowed-methods": [
                                            "TRACE"
                                        ],
                                        "enable-http2": true,
                                        "worker": "default",
                                        "write-timeout": null
                                    }
                                },
                                "https-listener": {
                                    "https": {
                                        "allow-encoded-slash": false,
                                        "write-timeout": null
                                    }
                                }
                            }
                        },
                        "servlet-container": {
                            "default": {
                                "allow-non-standard-wrappers": false,
                                "mime-mapping": null,
                                "setting": {
                                    "jsp": {
                                        "check-interval": 0,
                                        "development": false,
                                        "x-powered-by": true
                                    },
                                    "websockets": {
                                        "buffer-pool": "default",
                                        "deflater-level": 0,
                                        "dispatch-to-worker": true,
                                        "per-message-deflate": false,
                                        "worker": "default"
                                    }
                                },
                                "welcome-file": null
                            }
                        }
                    },
                    "webservices": {
                        "modify-wsdl-address": true,
                        "endpoint-config": {
                            "Standard-Endpoint-Config": {
                                "post-handler-chain": null,
                                "pre-handler-chain": null,
                                "property": null
                            },
                            "Recording-Endpoint-Config": {
                                "post-handler-chain": null,
                                "pre-handler-chain": {
                                    "recording-handlers": {
                                        "protocol-bindings": "##SOAP11_HTTP ##SOAP11_HTTP_MTOM ##SOAP12_HTTP ##SOAP12_HTTP_MTOM",
                                        "handler": {
                                            "RecordingHandler": {
                                                "class": "org.jboss.ws.common.invocation.RecordingServerHandler"
                                            }
                                        }
                                    }
                                },
                                "property": null
                            }
                        }
                    }
                }
            }
        },
        "eap-deployments": {
            "version": "1.0.0",
            "deployments": [
                {
                    "name": "helloworld.war",
                    "archives": [
                        {
                            "name": "helloworld.war",
                            "version": " ",
                            "attributes": {
                                "sha1Checksum": "cbf0287e4457c5f6555da118fc77815c143e2d2a",
                                "sha256Checksum": "f41848d63c4098b96beb5c3eb51139de48757738fa093aca1bf666c95608a6ca",
                                "sha512Checksum": "70389a1e8d8581ec6706e4d731aa617d09864a602059b8bb505c68f311f83b9cc45b66f3abd25593dd573675b2df4e5fbbc1008a8f0f03fd5ae60e2f323bd85d",
                                "deployment": "helloworld.war"
                            }
                        }
                    ]
                }
            ]
        }
    }
}
""".strip()


def test_eap_json_report():
    result = EAPJSONReports(context_wrap(EAP_JSON_DATA_1))
    assert result.data['version'] == '1.0.0'
    assert result.data['basic']['app.user.dir'] == "/opt/t_eap/jboss-eap-7.4"


def test_doc_examples():
    env = {
        'eap_json_report': EAPJSONReports(context_wrap(EAP_JSON_DATA_1)),
    }
    failed, total = doctest.testmod(eap_json_reports, globs=env)
    assert failed == 0
