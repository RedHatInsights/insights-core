from insights.tests import context_wrap
from insights.parsers.foreman_log import SatelliteLog, ProductionLog
from insights.parsers.foreman_log import CandlepinLog, ProxyLog
from insights.parsers.foreman_log import CandlepinErrorLog
from insights.parsers.foreman_log import ForemanSSLAccessLog
from datetime import datetime


PRODUCTION_LOG = """
2015-11-13 03:30:07 [I] Completed 200 OK in 1783ms (Views: 0.2ms | ActiveRecord: 172.9ms)
2015-11-13 03:30:07 [I] Processing by Katello::Api::V2::RepositoriesController#sync_complete as JSON
2015-11-13 03:30:07 [I]   Parameters: {"call_report"=>"[FILTERED]", "event_type"=>"repo.sync.finish", "payload"=>{"importer_id"=>"yum_importer", "exception"=>nil, "repo_id"=>"1-Acme_Corp_-Red_Hat_Enterprise_Linux_Server-Red_Hat_Satellite_Tools_6_1_for_RHEL_6_Server_RPMs_i386", "traceback"=>nil, "started"=>"2015-11-13T08:30:00Z", "_ns"=>"repo_sync_results", "completed"=>"2015-11-13T08:30:06Z", "importer_type_id"=>"yum_importer", "error_message"=>nil, "summary"=>{"content"=>{"state"=>"FINISHED"}, "comps"=>{"state"=>"FINISHED"}, "distribution"=>{"state"=>"FINISHED"}, "errata"=>{"state"=>"FINISHED"}, "metadata"=>{"state"=>"FINISHED"}}, "added_count"=>0, "result"=>"success", "updated_count"=>3, "details"=>{"content"=>{"size_total"=>0, "items_left"=>0, "items_total"=>0, "state"=>"FINISHED", "size_left"=>0, "details"=>{"rpm_total"=>0, "rpm_done"=>0, "drpm_total"=>0, "drpm_done"=>0}, "error_details"=>[]}, "comps"=>{"state"=>"FINISHED"}, "distribution"=>{"items_total"=>0, "state"=>"FINISHED", "error_details"=>[], "items_left"=>0}, "errata"=>{"state"=>"FINISHED"}, "metadata"=>{"state"=>"FINISHED"}}, "id"=>"56459f8ef301a213bbfd87bb", "removed_count"=>0}, "token"=>"oQumn3XsKrdRkijuvpCNhKF2PDWZt6az", "api_version"=>"v2", "repository"=>{}}
2015-11-13 03:30:07 [I] Sync_complete called for Red Hat Satellite Tools 6.1 for RHEL 6 Server RPMs i386, running after_sync.
2015-11-13 03:30:09 [I] Completed 200 OK in 1995ms (Views: 0.2ms | ActiveRecord: 81.5ms)
2015-11-13 03:30:10 [I] Processing by Katello::Api::V2::RepositoriesController#sync_complete as JSON
2015-11-13 03:30:10 [I]   Parameters: {"call_report"=>"[FILTERED]", "event_type"=>"repo.sync.finish", "payload"=>{"importer_id"=>"yum_importer", "exception"=>nil, "repo_id"=>"1-Acme_Corp_-Red_Hat_Enterprise_Linux_Server-Red_Hat_Satellite_Tools_6_1_for_RHEL_5_Server_RPMs_i386", "traceback"=>nil, "started"=>"2015-11-13T08:30:05Z", "_ns"=>"repo_sync_results", "completed"=>"2015-11-13T08:30:10Z", "importer_type_id"=>"yum_importer", "error_message"=>nil, "summary"=>{"content"=>{"state"=>"FINISHED"}, "comps"=>{"state"=>"FINISHED"}, "distribution"=>{"state"=>"FINISHED"}, "errata"=>{"state"=>"FINISHED"}, "metadata"=>{"state"=>"FINISHED"}}, "added_count"=>0, "result"=>"success", "updated_count"=>3, "details"=>{"content"=>{"size_total"=>0, "items_left"=>0, "items_total"=>0, "state"=>"FINISHED", "size_left"=>0, "details"=>{"rpm_total"=>0, "rpm_done"=>0, "drpm_total"=>0, "drpm_done"=>0}, "error_details"=>[]}, "comps"=>{"state"=>"FINISHED"}, "distribution"=>{"items_total"=>0, "state"=>"FINISHED", "error_details"=>[], "items_left"=>0}, "errata"=>{"state"=>"FINISHED"}, "metadata"=>{"state"=>"FINISHED"}}, "id"=>"56459f92f301a2137cd6b802", "removed_count"=>0}, "token"=>"oQumn3XsKrdRkijuvpCNhKF2PDWZt6az", "api_version"=>"v2", "repository"=>{}}
2015-11-13 03:30:10 [I] Sync_complete called for Red Hat Satellite Tools 6.1 for RHEL 5 Server RPMs i386, running after_sync.
2015-11-13 03:30:11 [I] Connecting to database specified by database.yml
2015-11-13 03:30:11 [I] Connecting to database specified by database.yml
2015-11-13 03:30:11 [I] Completed 200 OK in 818ms (Views: 0.2ms | ActiveRecord: 77.2ms)
2015-11-13 03:30:17 [I] Connecting to database specified by database.yml
2015-11-13 03:30:26 [I] Sync_complete called for RHN Tools for Red Hat Enterprise Linux 5 Server RPMs x86_64 5Server, running after_sync.
2015-11-13 03:50:46 [I] Completed 200 OK in 2583ms (Views: 2.7ms | ActiveRecord: 0.3ms)
2015-11-13 06:58:25 [I]   Parameters: {"id"=>"cfd7275b-8cce-4323-8d1f-55ef85eca883"}
2015-11-13 06:58:25 [I] Completed 200 OK in 249ms (Views: 3.1ms | ActiveRecord: 0.3ms)
2015-11-13 06:59:26 [I] Processing by Katello::Api::Rhsm::CandlepinProxiesController#consumer_show as JSON
2015-11-13 06:59:26 [I]   Parameters: {"id"=>"cfd7275b-8cce-4323-8d1f-55ef85eca883"}
2015-11-13 06:59:26 [I] Completed 200 OK in 84ms (Views: 3.1ms | ActiveRecord: 0.3ms)
2015-11-13 07:00:12 [I] Connecting to database specified by database.yml
2015-11-13 07:00:12 [I] Connecting to database specified by database.yml
2015-11-13 07:00:12 [I] Connecting to database specified by database.yml
2015-11-13 07:00:18 [W] Creating scope :completer_scope. Overwriting existing method Organization.completer_scope.
2015-11-13 07:00:18 [W] Creating scope :completer_scope. Overwriting existing method Organization.completer_scope.
2015-11-13 07:00:18 [W] Creating scope :completer_scope. Overwriting existing method Location.completer_scope.
2015-11-13 07:00:18 [W] Creating scope :completer_scope. Overwriting existing method Location.completer_scope.
2015-11-13 07:00:18 [W] Creating scope :completer_scope. Overwriting existing method Organization.completer_scope.
2015-11-13 07:09:22 [I]   Parameters: {"facts"=>"[FILTERED]", "name"=>"infrhnpl002.example.com", "certname"=>"infrhnpl002.example.com", "apiv"=>"v2", :host=>{"name"=>"infrhnpl002.example.com", "certname"=>"infrhnpl002.example.com"}}
2015-11-13 07:09:22 [I] Import facts for 'infrhnpl002.example.com' completed. Added: 0, Updated: 6, Deleted 0 facts
2015-11-13 07:09:22 [I] Completed 201 Created in 251ms (Views: 179.3ms | ActiveRecord: 0.0ms)
2015-11-13 07:09:22 [I] Processing by HostsController#externalNodes as YML
2015-11-13 07:09:22 [I]   Parameters: {"name"=>"infrhnpl002.example.com"}
2015-11-13 07:09:22 [I]   Rendered text template (0.0ms)
2015-11-13 07:09:22 [I] Completed 200 OK in 48ms (Views: 0.5ms | ActiveRecord: 6.6ms)
2015-11-13 07:09:22 [I] Processing by Api::V2::ReportsController#create as JSON
2015-11-13 07:09:22 [I]   Parameters: {"report"=>"[FILTERED]", "apiv"=>"v2"}
2015-11-13 07:09:22 [I]   Rendered text template (0.0ms)
2015-11-13 07:09:22 [I] processing report for infrhnpl002.example.com
2015-11-13 07:09:22 [I] Imported report for infrhnpl002.example.com in 0.02 seconds
2015-11-13 07:09:22 [I] Completed 201 Created in 28ms (Views: 1.2ms | ActiveRecord: 0.0ms)
2015-11-13 07:30:17 [W] Creating scope :completer_scope. Overwriting existing method Organization.completer_scope.
2015-11-13 07:30:18 [W] Creating scope :completer_scope. Overwriting existing method Location.completer_scope.
2015-11-13 07:30:18 [W] Creating scope :completer_scope. Overwriting existing method Location.completer_scope.
2015-11-13 07:30:18 [W] Creating scope :completer_scope. Overwriting existing method Location.completer_scope.
2015-11-13 07:30:25 [I] Client connected.
2015-11-13 07:30:25 [I] Connected to server.
2015-11-13 07:30:25 [I] Client connected.
2015-11-13 07:30:25 [I] Connected to server.
2015-11-13 07:30:25 [I] Client connected.
2015-11-13 07:30:25 [I] Connected to server.
2015-11-13 07:30:30 [I] init config for SecureHeaders::Configuration
2015-11-13 07:30:30 [I] init config for SecureHeaders::Configuration
2015-11-13 07:30:30 [I] init config for SecureHeaders::Configuration
2015-11-13 07:30:32 [I] Processing by Katello::Api::Rhsm::CandlepinProxiesController#consumer_show as JSON
2015-11-13 07:30:32 [I]   Parameters: {"id"=>"cfd7275b-8cce-4323-8d1f-55ef85eca883"}
2015-11-13 07:30:32 [I] Completed 200 OK in 110ms (Views: 2.7ms | ActiveRecord: 0.3ms)
2015-11-13 07:30:33 [I] 2015-11-13 07:30:33 -0500: Expired 48 Reports
2015-11-13 07:30:33 [I] Client disconnected.
2015-11-13 09:41:58 [I] Completed 200 OK in 93ms (Views: 2.9ms | ActiveRecord: 0.3ms)
2015-11-13 09:42:58 [I] Processing by Katello::Api::Rhsm::CandlepinProxiesController#consumer_show as JSON
2015-11-13 09:42:58 [I]   Parameters: {"id"=>"cfd7275b-8cce-4323-8d1f-55ef85eca883"}
2015-11-13 09:42:58 [I] Completed 200 OK in 80ms (Views: 3.6ms | ActiveRecord: 0.3ms)
2015-11-13 09:43:58 [I] Processing by Katello::Api::Rhsm::CandlepinProxiesController#consumer_show as JSON
2015-11-13 09:43:58 [I]   Parameters: {"id"=>"cfd7275b-8cce-4323-8d1f-55ef85eca883"}
2015-11-13 09:43:59 [I] Completed 200 OK in 80ms (Views: 2.9ms | ActiveRecord: 0.3ms)
""".strip()


