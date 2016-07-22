from falafel.tests import context_wrap
from falafel.mappers.foreman_production_log import foreman_production_log

PRODUCTION_LOG = """
2015-11-13 03:30:07 [I] Completed 200 OK in 1783ms (Views: 0.2ms | ActiveRecord: 172.9ms)
2015-11-13 03:30:07 [I] Processing by Katello::Api::V2::RepositoriesController#sync_complete as JSON
2015-11-13 03:30:07 [I]   Parameters: {"call_report"=>"[FILTERED]", "event_type"=>"repo.sync.finish", "payload"=>{"importer_id"=>"yum_importer", "exception"=>nil, "repo_id"=>"1-Gulfstream_Aerospace_Corp_-Red_Hat_Enterprise_Linux_Server-Red_Hat_Satellite_Tools_6_1_for_RHEL_6_Server_RPMs_i386", "traceback"=>nil, "started"=>"2015-11-13T08:30:00Z", "_ns"=>"repo_sync_results", "completed"=>"2015-11-13T08:30:06Z", "importer_type_id"=>"yum_importer", "error_message"=>nil, "summary"=>{"content"=>{"state"=>"FINISHED"}, "comps"=>{"state"=>"FINISHED"}, "distribution"=>{"state"=>"FINISHED"}, "errata"=>{"state"=>"FINISHED"}, "metadata"=>{"state"=>"FINISHED"}}, "added_count"=>0, "result"=>"success", "updated_count"=>3, "details"=>{"content"=>{"size_total"=>0, "items_left"=>0, "items_total"=>0, "state"=>"FINISHED", "size_left"=>0, "details"=>{"rpm_total"=>0, "rpm_done"=>0, "drpm_total"=>0, "drpm_done"=>0}, "error_details"=>[]}, "comps"=>{"state"=>"FINISHED"}, "distribution"=>{"items_total"=>0, "state"=>"FINISHED", "error_details"=>[], "items_left"=>0}, "errata"=>{"state"=>"FINISHED"}, "metadata"=>{"state"=>"FINISHED"}}, "id"=>"56459f8ef301a213bbfd87bb", "removed_count"=>0}, "token"=>"oQumn3XsKrdRkijuvpCNhKF2PDWZt6az", "api_version"=>"v2", "repository"=>{}}
2015-11-13 03:30:07 [I] Sync_complete called for Red Hat Satellite Tools 6.1 for RHEL 6 Server RPMs i386, running after_sync.
2015-11-13 03:30:09 [I] Completed 200 OK in 1995ms (Views: 0.2ms | ActiveRecord: 81.5ms)
2015-11-13 03:30:10 [I] Processing by Katello::Api::V2::RepositoriesController#sync_complete as JSON
2015-11-13 03:30:10 [I]   Parameters: {"call_report"=>"[FILTERED]", "event_type"=>"repo.sync.finish", "payload"=>{"importer_id"=>"yum_importer", "exception"=>nil, "repo_id"=>"1-Gulfstream_Aerospace_Corp_-Red_Hat_Enterprise_Linux_Server-Red_Hat_Satellite_Tools_6_1_for_RHEL_5_Server_RPMs_i386", "traceback"=>nil, "started"=>"2015-11-13T08:30:05Z", "_ns"=>"repo_sync_results", "completed"=>"2015-11-13T08:30:10Z", "importer_type_id"=>"yum_importer", "error_message"=>nil, "summary"=>{"content"=>{"state"=>"FINISHED"}, "comps"=>{"state"=>"FINISHED"}, "distribution"=>{"state"=>"FINISHED"}, "errata"=>{"state"=>"FINISHED"}, "metadata"=>{"state"=>"FINISHED"}}, "added_count"=>0, "result"=>"success", "updated_count"=>3, "details"=>{"content"=>{"size_total"=>0, "items_left"=>0, "items_total"=>0, "state"=>"FINISHED", "size_left"=>0, "details"=>{"rpm_total"=>0, "rpm_done"=>0, "drpm_total"=>0, "drpm_done"=>0}, "error_details"=>[]}, "comps"=>{"state"=>"FINISHED"}, "distribution"=>{"items_total"=>0, "state"=>"FINISHED", "error_details"=>[], "items_left"=>0}, "errata"=>{"state"=>"FINISHED"}, "metadata"=>{"state"=>"FINISHED"}}, "id"=>"56459f92f301a2137cd6b802", "removed_count"=>0}, "token"=>"oQumn3XsKrdRkijuvpCNhKF2PDWZt6az", "api_version"=>"v2", "repository"=>{}}
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
2015-11-13 07:09:22 [I]   Parameters: {"facts"=>"[FILTERED]", "name"=>"infrhnpl002.gac.gulfaero.com", "certname"=>"infrhnpl002.gac.gulfaero.com", "apiv"=>"v2", :host=>{"name"=>"infrhnpl002.gac.gulfaero.com", "certname"=>"infrhnpl002.gac.gulfaero.com"}}
2015-11-13 07:09:22 [I] Import facts for 'infrhnpl002.gac.gulfaero.com' completed. Added: 0, Updated: 6, Deleted 0 facts
2015-11-13 07:09:22 [I] Completed 201 Created in 251ms (Views: 179.3ms | ActiveRecord: 0.0ms)
2015-11-13 07:09:22 [I] Processing by HostsController#externalNodes as YML
2015-11-13 07:09:22 [I]   Parameters: {"name"=>"infrhnpl002.gac.gulfaero.com"}
2015-11-13 07:09:22 [I]   Rendered text template (0.0ms)
2015-11-13 07:09:22 [I] Completed 200 OK in 48ms (Views: 0.5ms | ActiveRecord: 6.6ms)
2015-11-13 07:09:22 [I] Processing by Api::V2::ReportsController#create as JSON
2015-11-13 07:09:22 [I]   Parameters: {"report"=>"[FILTERED]", "apiv"=>"v2"}
2015-11-13 07:09:22 [I]   Rendered text template (0.0ms)
2015-11-13 07:09:22 [I] processing report for infrhnpl002.gac.gulfaero.com
2015-11-13 07:09:22 [I] Imported report for infrhnpl002.gac.gulfaero.com in 0.02 seconds
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

foreman_production_log.filters.extend([
    "Rendered text template",
    "Expired 48 Reports",
    "Completed 200 OK in 93ms",
])


def test_foreman_production_log():
    fm_log = foreman_production_log(context_wrap(PRODUCTION_LOG))
    assert 2 == len(fm_log.get("Rendered text template"))
    assert "Expired 48 Reports" in fm_log
    assert fm_log.get("Completed 200 OK in 93")[0] == \
        "2015-11-13 09:41:58 [I] Completed 200 OK in 93ms (Views: 2.9ms | ActiveRecord: 0.3ms)"
