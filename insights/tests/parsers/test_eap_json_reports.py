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
        "java.class.path": "/opt/t_eap/jboss-eap-7.4/jboss-modules.jar",
        "app.client.exception": "I4ASR0019: org.apache.http.client.ClientProtocolException",
        "system.os.name": "Linux",
        "app.transport.type.file": "rhel",
        "java.vm.vendor": "Red Hat, Inc.",
        "app.transport.type.https": "mtls",
        "jvm.packages": "[package org.jboss.as.controller.descriptions, WildFly: Controller Core, version 15.0, package com.sun.jmx.defaults, Java Platform API Specification, version 1.8, package sun.util, Java Platform API Specification, version 1.8, package org.jboss.modules.xml, JBoss Modules, version 1.12, package org.jboss.dmr, JBoss Dynamic Model Representation, version 1.5, package org.wildfly.security.sasl.anonymous, WildFly Elytron - SASL Anonymous, version 1.15, package org.wildfly.security.http.spnego, WildFly Elytron - HTTP SPNEGO, version 1.15, package java.lang.management, Java Platform API Specification, version 1.8, package sun.security.provider, Java Platform API Specification, version 1.8, package java.lang.ref, Java Platform API Specification, version 1.8, package org.jboss.as.controller.client.helpers.domain, WildFly: Controller Client, version 15.0, package org.wildfly.security.sasl.localuser, WildFly Elytron - SASL JBOSS-LOCAL-USER, version 1.15, package java.util.stream, Java Platform API Specification, version 1.8, package org.wildfly.security.sasl.otp, WildFly Elytron - SASL OTP, version 1.15, package org.jboss.modules.maven, JBoss Modules, version 1.12, package org.wildfly.security.auth.server._private, WildFly Elytron - Auth Server, version 1.15, package java.util.regex, Java Platform API Specification, version 1.8, package org.wildfly.security.sasl.plain, WildFly Elytron - SASL Plain, version 1.15, package org.jboss.as.controller.access.management, WildFly: Controller Core, version 15.0, package org.apache.http.client, Apache HttpClient, version 4.5, package org.wildfly.security.auth.realm, WildFly Elytron - Realm, version 1.15, package javax.net, Java Platform API Specification, version 1.8, package org.jboss.as.server.deployment.service, WildFly: Server, version 15.0, package java.time.chrono, Java Platform API Specification, version 1.8, package java.nio.charset.spi, Java Platform API Specification, version 1.8, package org.jboss.as.controller.parsing, WildFly: Controller Core, version 15.0, package org.wildfly.common.context, wildfly-common, version 1.5, package sun.reflect.generics.repository, Java Platform API Specification, version 1.8, package org.jboss.as.controller.interfaces, WildFly: Controller Core, version 15.0, package java.time.format, Java Platform API Specification, version 1.8, package org.jboss.modules.security, JBoss Modules, version 1.12, package org.wildfly.security.password.spec, WildFly Elytron - Credential, version 1.15, package org.wildfly.security.keystore, WildFly Elytron - Credential, version 1.15, package sun.net.www.protocol.file, Java Platform API Specification, version 1.8, package sun.security.tools, Java Platform API Specification, version 1.8, package sun.security.rsa, Java Platform API Specification, version 1.8, package sun.security.jca, Java Platform API Specification, version 1.8, package javax.management.remote, Java Platform API Specification, version 1.8, package com.redhat.insights.logging, package org.wildfly.security.provider.util, WildFly Elytron - Provider Util, version 1.15, package sun.security.validator, Java Platform API Specification, version 1.8, package org.jboss.vfs.protocol, JBoss VFS, version 3.2.17.Final-redhat-00001, package org.wildfly.security.manager, WildFly Elytron - Security Manager, version 1.15, package sun.net.www, Java Platform API Specification, version 1.8, package org.jboss.as.server.suspend, WildFly: Server, version 15.0, package org.jboss.as.server.controller.descriptions, WildFly: Server, version 15.0, package org.jboss.as.controller.remote, WildFly: Controller Core, version 15.0, package org.wildfly.security.authz.jacc, WildFly Elytron - JACC, version 1.15, package org.wildfly.security.evidence, WildFly Elytron - Credential, version 1.15, package sun.security.provider.certpath, Java Platform API Specification, version 1.8, package sun.net.www.protocol.jar, Java Platform API Specification, version 1.8, package org.wildfly.security.http.bearer, WildFly Elytron - HTTP Bearer, version 1.15, package java.util, Java Platform API Specification, version 1.8, package org.jboss.as.controller.persistence, WildFly: Controller Core, version 15.0, package java.nio.channels.spi, Java Platform API Specification, version 1.8, package sun.security.ssl, Java Platform API Specification, version 1.8, package org.jboss.as.controller.resource, WildFly: Controller Core, version 15.0, package org.apache.http.client.methods, Apache HttpClient, version 4.5, package org.wildfly.security.http.basic, WildFly Elytron - HTTP Basic, version 1.15, package com.fasterxml.jackson.databind.module, jackson-databind, version 2.12.7.redhat-00003, package org.jboss.as.controller.descriptions.common, WildFly: Controller Core, version 15.0, package org.jboss.modules.log, JBoss Modules, version 1.12, package org.jboss.as.server.deployment.module.descriptor, WildFly: Server, version 15.0, package org.wildfly.security.authz, WildFly Elytron - Auth Server, version 1.15, package org.wildfly.security.http.cert, WildFly Elytron - HTTP Cert, version 1.15, package org.wildfly.security.auth.server, WildFly Elytron - Auth Server, version 1.15, package org.wildfly.security.audit, WildFly Elytron - Audit Logging, version 1.15, package org.wildfly.security.http.digest, WildFly Elytron - HTTP DIGEST, version 1.15, package java.util.zip, Java Platform API Specification, version 1.8, package sun.nio.fs, Java Platform API Specification, version 1.8, package org.jboss.as.controller.access, WildFly: Controller Core, version 15.0, package org.wildfly.security.password, WildFly Elytron - Credential, version 1.15, package sun.util.calendar, Java Platform API Specification, version 1.8, package sun.security.pkcs12, Java Platform API Specification, version 1.8, package com.redhat.insights.http, package javax.management, Java Platform API Specification, version 1.8, package com.sun.crypto.provider, Java Platform API Specification, version 1.8, package sun.reflect, Java Platform API Specification, version 1.8, package org.wildfly.security.sasl.oauth2, WildFly Elytron - SASL OAuth2, version 1.15, package javax.security.auth.spi, Java Platform API Specification, version 1.8, package org.jboss.as.controller.operations.common, WildFly: Controller Core, version 15.0, package org.wildfly.security.permission, WildFly Elytron - Permission, version 1.15, package org.wildfly.security.auth.jaspi, WildFly Elytron - JASPI, version 1.15, package sun.invoke.empty, Java Platform API Specification, version 1.8, package sun.text.normalizer, Java Platform API Specification, version 1.8, package org.jboss.as.server.deployment.dependencies, WildFly: Server, version 15.0, package org.wildfly.security.http, WildFly Elytron - HTTP, version 1.15, package org.jboss.as.server.controller.git, WildFly: Server, version 15.0, package java.text.spi, Java Platform API Specification, version 1.8, package javax.management.openmbean, Java Platform API Specification, version 1.8, package java.net, Java Platform API Specification, version 1.8, package org.wildfly.common.math, wildfly-common, version 1.5, package java.time, Java Platform API Specification, version 1.8, package org.jboss.as.repository, WildFly: Deployment Repository, version 15.0, package org.jboss.msc.inject, JBoss Modular Service Container, version 1.4, package java.nio.file.attribute, Java Platform API Specification, version 1.8, package org.jboss.vfs.spi, JBoss VFS, version 3.2.17.Final-redhat-00001, package org.wildfly.client.config, WildFly Client Configuration, version 1.0.1.Final-redhat-00001, package java.util.concurrent, Java Platform API Specification, version 1.8, package sun.launcher, Java Platform API Specification, version 1.8, package sun.nio.cs, Java Platform API Specification, version 1.8, package sun.nio.ch, Java Platform API Specification, version 1.8, package com.redhat.insights, package org.jboss.as.server.operations, WildFly: Server, version 15.0, package org.wildfly.security.digest, WildFly Elytron - Digest, version 1.15, package org.jboss.as.server.security, WildFly: Server, version 15.0, package org.jboss.as.controller.registry, WildFly: Controller Core, version 15.0, package org.apache.http.util, HttpComponents Apache HttpCore, version 4.4.14.redhat-00001, package org.jboss.as.controller.client.helpers, WildFly: Controller Client, version 15.0, package org.wildfly.security.auth.server.event, WildFly Elytron - Auth Server, version 1.15, package sun.security.util, Java Platform API Specification, version 1.8, package org.wildfly.security.x500.cert.acme, WildFly Elytron - X.500 Certificate ACME, version 1.15, package javax.management.loading, Java Platform API Specification, version 1.8, package org.jboss.as.controller.operations.global, WildFly: Controller Core, version 15.0, package org.jboss.logging, JBoss Logging 3, version 3.4, package java.math, Java Platform API Specification, version 1.8, package sun.net.sdp, Java Platform API Specification, version 1.8, package sun.security.pkcs, Java Platform API Specification, version 1.8, package com.redhat.insights.tls, package org.jboss.as.controller.capability, WildFly: Controller Core, version 15.0, package javax.net.ssl, Java Platform API Specification, version 1.8, package java.nio, Java Platform API Specification, version 1.8, package org.wildfly.security.util, WildFly Elytron - Util, version 1.15, package com.sun.jmx.interceptor, Java Platform API Specification, version 1.8, package sun.util.locale.provider, Java Platform API Specification, version 1.8, package java.util.function, Java Platform API Specification, version 1.8, package org.jboss.as.version, WildFly: Version, version 15.0, package com.fasterxml.jackson.databind.jsonFormatVisitors, jackson-databind, version 2.12.7.redhat-00003, package org.jboss.as.controller.extension, WildFly: Controller Core, version 15.0, package org.wildfly.security.sasl, WildFly Elytron - SASL, version 1.15, package org.wildfly.security.sasl.util, WildFly Elytron - SASL, version 1.15, package sun.util.resources, Java Platform API Specification, version 1.8, package java.util.jar, Java Platform API Specification, version 1.8, package org.jboss.as.controller.transform.description, WildFly: Controller Core, version 15.0, package org.jboss.as.controller.management, WildFly: Controller Core, version 15.0, package org.apache.http.conn.routing, Apache HttpClient, version 4.5, package jdk.internal.org.objectweb.asm, Java Platform API Specification, version 1.8, package org.wildfly.common.os, wildfly-common, version 1.5, package org.jboss.as.server.deployment.reflect, WildFly: Server, version 15.0, package org.jboss.dmr.stream, JBoss Dynamic Model Representation, version 1.5, package org.jboss.as.controller.capability.registry, WildFly: Controller Core, version 15.0, package org.jboss.modules, JBoss Modules, version 1.12, package sun.reflect.generics.factory, Java Platform API Specification, version 1.8, package org.jboss.as.controller.transform, WildFly: Controller Core, version 15.0, package org.jboss.as.server.deploymentoverlay, WildFly: Server, version 15.0, package org.wildfly.security.password.interfaces, WildFly Elytron - Credential, version 1.15, package org.wildfly.common.iteration, wildfly-common, version 1.5, package com.sun.jmx.remote.util, Java Platform API Specification, version 1.8, package java.lang.invoke, Java Platform API Specification, version 1.8, package com.redhat.insights.jars, package org.jboss.as.server.deployment.transformation, WildFly: Server, version 15.0, package sun.util.locale, Java Platform API Specification, version 1.8, package org.jboss.eap.insights.report.logging, JBoss EAP Insights Integration, version 7.4, package org.jboss.as.controller.operations, WildFly: Controller Core, version 15.0, package java.nio.file, Java Platform API Specification, version 1.8, package sun.net.util, Java Platform API Specification, version 1.8, package sun.reflect.generics.scope, Java Platform API Specification, version 1.8, package sun.net, Java Platform API Specification, version 1.8, package sun.text.resources, Java Platform API Specification, version 1.8, package sun.util.spi, Java Platform API Specification, version 1.8, package sun.management, Java Platform API Specification, version 1.8, package org.jboss.as.server.deployment.annotation, WildFly: Server, version 15.0, package org.wildfly.security.auth.realm.jdbc, WildFly Elytron - Realm JDBC, version 1.15, package org.wildfly.security.sasl.scram, WildFly Elytron - SASL SCRAM, version 1.15, package java.nio.file.spi, Java Platform API Specification, version 1.8, package java.security, Java Platform API Specification, version 1.8, package org.wildfly.security.auth.client, WildFly Elytron - Client, version 1.15, package org.wildfly.security.auth.realm.ldap, WildFly Elytron - Realm LDAP, version 1.15, package org.wildfly.security.http.form, WildFly Elytron - HTTP Basic, version 1.15, package org.jboss.as.controller.client, WildFly: Controller Client, version 15.0, package org.jboss.as.server.moduleservice, WildFly: Server, version 15.0, package org.jboss.as.controller.access.constraint, WildFly: Controller Core, version 15.0, package org.jboss.msc, JBoss Modular Service Container, version 1.4, package java.lang, Java Platform API Specification, version 1.8, package org.wildfly.security.sasl.external, WildFly Elytron - SASL External, version 1.15, package org.jboss.as.server, WildFly: Server, version 15.0, package java.util.concurrent.atomic, Java Platform API Specification, version 1.8, package org.jboss.as.server.services.security, WildFly: Server, version 15.0, package org.jboss.as.controller._private, WildFly: Controller Core, version 15.0, package org.wildfly.security.ssl, WildFly Elytron - SSL, version 1.15, package org.wildfly.common.ref, wildfly-common, version 1.5, package java.util.spi, Java Platform API Specification, version 1.8, package java.security.spec, Java Platform API Specification, version 1.8, package com.fasterxml.jackson.databind, jackson-databind, version 2.12.7.redhat-00003, package org.jboss.as.controller.operations.validation, WildFly: Controller Core, version 15.0, package org.jboss.as.server.mgmt.domain, WildFly: Server, version 15.0, package org.jboss.as.controller.audit, WildFly: Controller Core, version 15.0, package org.wildfly.security.cache, WildFly Elytron - Auth Server, version 1.15, package org.wildfly.security.sasl.gs2, WildFly Elytron - SASL GS2, version 1.15, package javax.security.auth.x500, Java Platform API Specification, version 1.8, package java.lang.reflect, Java Platform API Specification, version 1.8, package org.jboss.as.controller.logging, WildFly: Controller Core, version 15.0, package sun.nio, Java Platform API Specification, version 1.8, package org.wildfly.security.http.external, WildFly Elytron - HTTP External, version 1.15, package org.wildfly.security.asn1, WildFly Elytron - ASN.1, version 1.15, package org.wildfly.security.auth.permission, WildFly Elytron - Auth Server, version 1.15, package org.jboss.as.controller.services.path, WildFly: Controller Core, version 15.0, package java.nio.channels, Java Platform API Specification, version 1.8, package org.jboss.as.controller.security, WildFly: Controller Core, version 15.0, package org.wildfly.security.sasl.entity, WildFly Elytron - SASL Entity, version 1.15, package org.jboss.as.server.deployment.jbossallxml, WildFly: Server, version 15.0, package sun.reflect.annotation, Java Platform API Specification, version 1.8, package jdk.internal.util, Java Platform API Specification, version 1.8, package javax.security.auth, Java Platform API Specification, version 1.8, package java.time.zone, Java Platform API Specification, version 1.8, package sun.reflect.generics.parser, Java Platform API Specification, version 1.8, package org.jboss.as.controller.access.permission, WildFly: Controller Core, version 15.0, package org.jboss.msc.service, JBoss Modular Service Container, version 1.4, package org.jboss.as.controller.notification, WildFly: Controller Core, version 15.0, package org.wildfly.security.key, WildFly Elytron - Credential, version 1.15, package com.fasterxml.jackson.core, Jackson-core, version 2.12.7.redhat-00003, package org.wildfly.security.manager.action, WildFly Elytron - Security Manager Action, version 1.15, package org.wildfly.security.sasl.gssapi, WildFly Elytron - SASL GSSAPI, version 1.15, package org.wildfly.security.sasl.digest, WildFly Elytron - SASL Digest, version 1.15, package sun.security.x509, Java Platform API Specification, version 1.8, package org.jboss.as.controller, WildFly: Controller Core, version 15.0, package org.jboss.vfs.util, JBoss VFS, version 3.2.17.Final-redhat-00001, package org.jboss.as.server.services.net, WildFly: Server, version 15.0, package sun.invoke.util, Java Platform API Specification, version 1.8, package com.redhat.insights.config, package org.jboss.as.server.deployment.integration, WildFly: Server, version 15.0, package org.wildfly.security.credential, WildFly Elytron - Credential, version 1.15, package org.jboss.msc.value, JBoss Modular Service Container, version 1.4, package org.jboss.as.controller.access.rbac, WildFly: Controller Core, version 15.0, package org.jboss.as.server.logging, WildFly: Server, version 15.0, package org.wildfly.security.http.util, WildFly Elytron - HTTP Util, version 1.15, package org.wildfly.security.auth.principal, WildFly Elytron - Auth, version 1.15, package org.jboss.vfs, JBoss VFS, version 3.2.17.Final-redhat-00001, package java.security.cert, Java Platform API Specification, version 1.8, package org.jboss.as.server.jmx, WildFly: Server, version 15.0, package org.jboss.modules.filter, JBoss Modules, version 1.12, package com.sun.jmx.mbeanserver, Java Platform API Specification, version 1.8, package sun.net.www.protocol.http, Java Platform API Specification, version 1.8, package javax.crypto, Java Platform API Specification, version 1.8, package org.wildfly.security, WildFly Elytron - Base, version 1.15, package org.jboss.as.server.deployment, WildFly: Server, version 15.0, package java.util.concurrent.locks, Java Platform API Specification, version 1.8, package javax.security.auth.login, Java Platform API Specification, version 1.8, package org.wildfly.security.auth, WildFly Elytron - Auth, version 1.15, package org.wildfly.common.function, wildfly-common, version 1.5, package sun.util.logging, Java Platform API Specification, version 1.8, package org.jboss.eap.insights.report, JBoss EAP Insights Integration, version 7.4, package org.jboss.modules.ref, JBoss Modules, version 1.12, package org.jboss.msc.service.management, JBoss Modular Service Container, version 1.4, package sun.reflect.generics.visitor, Java Platform API Specification, version 1.8, package org.wildfly.security.credential.store, WildFly Elytron - Credential Store, version 1.15, package java.nio.charset, Java Platform API Specification, version 1.8, package java.lang.annotation, Java Platform API Specification, version 1.8, package org.jboss.as.server.controller.resources, WildFly: Server, version 15.0, package org.wildfly.common.cpu, wildfly-common, version 1.5, package java.beans, Java Platform API Specification, version 1.8, package java.io, Java Platform API Specification, version 1.8, package org.wildfly.common.net, wildfly-common, version 1.5, package org.jboss.as.server.parsing, WildFly: Server, version 15.0, package java.time.temporal, Java Platform API Specification, version 1.8, package sun.reflect.generics.tree, Java Platform API Specification, version 1.8, package org.wildfly.common, wildfly-common, version 1.5, package org.jboss.as.server.mgmt, WildFly: Server, version 15.0, package sun.reflect.misc, Java Platform API Specification, version 1.8, package com.fasterxml.jackson.datatype.jsr310, Jackson datatype: JSR310, version 2.12.7.redhat-00003, package javax.security.auth.callback, Java Platform API Specification, version 1.8, package java.text, Java Platform API Specification, version 1.8, package sun.security.action, Java Platform API Specification, version 1.8, package org.wildfly.security.x500.cert, WildFly Elytron - X.500 Certificates, version 1.15, package org.jboss.as.server.deployment.module, WildFly: Server, version 15.0, package org.jboss.modules.management, JBoss Modules, version 1.12, package java.security.interfaces, Java Platform API Specification, version 1.8, package com.sun.net.ssl.internal.ssl, Java Platform API Specification, version 1.8, package org.wildfly.security.credential.source, WildFly Elytron - Auth Server, version 1.15, package sun.reflect.generics.reflectiveObjects, Java Platform API Specification, version 1.8]",
        "system.os.version": "4.18.0-425.13.1.el8_7.x86_64",
        "jvm.args": [
            "-D[Standalone]",
            "-verbose:gc",
            "-Xloggc:/opt/t_eap/jboss-eap-7.4/standalone/log/gc.log",
            "-XX:+PrintGCDetails",
            "-XX:+PrintGCDateStamps",
            "-XX:+UseGCLogFileRotation",
            "-XX:NumberOfGCLogFiles=5",
            "-XX:GCLogFileSize=3M",
            "-XX:-TraceClassUnloading",
            "-Xms1303m",
            "-Xmx1303m",
            "-XX:MetaspaceSize=96M",
            "-XX:MaxMetaspaceSize=256m",
            "-Djava.net.preferIPv4Stack=true",
            "-Djboss.modules.system.pkgs=org.jboss.byteman",
            "-Djava.awt.headless=true",
            "-Dorg.jboss.boot.log.file=/opt/t_eap/jboss-eap-7.4/standalone/log/server.log",
            "-Dlogging.configuration=file:/opt/t_eap/jboss-eap-7.4/standalone/configuration/logging.properties"
        ],
        "java.vm.name": "OpenJDK 64-Bit Server VM",
        "java.vm.specification.version": "1.8",
        "jvm.heap.min": 1304,
        "app.name": "Red Hat JBoss EAP 254d541c-a9ab-4df4-8bb7-2bc84447beb7",
        "app.transport.cert.https": "/etc/pki/consumer/cert.pem",
        "system.hostname": "kafka",
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
        "eap-version": "JBoss EAP 7.4.11.GA (WildFly Core 15.0.26.Final-redhat-00001)",
        "eap-installation": {
            "version": "1.0.0",
            "eap-xp": false,
            "yaml-extension": false,
            "bootable-jar": false,
            "use-git": false
        },
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
                    "name": "aesh-2.4.0.redhat-00001.jar",
                    "version": "2.4.0.redhat-00001",
                    "attributes": {
                        "sha1Checksum": "59eba93e98cbed16ffeb8ea3bc1150892a67de3c",
                        "overridden": "unknown",
                        "version": "2.4.0.redhat-00001"
                    }
                },
                {
                    "name": "aesh-extensions-1.8.0.redhat-00001.jar",
                    "version": "1.8.0.redhat-00001",
                    "attributes": {
                        "sha1Checksum": "6b7f6d00606056eb910c5802cea00a82f1d5a501",
                        "Implementation-Vendor": "JBoss by Red Hat",
                         "overridden": "unknown",
                        "version": "1.8.0.redhat-00001"
                    }
                },
                {
                    "name": "agroal-api-1.3.0.redhat-00001.jar",
                    "version": "1.3.0.redhat-00001",
                    "attributes": {
                        "sha1Checksum": "c4dd14dc46993779d38813dd6cbe8d874e916810",
                        "Implementation-Vendor": "JBoss by Red Hat",
                        "path": "system/layers/base/io/agroal/main/agroal-api-1.3.0.redhat-00001.jar",
                        "groupId": "io.agroal",
                        "sha256Checksum": "aff6ebcb7779137bce087d3a6687400a23f4c21328f1452083bac71a65596a96",
                        "artifactId": "agroal-api",
                        "sha512Checksum": "1d344d3799294d81892050f63908adc158651656033dfeaae80249e2e05dd1418eff5d20162b899580eea89e5e258ce84a354c6ea2a937ff4ae91581932c6816",
                        "Implementation-Vendor-Id": "io.agroal",
                        "overridden": "unknown",
                        "version": "1.3.0.redhat-00001"
                    }
                },
                {
                    "name": "artemis-jms-server-2.16.0.redhat-00047.jar",
                    "version": "2.16.0.redhat-00047",
                    "attributes": {
                        "sha1Checksum": "41231a9d24e63fed8967fdc611c20ba97d39a68b",
                        "version": "2.16.0.redhat-00047"
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
                                "context-root": "/helloworld",
                                "expired-sessions": 0,
                                "highest-session-count": 0,
                                "max-active-sessions": -1,
                                "rejected-sessions": 0,
                                "server": "default-server",
                                "session-avg-alive-time": 0,
                                "session-max-alive-time": 0,
                                "sessions-created": 0,
                                "virtual-host": "default-host",
                                "servlet": null,
                                "websocket": null
                            },
                            "logging": {
                                "configuration": {
                                    "default": {
                                        "error-manager": null,
                                        "filter": null,
                                        "formatter": {
                                            "PATTERN": {
                                                "class-name": "org.jboss.logmanager.formatters.PatternFormatter",
                                                "module": null,
                                                "properties": {
                                                    "pattern": "%d{yyyy-MM-dd HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n"
                                                }
                                            },
                                            "COLOR-PATTERN": {
                                                "class-name": "org.jboss.logmanager.formatters.PatternFormatter",
                                                "module": null,
                                                "properties": {
                                                    "pattern": "%K{level}%d{HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n"
                                                }
                                            }
                                        },
                                        "handler": {
                                            "CONSOLE": {
                                                "class-name": "org.jboss.logmanager.handlers.ConsoleHandler",
                                                "encoding": null,
                                                "error-manager": null,
                                                "filter": null,
                                                "formatter": "COLOR-PATTERN",
                                                "handlers": [],
                                                "level": "INFO",
                                                "module": null,
                                                "properties": {
                                                    "autoFlush": "true",
                                                    "target": "SYSTEM_OUT"
                                                }
                                            },
                                            "FILE": {
                                                "class-name": "org.jboss.logmanager.handlers.PeriodicRotatingFileHandler",
                                                "encoding": null,
                                                "error-manager": null,
                                                "filter": null,
                                                "formatter": "PATTERN",
                                                "handlers": [],
                                                "level": "ALL",
                                                "module": null,
                                                "properties": {
                                                    "autoFlush": "true",
                                                    "append": "true",
                                                    "fileName": "/opt/t_eap/jboss-eap-7.4/standalone/log/server.log",
                                                    "suffix": ".yyyy-MM-dd"
                                                }
                                            }
                                        },
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
                                            "sun.rmi": {
                                                "filter": null,
                                                "handlers": [],
                                                "level": "WARN",
                                                "use-parent-handlers": true
                                            },
                                            "io.jaegertracing.Configuration": {
                                                "filter": null,
                                                "handlers": [],
                                                "level": "WARN",
                                                "use-parent-handlers": true
                                            },
                                            "org.jboss.as.config": {
                                                "filter": null,
                                                "handlers": [],
                                                "level": "DEBUG",
                                                "use-parent-handlers": true
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
                    "org.jboss.as.connector": {
                        "module": "org.jboss.as.connector",
                        "subsystem": {
                            "jca": {
                                "management-major-version": 5,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            },
                            "datasources": {
                                "management-major-version": 6,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            },
                            "resource-adapters": {
                                "management-major-version": 6,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.deployment-scanner": {
                        "module": "org.jboss.as.deployment-scanner",
                        "subsystem": {
                            "deployment-scanner": {
                                "management-major-version": 2,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.ee": {
                        "module": "org.jboss.as.ee",
                        "subsystem": {
                            "ee": {
                                "management-major-version": 6,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.ejb3": {
                        "module": "org.jboss.as.ejb3",
                        "subsystem": {
                            "ejb3": {
                                "management-major-version": 9,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.jaxrs": {
                        "module": "org.jboss.as.jaxrs",
                        "subsystem": {
                            "jaxrs": {
                                "management-major-version": 3,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.jdr": {
                        "module": "org.jboss.as.jdr",
                        "subsystem": {
                            "jdr": {
                                "management-major-version": 2,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.jmx": {
                        "module": "org.jboss.as.jmx",
                        "subsystem": {
                            "jmx": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 2
                            }
                        }
                    },
                    "org.jboss.as.jpa": {
                        "module": "org.jboss.as.jpa",
                        "subsystem": {
                            "jpa": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 2
                            }
                        }
                    },
                    "org.jboss.as.jsf": {
                        "module": "org.jboss.as.jsf",
                        "subsystem": {
                            "jsf": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 1
                            }
                        }
                    },
                    "org.jboss.as.logging": {
                        "module": "org.jboss.as.logging",
                        "subsystem": {
                            "logging": {
                                "management-major-version": 9,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.mail": {
                        "module": "org.jboss.as.mail",
                        "subsystem": {
                            "mail": {
                                "management-major-version": 4,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.naming": {
                        "module": "org.jboss.as.naming",
                        "subsystem": {
                            "naming": {
                                "management-major-version": 2,
                                "management-micro-version": 0,
                                "management-minor-version": 1
                            }
                        }
                    },
                    "org.jboss.as.pojo": {
                        "module": "org.jboss.as.pojo",
                        "subsystem": {
                            "pojo": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.remoting": {
                        "module": "org.jboss.as.remoting",
                        "subsystem": {
                            "remoting": {
                                "management-major-version": 5,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.sar": {
                        "module": "org.jboss.as.sar",
                        "subsystem": {
                            "sar": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.security": {
                        "module": "org.jboss.as.security",
                        "subsystem": {
                            "security": {
                                "management-major-version": 2,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.transactions": {
                        "module": "org.jboss.as.transactions",
                        "subsystem": {
                            "transactions": {
                                "management-major-version": 6,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.webservices": {
                        "module": "org.jboss.as.webservices",
                        "subsystem": {
                            "webservices": {
                                "management-major-version": 3,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.jboss.as.weld": {
                        "module": "org.jboss.as.weld",
                        "subsystem": {
                            "weld": {
                                "management-major-version": 4,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.batch.jberet": {
                        "module": "org.wildfly.extension.batch.jberet",
                        "subsystem": {
                            "batch-jberet": {
                                "management-major-version": 2,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.bean-validation": {
                        "module": "org.wildfly.extension.bean-validation",
                        "subsystem": {
                            "bean-validation": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.clustering.web": {
                        "module": "org.wildfly.extension.clustering.web",
                        "subsystem": {
                            "distributable-web": {
                                "management-major-version": 2,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.core-management": {
                        "module": "org.wildfly.extension.core-management",
                        "subsystem": {
                            "core-management": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.discovery": {
                        "module": "org.wildfly.extension.discovery",
                        "subsystem": {
                            "discovery": {
                                "management-major-version": 2,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.ee-security": {
                        "module": "org.wildfly.extension.ee-security",
                        "subsystem": {
                            "ee-security": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.elytron": {
                        "module": "org.wildfly.extension.elytron",
                        "subsystem": {
                            "elytron": {
                                "management-major-version": 13,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.health": {
                        "module": "org.wildfly.extension.health",
                        "subsystem": {
                            "health": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.io": {
                        "module": "org.wildfly.extension.io",
                        "subsystem": {
                            "io": {
                                "management-major-version": 5,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.metrics": {
                        "module": "org.wildfly.extension.metrics",
                        "subsystem": {
                            "metrics": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 0
                            }
                        }
                    },
                    "org.wildfly.extension.request-controller": {
                        "module": "org.wildfly.extension.request-controller",
                        "subsystem": {
                            "request-controller": {
                                "management-major-version": 1,
                                "management-micro-version": 0,
                                "management-minor-version": 1
                            }
                        }
                    },
                    "org.wildfly.extension.security.manager": {
                        "module": "org.wildfly.extension.security.manager",
                        "subsystem": {
                            "security-manager": {
                                "management-major-version": 3,
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
                            "txn-recovery-environment": {
                                "bound": false,
                                "bound-address": null,
                                "bound-port": null,
                                "client-mappings": null,
                                "fixed-port": false,
                                "interface": null,
                                "multicast-address": null,
                                "multicast-port": null,
                                "name": "txn-recovery-environment",
                                "port": 4712
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
                    "logging": {
                        "add-logging-api-dependencies": true,
                        "use-deployment-logging-config": true,
                        "async-handler": null,
                        "console-handler": {
                            "CONSOLE": {
                                "autoflush": true,
                                "enabled": true,
                                "encoding": null,
                                "filter": null,
                                "filter-spec": null,
                                "formatter": "%d{HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n",
                                "level": "INFO",
                                "name": "CONSOLE",
                                "named-formatter": "COLOR-PATTERN",
                                "target": "System.out"
                            }
                        },
                        "custom-formatter": null,
                        "custom-handler": null,
                        "file-handler": null,
                        "filter": null,
                        "json-formatter": null,
                        "log-file": {
                            "server.log": {
                                "file-size": 30293,
                                "last-modified-time": 1686660039187,
                                "last-modified-timestamp": "2023-06-13T12:40:39.187+0000",
                                "stream": "0633e009-8065-4a6b-a2c1-e6d5a5318cd3"
                            }
                        },
                        "logger": {
                            "com.arjuna": {
                                "category": "com.arjuna",
                                "filter": null,
                                "filter-spec": null,
                                "handlers": null,
                                "level": "WARN",
                                "use-parent-handlers": true
                            },
                            "sun.rmi": {
                                "category": "sun.rmi",
                                "filter": null,
                                "filter-spec": null,
                                "handlers": null,
                                "level": "WARN",
                                "use-parent-handlers": true
                            }
                        },
                        "logging-profile": null,
                        "pattern-formatter": {
                            "PATTERN": {
                                "color-map": null,
                                "pattern": "%d{yyyy-MM-dd HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n"
                            },
                            "COLOR-PATTERN": {
                                "color-map": null,
                                "pattern": "%K{level}%d{HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n"
                            }
                        },
                        "periodic-rotating-file-handler": {
                            "FILE": {
                                "append": true,
                                "autoflush": true,
                                "enabled": true,
                                "encoding": null,
                                "file": {
                                    "relative-to": "jboss.server.log.dir",
                                    "path": "server.log"
                                },
                                "filter": null,
                                "filter-spec": null,
                                "formatter": "%d{HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n",
                                "level": "ALL",
                                "name": "FILE",
                                "named-formatter": "PATTERN",
                                "suffix": ".yyyy-MM-dd"
                            }
                        },
                        "periodic-size-rotating-file-handler": null,
                        "root-logger": {
                            "ROOT": {
                                "filter": null,
                                "filter-spec": null,
                                "handlers": [
                                    "CONSOLE",
                                    "FILE"
                                ],
                                "level": "INFO"
                            }
                        },
                        "size-rotating-file-handler": null,
                        "socket-handler": null,
                        "syslog-handler": null,
                        "xml-formatter": null
                    },
                    "batch-jberet": {
                        "restart-jobs-on-resume": true,
                        "security-domain": null,
                        "default-job-repository": "in-memory",
                        "default-thread-pool": "batch",
                        "in-memory-job-repository": {
                            "in-memory": {}
                        },
                        "jdbc-job-repository": null,
                        "thread-factory": null,
                        "thread-pool": {
                            "batch": {
                                "active-count": 0,
                                "completed-task-count": 0,
                                "current-thread-count": 0,
                                "keepalive-time": {
                                    "time": 30,
                                    "unit": "SECONDS"
                                },
                                "largest-thread-count": 0,
                                "max-threads": 10,
                                "name": "batch",
                                "queue-size": 0,
                                "rejected-count": 0,
                                "task-count": 0,
                                "thread-factory": null
                            }
                        }
                    },
                    "bean-validation": {},
                    "core-management": {
                        "process-state-listener": null,
                        "service": null
                    },
                    "datasources": {
                        "installed-drivers": [
                            {
                                "driver-name": "h2",
                                "deployment-name": null,
                                "driver-module-name": "com.h2database.h2",
                                "module-slot": "main",
                                "driver-datasource-class-name": "",
                                "driver-xa-datasource-class-name": "org.h2.jdbcx.JdbcDataSource",
                                "datasource-class-info": [
                                    {
                                        "org.h2.jdbcx.JdbcDataSource": {
                                            "URL": "java.lang.String",
                                            "description": "java.lang.String",
                                            "loginTimeout": "int",
                                            "password": "java.lang.String",
                                            "url": "java.lang.String",
                                            "user": "java.lang.String"
                                        }
                                    }
                                ],
                                "driver-class-name": "org.h2.Driver",
                                "driver-major-version": 1,
                                "driver-minor-version": 4,
                                "jdbc-compliant": true
                            }
                        ],
                        "data-source": {
                            "ExampleDS": {
                                "allocation-retry": null,
                                "spy": false,
                                "stale-connection-checker-class-name": null,
                                "stale-connection-checker-properties": null,
                                "statistics-enabled": {
                                    "EXPRESSION_VALUE": "${wildfly.datasources.statistics-enabled:${wildfly.statistics-enabled:false}}"
                                },
                                "track-statements": "NOWARN",
                                "connection-properties": null,
                                "statistics": {
                                    "jdbc": {
                                        "PreparedStatementCacheAccessCount": 0,
                                        "PreparedStatementCacheAddCount": 0,
                                        "PreparedStatementCacheCurrentSize": 0,
                                        "PreparedStatementCacheDeleteCount": 0,
                                        "PreparedStatementCacheHitCount": 0,
                                        "PreparedStatementCacheMissCount": 0,
                                        "statistics-enabled": false
                                    },
                                    "pool": {
                                        "ActiveCount": 0,
                                        "XARollbackMaxTime": 0,
                                        "XARollbackTotalTime": 0,
                                        "XAStartAverageTime": 0,
                                        "XAStartCount": 0,
                                        "XAStartMaxTime": 0,
                                        "XAStartTotalTime": 0,
                                        "statistics-enabled": false
                                    }
                                }
                            }
                        },
                        "jdbc-driver": {
                            "h2": {
                                "datasource-class-info": [
                                    {
                                        "org.h2.jdbcx.JdbcDataSource": {
                                            "URL": "java.lang.String",
                                            "description": "java.lang.String",
                                            "loginTimeout": "int",
                                            "password": "java.lang.String",
                                            "url": "java.lang.String",
                                            "user": "java.lang.String"
                                        }
                                    }
                                ],
                                "deployment-name": null,
                                "xa-datasource-class": null
                            }
                        },
                        "xa-data-source": null
                    },
                    "deployment-scanner": {
                        "scanner": {
                            "default": {
                                "auto-deploy-exploded": false,
                                "auto-deploy-xml": true,
                                "auto-deploy-zipped": true,
                                "deployment-timeout": 600,
                                "path": "deployments",
                                "relative-to": "jboss.server.base.dir",
                                "runtime-failure-causes-rollback": {
                                    "EXPRESSION_VALUE": "${jboss.deployment.scanner.rollback.on.failure:false}"
                                },
                                "scan-enabled": true,
                                "scan-interval": 5000
                            }
                        }
                    },
                    "discovery": {
                        "aggregate-provider": null,
                        "static-provider": null
                    },
                    "distributable-web": {
                        "default-session-management": "default",
                        "default-single-sign-on-management": "default",
                        "hotrod-session-management": null,
                        "hotrod-single-sign-on-management": null,
                        "infinispan-session-management": {
                            "default": {
                                "cache": null,
                                "cache-container": "web",
                                "granularity": "SESSION",
                                "affinity": {
                                    "local": {}
                                }
                            }
                        },
                        "infinispan-single-sign-on-management": {
                            "default": {
                                "cache": "sso",
                                "cache-container": "web"
                            }
                        },
                        "routing": {
                            "local": {}
                        }
                    },
                    "ee": {
                        "annotation-property-replacement": false,
                        "ear-subdeployments-isolated": false,
                        "global-modules": null,
                        "jboss-descriptor-property-replacement": true,
                        "spec-descriptor-property-replacement": false,
                        "context-service": {
                            "default": {
                                "jndi-name": "java:jboss/ee/concurrency/context/default",
                                "use-transaction-setup-provider": true
                            }
                        },
                        "global-directory": null,
                        "managed-executor-service": {
                            "default": {
                                "active-thread-count": 0,
                                "thread-factory": null,
                                "thread-priority": 5
                            }
                        },
                        "managed-scheduled-executor-service": {
                            "default": {
                                "active-thread-count": 0,
                                "thread-factory": null,
                                "thread-priority": 5
                            }
                        },
                        "managed-thread-factory": {
                            "default": {
                                "context-service": "default",
                                "jndi-name": "java:jboss/ee/concurrency/factory/default",
                                "priority": 5
                            }
                        },
                        "service": {
                            "default-bindings": {
                                "context-service": "java:jboss/ee/concurrency/context/default",
                                "datasource": "java:jboss/datasources/ExampleDS",
                                "jms-connection-factory": null,
                                "managed-executor-service": "java:jboss/ee/concurrency/executor/default",
                                "managed-scheduled-executor-service": "java:jboss/ee/concurrency/scheduler/default",
                                "managed-thread-factory": "java:jboss/ee/concurrency/factory/default"
                            }
                        }
                    },
                    "ee-security": {},
                    "ejb3": {
                        "allow-ejb-name-regex": false,
                        "client-interceptors": null,
                        "server-interceptors": null,
                        "statistics-enabled": {
                            "EXPRESSION_VALUE": "${wildfly.ejb3.statistics-enabled:${wildfly.statistics-enabled:false}}"
                        },
                        "application-security-domain": null,
                        "cache": {
                            "simple": {
                                "aliases": null,
                                "passivation-store": null
                            },
                            "distributable": {
                                "aliases": [
                                    "passivating",
                                    "clustered"
                                ],
                                "passivation-store": "infinispan"
                            }
                        },
                        "cluster-passivation-store": null,
                        "file-passivation-store": null,
                        "mdb-delivery-group": null,
                        "passivation-store": {
                            "infinispan": {
                                "bean-cache": null,
                                "cache-container": "ejb",
                                "max-size": 10000
                            }
                        },
                        "remoting-profile": null,
                        "service": {
                            "async": {
                                "thread-pool-name": "default"
                            },
                            "timer-service": {
                                "default-data-store": "default-file-store",
                                "thread-pool-name": "default",
                                "database-data-store": null,
                                "file-data-store": {
                                    "default-file-store": {
                                        "path": "timer-service-data",
                                        "relative-to": "jboss.server.data.dir"
                                    }
                                }
                            },
                            "remote": {
                                "cluster": "ejb",
                                "connector-ref": "http-remoting-connector",
                                "connectors": [
                                    "http-remoting-connector"
                                ],
                                "execute-in-worker": true,
                                "thread-pool-name": "default",
                                "channel-creation-options": {
                                    "MAX_OUTBOUND_MESSAGES": {
                                        "type": "remoting",
                                        "value": "1234"
                                    }
                                }
                            }
                        },
                        "strict-max-bean-instance-pool": {
                            "mdb-strict-max-pool": {
                                "derive-size": "from-cpu-count",
                                "derived-size": 8,
                                "max-pool-size": 20,
                                "timeout": 5,
                                "timeout-unit": "MINUTES"
                            },
                            "slsb-strict-max-pool": {
                                "derive-size": "from-worker-pools",
                                "derived-size": 32,
                                "max-pool-size": 20,
                                "timeout": 5,
                                "timeout-unit": "MINUTES"
                            }
                        },
                        "thread-pool": {
                            "default": {
                                "active-count": 0,
                                "completed-task-count": 0,
                                "core-threads": null,
                                "current-thread-count": 0,
                                "keepalive-time": {
                                    "time": 60,
                                    "unit": "SECONDS"
                                },
                                "largest-thread-count": 0,
                                "max-threads": 10,
                                "name": "default",
                                "queue-size": 0,
                                "rejected-count": 0,
                                "task-count": 0,
                                "thread-factory": null
                            }
                        }
                    },
                    "health": {
                        "security-enabled": false
                    },
                    "infinispan": {
                        "cache-container": {
                            "ejb": {
                                "aliases": [
                                    "sfsb"
                                ],
                                "cache-manager-status": "RUNNING",
                                "cluster-name": "ISPN",
                                "coordinator-address": "<local>",
                                "default-cache": "passivation",
                                "eviction-executor": null,
                                "is-coordinator": false,
                                "jndi-name": null,
                                "listener-executor": null,
                                "local-address": "<local>",
                                "modules": [
                                    "org.wildfly.clustering.ejb.infinispan"
                                ],
                                "replication-queue-executor": null,
                                "start": "LAZY",
                                "statistics-enabled": false,
                                "cache": {
                                    "http-remoting-connector": {
                                        "activations": 0,
                                        "average-read-time": null,
                                        "time-since-start": null,
                                        "writes": null,
                                        "component": {
                                            "locking": {
                                                "current-concurrency-level": null,
                                                "number-of-locks-available": null,
                                                "number-of-locks-held": null
                                            },
                                            "persistence": {
                                                "cache-loader-loads": null,
                                                "cache-loader-misses": null
                                            },
                                            "transaction": {
                                                "commits": null,
                                                "prepares": null,
                                                "rollbacks": null
                                            },
                                            "partition-handling": {
                                                "availability": "AVAILABLE"
                                            }
                                        }
                                    }
                                },
                                "distributed-cache": null,
                                "invalidation-cache": null,
                                "local-cache": {
                                    "passivation": {
                                        "activations": null,
                                        "average-read-time": null,
                                        "start": "LAZY",
                                        "statistics-enabled": false,
                                        "stores": null,
                                        "time-since-reset": null,
                                        "component": {
                                            "expiration": {
                                                "interval": 60000,
                                                "lifespan": null,
                                                "max-idle": null
                                            },
                                            "locking": {
                                                "acquire-timeout": 15000,
                                                "concurrency-level": 1000,
                                                "current-concurrency-level": null,
                                                "isolation": "READ_COMMITTED",
                                                "number-of-locks-available": null,
                                                "number-of-locks-held": null,
                                                "striping": false
                                            },
                                            "transaction": {
                                                "commits": null,
                                                "locking": "PESSIMISTIC",
                                                "mode": "NONE",
                                                "prepares": null,
                                                "rollbacks": null,
                                                "stop-timeout": 10000
                                            }
                                        },
                                        "memory": {
                                            "heap": {
                                                "evictions": null,
                                                "max-entries": null,
                                                "size": null,
                                                "size-unit": "ENTRIES",
                                                "strategy": "NONE"
                                            }
                                        },
                                        "store": {
                                            "file": {
                                                "cache-loader-loads": null,
                                                "cache-loader-misses": null,
                                                "fetch-state": true,
                                                "property": null,
                                                "write": {
                                                    "through": {}
                                                }
                                            }
                                        }
                                    }
                                },
                                "replicated-cache": null,
                                "scattered-cache": null,
                                "thread-pool": {
                                    "async-operations": {
                                        "keepalive-time": 60000,
                                        "max-threads": 25,
                                        "min-threads": 25,
                                        "queue-length": 1000
                                    },
                                    "transport": {
                                        "keepalive-time": 60000,
                                        "max-threads": 10,
                                        "min-threads": 10,
                                        "queue-length": 1000
                                    }
                                },
                                "transport": {
                                    "none": {}
                                }
                            },
                            "web": {
                                "aliases": null,
                                "cache-manager-status": null,
                                "cluster-name": null,
                                "coordinator-address": null,
                                "default-cache": "passivation",
                                "eviction-executor": null,
                                "is-coordinator": null,
                                "jndi-name": null,
                                "listener-executor": null,
                                "local-address": null,
                                "modules": [
                                    "org.wildfly.clustering.web.infinispan"
                                ],
                                "replication-queue-executor": null,
                                "start": "LAZY",
                                "statistics-enabled": false,
                                "cache": null,
                                "distributed-cache": null,
                                "invalidation-cache": null,
                                "local-cache": {
                                    "passivation": {
                                        "activations": null,
                                        "average-read-time": null,
                                        "average-write-time": null,
                                        "batching": false,
                                        "cache-status": "RUNNING",
                                        "elapsed-time": null,
                                        "hit-ratio": null,
                                        "hits": null,
                                        "indexing": "NONE",
                                        "indexing-properties": null,
                                        "invalidations": null,
                                        "jndi-name": null,
                                        "misses": null,
                                        "module": null,
                                        "modules": null,
                                        "number-of-entries": null,
                                        "passivations": null,
                                        "read-write-ratio": null,
                                        "remove-hits": null,
                                        "remove-misses": null,
                                        "start": "LAZY",
                                        "statistics-enabled": false,
                                        "stores": null,
                                        "time-since-reset": null,
                                        "component": {
                                            "expiration": {
                                                "interval": 60000,
                                                "lifespan": null,
                                                "max-idle": null
                                            },
                                            "locking": {
                                                "acquire-timeout": 15000,
                                                "concurrency-level": 1000,
                                                "current-concurrency-level": null,
                                                "isolation": "READ_COMMITTED",
                                                "number-of-locks-available": null,
                                                "number-of-locks-held": null,
                                                "striping": false
                                            },
                                            "transaction": {
                                                "commits": null,
                                                "locking": "PESSIMISTIC",
                                                "mode": "NONE",
                                                "prepares": null,
                                                "rollbacks": null,
                                                "stop-timeout": 10000
                                            }
                                        },
                                        "memory": {
                                            "heap": {
                                                "evictions": null,
                                                "max-entries": null,
                                                "size": null,
                                                "size-unit": "ENTRIES",
                                                "strategy": "NONE"
                                            }
                                        },
                                        "store": {
                                            "file": {
                                                "cache-loader-loads": null,
                                                "cache-loader-misses": null,
                                                "write": {
                                                    "through": {}
                                                }
                                            }
                                        }
                                    },
                                    "sso": {
                                        "activations": null,
                                        "remove-misses": null,
                                        "start": "LAZY",
                                        "statistics-enabled": false,
                                        "stores": null,
                                        "time-since-reset": null,
                                        "component": {
                                            "expiration": {
                                                "interval": 60000,
                                                "lifespan": null,
                                                "max-idle": null
                                            },
                                            "locking": {
                                                "acquire-timeout": 15000,
                                                "concurrency-level": 1000,
                                                "current-concurrency-level": null,
                                                "isolation": "READ_COMMITTED",
                                                "number-of-locks-available": null,
                                                "number-of-locks-held": null,
                                                "striping": false
                                            },
                                            "transaction": {
                                                "commits": null,
                                                "locking": "PESSIMISTIC",
                                                "mode": "NONE",
                                                "prepares": null,
                                                "rollbacks": null,
                                                "stop-timeout": 10000
                                            }
                                        },
                                        "memory": {
                                            "heap": {
                                                "evictions": null,
                                                "max-entries": null,
                                                "size": null,
                                                "size-unit": "ENTRIES",
                                                "strategy": "NONE"
                                            }
                                        },
                                        "store": {
                                            "none": {}
                                        }
                                    }
                                },
                                "replicated-cache": null,
                                "scattered-cache": null,
                                "thread-pool": {
                                    "async-operations": {
                                        "keepalive-time": 60000,
                                        "max-threads": 25,
                                        "min-threads": 25,
                                        "queue-length": 1000
                                    },
                                    "transport": {
                                        "keepalive-time": 60000,
                                        "max-threads": 10,
                                        "min-threads": 10,
                                        "queue-length": 1000
                                    }
                                },
                                "transport": {
                                    "none": {}
                                }
                            },
                            "server": {
                                "aliases": null,
                                "local-address": null,
                                "modules": [
                                    "org.wildfly.clustering.server"
                                ],
                                "replication-queue-executor": null,
                                "start": "LAZY",
                                "statistics-enabled": false,
                                "cache": null,
                                "distributed-cache": null,
                                "invalidation-cache": null,
                                "local-cache": {
                                    "default": {
                                        "activations": null,
                                        "statistics-enabled": false,
                                        "stores": null,
                                        "time-since-reset": null,
                                        "component": {
                                            "expiration": {
                                                "interval": 60000,
                                                "lifespan": null,
                                                "max-idle": null
                                            },
                                            "transaction": {
                                                "commits": null,
                                                "locking": "PESSIMISTIC",
                                                "mode": "NONE",
                                                "prepares": null,
                                                "rollbacks": null,
                                                "stop-timeout": 10000
                                            }
                                        },
                                        "memory": {
                                            "heap": {
                                                "evictions": null,
                                                "max-entries": null,
                                                "size": null,
                                                "size-unit": "ENTRIES",
                                                "strategy": "NONE"
                                            }
                                        },
                                        "store": {
                                            "none": {}
                                        }
                                    }
                                },
                                "replicated-cache": null,
                                "scattered-cache": null,
                                "thread-pool": {
                                    "async-operations": {
                                        "keepalive-time": 60000,
                                        "max-threads": 25,
                                        "min-threads": 25,
                                        "queue-length": 1000
                                    },
                                    "blocking": {
                                        "keepalive-time": 60000,
                                        "max-threads": 150,
                                        "min-threads": 1,
                                        "queue-length": 5000
                                    },
                                    "expiration": {
                                        "keepalive-time": 60000,
                                        "max-threads": 1,
                                        "min-threads": 1
                                    },
                                    "listener": {
                                        "keepalive-time": 60000,
                                        "max-threads": 1,
                                        "min-threads": 1,
                                        "queue-length": 1000
                                    },
                                    "transport": {
                                        "keepalive-time": 60000,
                                        "max-threads": 10,
                                        "min-threads": 10,
                                        "queue-length": 1000
                                    }
                                },
                                "transport": {
                                    "none": {}
                                }
                            },
                            "hibernate": {
                                "aliases": null,
                                "local-address": null,
                                "modules": [
                                    "org.infinispan.hibernate-cache"
                                ],
                                "replication-queue-executor": null,
                                "start": "LAZY",
                                "statistics-enabled": false,
                                "cache": null,
                                "distributed-cache": null,
                                "invalidation-cache": null,
                                "local-cache": {
                                    "entity": {
                                        "activations": null,
                                        "time-since-reset": null,
                                        "component": {
                                            "expiration": {
                                                "interval": 60000,
                                                "lifespan": null,
                                                "max-idle": 100000
                                            },
                                            "locking": {
                                                "acquire-timeout": 15000,
                                                "striping": false
                                            },
                                            "transaction": {
                                                "commits": null,
                                                "locking": "PESSIMISTIC",
                                                "mode": "NONE",
                                                "prepares": null,
                                                "rollbacks": null,
                                                "stop-timeout": 10000
                                            }
                                        },
                                        "memory": {
                                            "heap": {
                                                "evictions": null,
                                                "max-entries": 10000,
                                                "size": 10000,
                                                "size-unit": "ENTRIES",
                                                "strategy": "NONE"
                                            }
                                        },
                                        "store": {
                                            "none": {}
                                        }
                                    },
                                    "local-query": {
                                        "activations": null,
                                        "time-since-reset": null,
                                        "component": {
                                            "expiration": {
                                                "interval": 60000,
                                                "lifespan": null,
                                                "max-idle": 100000
                                            },
                                            "locking": {
                                                "acquire-timeout": 15000,
                                                "striping": false
                                            },
                                            "transaction": {
                                                "commits": null,
                                                "locking": "PESSIMISTIC",
                                                "mode": "NONE",
                                                "prepares": null,
                                                "rollbacks": null,
                                                "stop-timeout": 10000
                                            }
                                        },
                                        "memory": {
                                            "heap": {
                                                "evictions": null,
                                                "max-entries": 10000,
                                                "size": 10000,
                                                "size-unit": "ENTRIES",
                                                "strategy": "NONE"
                                            }
                                        },
                                        "store": {
                                            "none": {}
                                        }
                                    },
                                    "timestamps": {
                                        "activations": null,
                                        "time-since-reset": null,
                                        "component": {
                                            "expiration": {
                                                "interval": 60000,
                                                "lifespan": null,
                                                "max-idle": null
                                            },
                                            "locking": {
                                                "acquire-timeout": 15000,
                                                "striping": false
                                            },
                                            "transaction": {
                                                "commits": null,
                                                "locking": "PESSIMISTIC",
                                                "mode": "NONE",
                                                "prepares": null,
                                                "rollbacks": null,
                                                "stop-timeout": 10000
                                            }
                                        },
                                        "memory": {
                                            "heap": {
                                                "evictions": null,
                                                "max-entries": null,
                                                "size": null,
                                                "size-unit": "ENTRIES",
                                                "strategy": "NONE"
                                            }
                                        },
                                        "store": {
                                            "none": {}
                                        }
                                    },
                                    "pending-puts": {
                                        "activations": null,
                                        "average-read-time": null,
                                        "time-since-reset": null,
                                        "component": {
                                            "expiration": {
                                                "interval": 60000,
                                                "lifespan": null,
                                                "max-idle": 60000
                                            },
                                            "locking": {
                                                "acquire-timeout": 15000,
                                                "striping": false
                                            },
                                            "transaction": {
                                                "commits": null,
                                                "locking": "PESSIMISTIC",
                                                "mode": "NONE",
                                                "prepares": null,
                                                "rollbacks": null,
                                                "stop-timeout": 10000
                                            }
                                        },
                                        "memory": {
                                            "heap": {
                                                "evictions": null,
                                                "max-entries": null,
                                                "size": null,
                                                "size-unit": "ENTRIES",
                                                "strategy": "NONE"
                                            }
                                        },
                                        "store": {
                                            "none": {}
                                        }
                                    }
                                },
                                "replicated-cache": null,
                                "scattered-cache": null,
                                "thread-pool": {
                                    "async-operations": {
                                        "keepalive-time": 60000,
                                        "max-threads": 25,
                                        "min-threads": 25,
                                        "queue-length": 1000
                                    },
                                    "blocking": {
                                        "keepalive-time": 60000,
                                        "max-threads": 150,
                                        "min-threads": 1,
                                        "queue-length": 5000
                                    },
                                    "expiration": {
                                        "keepalive-time": 60000,
                                        "max-threads": 1,
                                        "min-threads": 1
                                    },
                                    "transport": {
                                        "keepalive-time": 60000,
                                        "max-threads": 10,
                                        "min-threads": 10,
                                        "queue-length": 1000
                                    }
                                },
                                "transport": {
                                    "none": {}
                                }
                            }
                        },
                        "remote-cache-container": null
                    },
                    "io": {
                        "buffer-pool": {
                            "default": {
                                "buffer-size": null,
                                "buffers-per-slice": null,
                                "direct-buffers": null
                            }
                        },
                        "worker": {
                            "default": {
                                "busy-task-thread-count": 0,
                                "core-pool-size": 2,
                                "outbound-bind-address": null,
                                "server": {
                                    "/127.0.0.1:8080": {
                                        "connection-count": 0,
                                        "connection-limit-high-water-mark": 2147483647,
                                        "connection-limit-low-water-mark": 2147483647
                                    },
                                    "/127.0.0.1:8443": {
                                        "connection-count": 0,
                                        "connection-limit-high-water-mark": 2147483647,
                                        "connection-limit-low-water-mark": 2147483647
                                    }
                                }
                            }
                        }
                    },
                    "jaxrs": {
                        "jaxrs-2-0-request-matching": false,
                        "resteasy-add-charset": true,
                        "resteasy-use-container-form-params": false,
                        "resteasy-wider-request-matching": false
                    },
                    "jca": {
                        "archive-validation": {
                            "archive-validation": {
                                "enabled": true,
                                "fail-on-error": true,
                                "fail-on-warn": false
                            }
                        },
                        "cached-connection-manager": {
                            "cached-connection-manager": {
                                "debug": false,
                                "error": false,
                                "ignore-unknown-connections": false,
                                "install": true
                            }
                        },
                        "distributed-workmanager": null,
                        "tracer": null,
                        "workmanager": {
                            "default": {
                                "elytron-enabled": false,
                                "name": "default",
                                "long-running-threads": {
                                    "default": {
                                        "allow-core-timeout": false,
                                        "core-threads": 50,
                                        "current-thread-count": 0,
                                        "keepalive-time": {
                                            "time": 10,
                                            "unit": "SECONDS"
                                        },
                                        "largest-thread-count": 0,
                                        "max-threads": 50,
                                        "name": "default",
                                        "queue-length": 50,
                                        "queue-size": 0,
                                        "rejected-count": 0,
                                        "thread-factory": null
                                    }
                                },
                                "short-running-threads": {
                                    "default": {
                                        "allow-core-timeout": false,
                                        "core-threads": 50,
                                        "current-thread-count": 0,
                                        "keepalive-time": {
                                            "time": 10,
                                            "unit": "SECONDS"
                                        },
                                        "largest-thread-count": 0,
                                        "max-threads": 50,
                                        "name": "default",
                                        "queue-length": 50,
                                        "queue-size": 0,
                                        "rejected-count": 0,
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
                        "configuration": null,
                        "expose-model": {
                            "resolved": {
                                "domain-name": "jboss.as",
                                "proper-property-format": true
                            },
                            "expression": {
                                "domain-name": "jboss.as.expr"
                            }
                        },
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
                    "metrics": {
                        "exposed-subsystems": [
                            "*"
                        ],
                        "prefix": {
                            "EXPRESSION_VALUE": "${wildfly.metrics.prefix:jboss}"
                        },
                        "security-enabled": false
                    },
                    "naming": {
                        "binding": null,
                        "service": {
                            "remote-naming": {}
                        }
                    },
                    "pojo": {},
                    "remoting": {
                        "worker-read-threads": null,
                        "worker": "default",
                        "configuration": {
                            "endpoint": {
                                "auth-realm": null,
                                "authentication-retries": 3,
                                "authorize-id": null,
                                "transmit-window-size": 131072,
                                "worker": "default"
                            }
                        },
                        "connector": null,
                        "http-connector": {
                            "http-remoting-connector": {
                                "authentication-provider": null,
                                "security": null
                            }
                        },
                        "local-outbound-connection": null,
                        "outbound-connection": null,
                        "remote-outbound-connection": null
                    },
                    "request-controller": {
                        "active-requests": 0,
                        "max-requests": -1,
                        "track-individual-endpoints": false
                    },
                    "resource-adapters": {
                        "resource-adapter": null
                    },
                    "sar": {},
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
                        "default-timeout": 300,
                        "enable-statistics": {
                            "EXPRESSION_VALUE": "${wildfly.transactions.statistics-enabled:${wildfly.statistics-enabled:false}}"
                        },
                        "enable-tsm-status": false,
                        "journal-store-enable-async-io": false,
                        "jts": false,
                        "maximum-timeout": 31536000,
                        "node-identifier": {
                            "EXPRESSION_VALUE": "${jboss.tx.node.id:1}"
                        },
                        "number-of-aborted-transactions": 0,
                        "socket-binding": "txn-recovery-environment",
                        "stale-transaction-time": 600,
                        "statistics-enabled": {
                            "EXPRESSION_VALUE": "${wildfly.transactions.statistics-enabled:${wildfly.statistics-enabled:false}}"
                        },
                        "status-socket-binding": "txn-status-manager",
                        "use-hornetq-store": false,
                        "use-jdbc-store": false,
                        "use-journal-store": false,
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
                        "default-server": "default-server",
                        "default-servlet-container": "default",
                        "default-virtual-host": "default-host",
                        "instance-id": {
                            "EXPRESSION_VALUE": "${jboss.node.name}"
                        },
                        "obfuscate-session-route": false,
                        "statistics-enabled": {
                            "EXPRESSION_VALUE": "${wildfly.undertow.statistics-enabled:${wildfly.statistics-enabled:false}}"
                        },
                        "application-security-domain": null,
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
                                        "filter-ref": null,
                                        "location": {
                                            "/": {
                                                "handler": "welcome-content",
                                                "filter-ref": null
                                            }
                                        },
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
                                        "allow-equals-in-cookie-value": false,
                                        "certificate-forwarding": false,
                                        "decode-url": true,
                                        "disallowed-methods": [
                                            "TRACE"
                                        ],
                                        "enable-http2": true,
                                        "enable-spdy": false,
                                        "enabled": true,
                                        "tcp-backlog": 10000,
                                        "tcp-keep-alive": null,
                                        "url-charset": "UTF-8",
                                        "verify-client": "NOT_REQUESTED",
                                        "worker": "default",
                                        "write-timeout": null
                                    }
                                }
                            }
                        },
                        "servlet-container": {
                            "default": {
                                "allow-non-standard-wrappers": false,
                                "default-buffer-cache": "default",
                                "default-cookie-version": 0,
                                "default-encoding": null,
                                "default-session-timeout": 30,
                                "directory-listing": null,
                                "disable-caching-for-secured-pages": true,
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
                        "statistics-enabled": {
                            "EXPRESSION_VALUE": "${wildfly.webservices.statistics-enabled:${wildfly.statistics-enabled:false}}"
                        },
                        "wsdl-host": {
                            "EXPRESSION_VALUE": "${jboss.bind.address:127.0.0.1}"
                        },
                        "wsdl-path-rewrite-rule": null,
                        "wsdl-port": null,
                        "wsdl-secure-port": null,
                        "wsdl-uri-scheme": null,
                        "client-config": {
                            "Standard-Client-Config": {
                                "post-handler-chain": null,
                                "pre-handler-chain": null,
                                "property": null
                            }
                        },
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
                    },
                    "weld": {
                        "development-mode": false,
                        "non-portable-mode": false,
                        "require-bean-descriptor": false,
                        "thread-pool-size": null
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
    print(result.data.keys())
    assert result.data['version'] == '1.0.0'
    assert result.data['basic']['app.user.dir'] == "/opt/t_eap/jboss-eap-7.4"


def test_doc_examples():
    env = {
        'eap_json_report': EAPJSONReports(context_wrap(EAP_JSON_DATA_1)),
    }
    failed, total = doctest.testmod(eap_json_reports, globs=env)
    assert failed == 0