SATELLITE_OUT = """
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Katello::Config::Pulp_client/Foreman_config_entry[pulp_client_cert]/require: requires Class[Certs::Pulp_client]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Katello::Config::Pulp_client/Foreman_config_entry[pulp_client_cert]/require: requires Exec[foreman-rake-db:seed]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Katello::Config::Pulp_client/Foreman_config_entry[pulp_client_key]/require: requires Class[Certs::Pulp_client]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Katello::Config::Pulp_client/Foreman_config_entry[pulp_client_key]/require: requires Exec[foreman-rake-db:seed]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Katello::Config/File[/etc/foreman/plugins/katello.yaml]/before: requires Class[Foreman::Database]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Katello::Config/File[/etc/foreman/plugins/katello.yaml]/before: requires Exec[foreman-rake-db:migrate]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Katello::Config/File[/etc/foreman/plugins/katello.yaml]/notify: subscribes to Service[foreman-tasks]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Katello::Config/File[/etc/foreman/plugins/katello.yaml]/notify: subscribes to Class[Foreman::Service]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Katello::Config/Foreman::Config::Passenger::Fragment[katello]/require: requires Class[Foreman::Config::Passenger]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/notify: subscribes to Class[Certs::Candlepin]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Cert[kam1opapp999.example2.com-qpid-broker]/notify: subscribes to Pubkey[/etc/pki/katello/certs/kam1opapp999.example2.com-qpid-broker.crt]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Pubkey[/etc/pki/katello/certs/kam1opapp999.example2.com-qpid-broker.crt]/notify: subscribes to Privkey[/etc/pki/katello/private/kam1opapp999.example2.com-qpid-broker.key]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Privkey[/etc/pki/katello/private/kam1opapp999.example2.com-qpid-broker.key]/notify: subscribes to File[/etc/pki/katello/private/kam1opapp999.example2.com-qpid-broker.key]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/File[/etc/pki/katello/private/kam1opapp999.example2.com-qpid-broker.key]/notify: subscribes to File[/etc/pki/katello/nssdb]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/File[/etc/pki/katello/nssdb]/notify: subscribes to Exec[generate-nss-password]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Exec[generate-nss-password]/before: requires File[/etc/pki/katello/nssdb/nss_db_password-file]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/File[/etc/pki/katello/nssdb/nss_db_password-file]/notify: subscribes to Exec[create-nss-db]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Exec[create-nss-db]/before: requires Exec[delete ca]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Exec[create-nss-db]/before: requires Exec[delete broker]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Exec[create-nss-db]/before: requires Exec[delete amqp-client]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Exec[create-nss-db]/notify: subscribes to Certs::Ssltools::Certutil[ca]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Certs::Ssltools::Certutil[ca]/notify: subscribes to File[/etc/pki/katello/nssdb/cert8.db]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Certs::Ssltools::Certutil[ca]/notify: subscribes to File[/etc/pki/katello/nssdb/key3.db]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Certs::Ssltools::Certutil[ca]/notify: subscribes to File[/etc/pki/katello/nssdb/secmod.db]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/File[/etc/pki/katello/nssdb/cert8.db]/notify: subscribes to Certs::Ssltools::Certutil[broker]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/File[/etc/pki/katello/nssdb/key3.db]/notify: subscribes to Certs::Ssltools::Certutil[broker]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/File[/etc/pki/katello/nssdb/secmod.db]/notify: subscribes to Certs::Ssltools::Certutil[broker]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Certs::Ssltools::Certutil[broker]/notify: subscribes to Exec[generate-pfx-for-nss-db]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Exec[generate-pfx-for-nss-db]/notify: subscribes to Exec[add-private-key-to-nss-db]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Qpid/Exec[add-private-key-to-nss-db]/notify: subscribes to Service[qpidd]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/notify: subscribes to Class[Candlepin]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Cert[java-client]/notify: subscribes to Pubkey[/etc/pki/katello/certs/java-client.crt]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/File[/etc/pki/katello/keystore_password-file]/notify: subscribes to Exec[candlepin-generate-ssl-keystore]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Exec[candlepin-generate-ssl-keystore]/notify: subscribes to File[/usr/share/tomcat/conf/keystore]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/File[/usr/share/tomcat/conf/keystore]/notify: subscribes to Service[tomcat]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Pubkey[/etc/pki/katello/certs/java-client.crt]/notify: subscribes to Privkey[/etc/pki/katello/private/java-client.key]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Privkey[/etc/pki/katello/private/java-client.key]/notify: subscribes to Certs::Ssltools::Certutil[amqp-client]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Certs::Ssltools::Certutil[amqp-client]/subscribe: subscribes to Exec[create-nss-db]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Certs::Ssltools::Certutil[amqp-client]/notify: subscribes to Service[qpidd]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Certs::Ssltools::Certutil[amqp-client]/notify: subscribes to File[/etc/candlepin/certs/amqp]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/File[/etc/candlepin/certs/amqp]/notify: subscribes to Exec[create candlepin qpid exchange]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Exec[create candlepin qpid exchange]/require: requires Service[qpidd]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Exec[create candlepin qpid exchange]/notify: subscribes to Exec[import CA into Candlepin truststore]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Exec[import CA into Candlepin truststore]/notify: subscribes to Exec[import client certificate into Candlepin keystore]
[DEBUG 2016-08-11 13:09:49 main]  /Stage[main]/Certs::Candlepin/Exec[import client certificate into Candlepin keystore]/notify: subscribes to File[/etc/candlepin/certs/amqp/candlepin.jks]
[DEBUG 2016-08-11 13:09:50 main]  /Stage[main]/Certs::Candlepin/File[/etc/candlepin/certs/amqp/candlepin.jks]/notify: subscribes to Service[tomcat]
[DEBUG 2016-08-11 13:09:50 main]  /Stage[main]/Candlepin/notify: subscribes to Class[Qpid]
[DEBUG 2016-08-11 13:09:51 main]  /Stage[main]/Candlepin::Install/notify: subscribes to Class[Candlepin::Config]
[DEBUG 2016-08-11 13:09:51 main]  /Stage[main]/Candlepin::Config/notify: subscribes to Class[Candlepin::Database]
[DEBUG 2016-08-11 13:09:52 main]  /Stage[main]/Candlepin::Database/notify: subscribes to Class[Candlepin::Service]
""".strip()

CANDLEPIN_LOG = """
2016-09-09 13:45:52,650 [req=bd5a4284-d280-4fc5-a3d5-fc976b7aa5cc, org=] INFO org.candlepin.common.filter.LoggingFilter - Request: verb=GET, uri=/candlepin/consumers/f7677b4b-c470-4626-86a4-2fdf2546af4b
2016-09-09 13:45:52,784 [req=bd5a4284-d280-4fc5-a3d5-fc976b7aa5cc, org=ING_Luxembourg_SA] INFO  org.candlepin.common.filter.LoggingFilter - Response: status=200, content-type="application/json", time=134
2016-09-09 13:45:52,947 [req=909ca4c5-f24e-4212-8f23-cc754d06ac57, org=] INFO org.candlepin.common.filter.LoggingFilter - Request: verb=GET, uri=/candlepin/consumers/f7677b4b-c470-4626-86a4-2fdf2546af4b/content_overrides
2016-09-09 13:45:52,976 [req=909ca4c5-f24e-4212-8f23-cc754d06ac57, org=] INFO org.candlepin.common.filter.LoggingFilter - Response: status=200, content-type="application/json", time=29
2016-09-09 13:45:53,072 [req=49becd26-5dfe-4d2f-8667-470519230d88, org=] INFO org.candlepin.common.filter.LoggingFilter - Request: verb=GET, uri=/candlepin/consumers/f7677b4b-c470-4626-86a4-2fdf2546af4b/release
2016-09-09 13:45:53,115 [req=49becd26-5dfe-4d2f-8667-470519230d88, org=ING_Luxembourg_SA] INFO  org.candlepin.common.filter.LoggingFilter - Response: status=200, content-type="application/json", time=43
""".strip()


PROXY_LOG = """
127.0.0.1 - - [31/May/2016:09:42:28 -0400] "GET /puppet/environments/KT_Encore_Library_RHEL_6_5/classes HTTP/1.1" 200 76785 6.1205
127.0.0.1 - - [31/May/2016:09:42:38 -0400] "GET /puppet/environments/KT_Encore_Library_RHEL_7_6/classes HTTP/1.1" 200 76785 4.4754
127.0.0.1 - - [31/May/2016:09:42:49 -0400] "GET /puppet/environments/KT_Encore_Library_RHEL6_8/classes HTTP/1.1" 200 76785 4.5776
127.0.0.1 - - [31/May/2016:09:57:34 -0400] "GET /tftp/serverName HTTP/1.1" 200 38 0.0014
E, [2016-05-31T09:57:35.884636 #4494] ERROR -- : Record 172.16.100.0/172.16.100.17 not found ]
""".strip()


CANDLEPIN_ERROR_LOG = """
2016-09-07 13:56:49,001 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
2016-09-07 14:07:33,735 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
2016-09-07 14:09:55,173 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
2016-09-07 15:20:33,796 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
2016-09-07 15:27:34,367 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
2016-09-07 16:49:24,650 [=, org=] WARN  org.apache.qpid.transport.network.security.ssl.SSLUtil - Exception received while trying to verify hostname
2016-09-07 18:07:53,688 [req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28, org=org_ray] ERROR org.candlepin.sync.Importer - Conflicts occurred during import that were not overridden:
2016-09-07 18:07:53,690 [req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28, org=org_ray] ERROR org.candlepin.sync.Importer - [DISTRIBUTOR_CONFLICT]
2016-09-07 18:07:53,711 [req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28, org=org_ray] ERROR org.candlepin.resource.OwnerResource - Recording import failure org.candlepin.sync.ImportConflictException: Owner has already imported from another subscription management application.
""".strip()


FOREMAN_SSL_ACCESS_SSL_LOG = """
10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/385e688f-43ad-41b2-9fc7-593942ddec78 HTTP/1.1" 200 10736 "-" "-"
10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/status HTTP/1.1" 200 263 "-" "-"
10.185.73.33 - 8a31cd915917666001591d6fb44602a7 [27/Mar/2017:13:34:52 -0400] "GET /pulp/repos/Acme_Inc/Library/RHEL7_Sat_Capsule_Servers/content/dist/rhel/server/7/7Server/x86_64/os/repodata/repomd.xml HTTP/1.1" 200 2018 "-" "urlgrabber/3.10 yum/3.4.3"
10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/4f8a39d0-38b6-4663-8b7e-03368be4d3ab/owner HTTP/1.1" 200 5159 "-" "-"
10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/385e688f-43ad-41b2-9fc7-593942ddec78/compliance HTTP/1.1" 200 5527 "-" "-"
10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/4f8a39d0-38b6-4663-8b7e-03368be4d3ab HTTP/1.1" 200 10695 "-" "-"
10.181.73.211 - rhcapkdc.example2.com [27/Mar/2017:13:34:52 -0400] "GET /rhsm/consumers/385e688f-43ad-41b2-9fc7-593942ddec78/entitlements?exclude=certificates.key&exclude=certificates.cert HTTP/1.1" 200 9920 "-" "-"
""".strip()


def test_production_log():
    fm_log = ProductionLog(context_wrap(PRODUCTION_LOG))
    assert 2 == len(fm_log.get("Rendered text template"))
    assert "Expired 48 Reports" in fm_log
    assert fm_log.get("Completed 200 OK in 93")[0]['raw_message'] == \
        "2015-11-13 09:41:58 [I] Completed 200 OK in 93ms (Views: 2.9ms | ActiveRecord: 0.3ms)"
    assert len(list(fm_log.get_after(datetime(2015, 11, 13, 9, 41, 58)))) == 7


def test_proxy_log():
    px_log = ProxyLog(context_wrap(PROXY_LOG))
    assert "ERROR -- " in px_log
    assert len(px_log.get("KT_Encore_Library_RHEL")) == 3
    # Test selection by both time formats - regular line format
    assert len(list(px_log.get_after(datetime(2016, 5, 31, 9, 45, 0)))) == 2
    # ... and error format
    assert len(list(px_log.get_after(datetime(2016, 5, 31, 9, 57, 35)))) == 1


def test_candlepin_log():
    cp_log = CandlepinLog(context_wrap(CANDLEPIN_LOG))
    assert "req=49becd26-5dfe-4d2f-8667-470519230d88" in cp_log
    assert len(cp_log.get("req=bd5a4284-d280-4fc5-a3d5-fc976b7aa5cc")) == 2
    assert len(list(cp_log.get_after(datetime(2016, 9, 9, 13, 45, 53)))) == 2


def test_satellite_log():
    sat_log = SatelliteLog(context_wrap(SATELLITE_OUT))
    assert "subscribes to Class[Qpid]" in sat_log
    assert len(sat_log.get("notify: subscribes to Class[")) == 7
    assert len(list(sat_log.get_after(datetime(2016, 8, 11, 13, 9, 50)))) == 5


def test_candlepin_error_log():
    error_log = CandlepinErrorLog(context_wrap(CANDLEPIN_ERROR_LOG))
    assert "req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28" in error_log
    assert len(error_log.get("req=d9dc3cfd-abf7-485e-b1eb-e1e28e4b0f28")) == 3
    assert len(list(error_log.get_after(datetime(2016, 9, 7, 18, 7, 53)))) == 3
    assert len(list(error_log.get_after(datetime(2016, 9, 7, 16, 0, 0)))) == 4


def test_foreman_ssl_access_ssl_log():
    foreman_ssl_access_log = ForemanSSLAccessLog(context_wrap(FOREMAN_SSL_ACCESS_SSL_LOG))
    assert "385e688f-43ad-41b2-9fc7-593942ddec78" in foreman_ssl_access_log
    assert len(foreman_ssl_access_log.get("GET /rhsm/consumers")) == 5
    assert len(foreman_ssl_access_log.get("385e688f-43ad-41b2-9fc7-593942ddec78")) == 3
    assert len(list(foreman_ssl_access_log.get_after(datetime(2017, 3, 27, 13, 34, 0)))) == 7
