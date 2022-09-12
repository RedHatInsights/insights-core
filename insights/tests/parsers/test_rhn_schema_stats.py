from insights.tests import context_wrap
from insights.parsers.rhn_schema_stats import DBStatsLog

POSTGRESQL_LOG = """
 schema |             table              |   rows
--------+--------------------------------+----------
 public | rhnsnapshotpackage             | 47428950
 public | rhnpackagefile                 | 32174333
 public | rhnpackagecapability           | 12934215
 public | rhnpackagechangelogrec         | 11269933
 public | rhnchecksum                    | 10129746
 public | rhnactionconfigrevision        |  2894957
 public | rhnpackageprovides             |  2712442
 public | rhnpackagerequires             |  2532861
 public | rhn_command_target             |  1009152
 public | rhnconfigfilename              |        0
 public | rhnxccdfidentsystem            |        0
 public | rhndistchannelmap              |        0
 public | rhnactionvirtshutdown          |        0
 public | rhnpublicchannelfamily         |        0
(402 rows)

                        name                        | type |             table              |                                                                                               src
----------------------------------------------------+------+--------------------------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 chkpb_probe_type_ck                                | c    | rhn_check_probe                | ((probe_type)::text = 'check'::text)
 cmdtg_target_type_ck                               | c    | rhn_command_target             | ((target_type)::text = ANY (ARRAY[('cluster')))
 contperm_wbuserid_fk                               | f    | web_user_contact_permission    |
 log_id_pk                                          | p    | log                            |
 log_user_id_fk                                     | f    | log                            |
 personal_info_web_user_id_fk                       | f    | web_user_personal_info         |
 prbst_probe_id_scout_id_pk                         | p    | rhn_probe_state                |
 pxt_sessions_pk                                    | p    | pxtsessions                    |
 pxtsessions_user                                   | f    | pxtsessions                    |
 qrtz_blob_triggers_pkey                            | p    | qrtz_blob_triggers             |
 rhn_actchainent_aid_fk                             | f    | rhnactionchainentry            |
 rhn_actchainent_sid_fk                             | f    | rhnactionchainentry            |
 rhn_action_archived_ck                             | c    | rhnaction                      | (archived = ANY (ARRAY[(0)::numeric, (1)::numeric]))
 rhn_action_at_fk                                   | f    | rhnaction                      |
 rhn_action_chain_id_pk                             | p    | rhnactionchain                 |
 rhn_action_oid_fk                                  | f    | rhnaction                      |
 rhn_action_pk                                      | p    | rhnaction                      |
 rhn_action_prereq_fk                               | f    | rhnaction                      |
 rhn_avsp_aid_fk                                    | f    | rhnactionvirtschedulepoller    |
 rhn_avsp_aid_pk                                    | p    | rhnactionvirtschedulepoller    |
 rhn_avstart_aid_pk                                 | p    | rhnactionvirtstart             |
 wusi_ipb_ck                                        | c    | web_user_site_info             | (is_po_box = ANY (ARRAY['1'::bpchar, '0'::bpchar]))
 wusi_type_fk                                       | f    | web_user_site_info             |
 wusi_wuid_fk                                       | f    | web_user_site_info             |
 wust_type_pk                                       | p    | web_user_site_type             |
(1771 rows)

                label                |  created   |  modified  |       name       | epoch | version  | release
-------------------------------------+------------+------------+------------------+-------+----------+----------
 schema-from-20130309-133209         | 2013-03-09 | 2013-07-02 | satellite-schema |       | 5.5.0.17 | 1.el6sat
 schema-from-20130702-090610         | 2013-07-02 | 2014-05-19 | satellite-schema |       | 5.5.0.20 | 1.el6sat
 schema-migrate-from-20140519-111223 | 2014-05-19 | 2014-12-08 | satellite-schema |       | 5.5.0.22 | 1.el6sat
 schema-from-20141208-181050         | 2014-12-08 | 2014-12-09 | satellite-schema |       | 5.6.0.10 | 1.el6sat
 schema-from-20150803-160946         | 2015-08-03 | 2015-10-16 | satellite-schema |       | 5.6.0.26 | 1.el6sat
 schema-from-20151016-113838         | 2015-10-16 | 2015-10-16 | satellite-schema |       | 5.7.0.11 | 1.el6sat
 schema                              | 2015-10-16 | 2015-10-16 | satellite-schema |       | 5.7.0.19 | 1.el6sat
(11 rows)
""".strip()

ORACLE_LOG = """
RHN_REDIRECT_TYPES: 4
RHN_SATELLITE_STATE: 0
RHN_SAT_CLUSTER: 0
RHN_SAT_CLUSTER_PROBE: 0
RHN_SAT_NODE: 0
RHN_SCHEDULES: 1
RHN_SCHEDULE_DAYS: 7
RHN_SCHEDULE_TYPES: 3
RHN_SCHEDULE_WEEKS: 0
RHN_SEMANTIC_DATA_TYPE: 7
RHN_SERVER_MONITORING_INFO: 0
RHN_SERVICE_PROBE_ORIGINS: 0
RHN_SNMP_ALERT: 0
RHN_STRATEGIES: 6
RHN_THRESHOLD_TYPE: 4
RHN_TIME_ZONE_NAMES: 22
RHNERRATASEVERITY: 112

PL/SQL procedure successfully completed.


CONSTRAINT NAME \t       TYPE TABLE NAME\t\t\t   SEARCH CONDITION\t\t\t\t\t\t\t\t    REFERENCED CONSTRAINT
------------------------------ ---- ------------------------------ -------------------------------------------------------------------------------- ------------------------------
SYS_C003263\t\t       C    RHNERRATASEVERITY\t\t   "LABEL" IS NOT NULL
RHN_ERRATATMP_ADV_TYPE_CK      C    RHNERRATATMP\t\t   advisory_type in ('Bug Fix Advisory',
\t\t\t\t\t\t\t\t   \t\t\t\t\t\t\t    'Product E

SYS_C003988\t\t       C    RHNERRATATMP\t\t   "LAST_MODIFIED" IS NOT NULL
WUSI_IPB_CK\t\t       C    WEB_USER_SITE_INFO\t\t   is_po_box in ('1','0')
WUSI_ID_PK\t\t       P    WEB_USER_SITE_INFO
WUSI_TYPE_FK\t\t       R    WEB_USER_SITE_INFO\t\t\t\t\t\t\t\t\t\t\t\t    WUST_TYPE_PK
WUSI_WUID_FK\t\t       R    WEB_USER_SITE_INFO\t\t\t\t\t\t\t\t\t\t\t\t    WEB_CONTACT_PK

2613 rows selected.


LABEL\t\t\t       CREATED\t  MODIFIED   NAME\t\t       EPOCH\t  VERSION    RELEASE
------------------------------ ---------- ---------- ------------------------- ---------- ---------- ----------
schema-from-20131111-143638    2013-11-11 2013-11-11 satellite-schema\t\t\t  5.5.0.13   1.el5sat
schema\t\t\t       2014-05-01 2014-05-01 satellite-schema\t\t\t  5.5.0.22   1.el5sat

8 rows selected.
""".strip()

NO_LOG = """
"""


def test_rhn_schema_stats_pgs():

    pg_log = DBStatsLog(context_wrap(POSTGRESQL_LOG))
    assert 'rhnsnapshotPACKAGE' in pg_log
    assert 'rhnsnapshotpackage_' not in pg_log
    assert pg_log.get_table('chkpb_probe_type_ck') == []
    assert pg_log.get_table('RHN_COMMAND_TARGET', ic=False) == []
    assert pg_log.get_table('RHN_COMMAND_TARGET') == [
        {'rows': '1009152', 'schema': 'public', 'table': 'rhn_command_target'},
        {'name': 'cmdtg_target_type_ck',
         'src': "((target_type)::text = ANY (ARRAY[('cluster')))",
         'table': 'rhn_command_target', 'type': 'c'}
    ]


def test_rhn_schema_stats_ora():
    ora_log = DBStatsLog(context_wrap(ORACLE_LOG))
    assert 'rhnerratatmP' in ora_log
    assert 'rhnerratatmP_' not in ora_log
    assert ora_log.get_table('rhnerrataseverity', ic=False) == []
    assert ora_log.get_table('rhnerrataseverity') == [
        {'rows': 112, 'table': 'RHNERRATASEVERITY'},
        {'CONSTRAINT NAME': 'SYS_C003263', 'REFERENCED CONSTRAINT': '',
         'SEARCH CONDITION': '"LABEL" IS NOT NULL',
         'TABLE NAME': 'RHNERRATASEVERITY', 'TYPE': 'C'}
    ]


def test_rhn_schema_stats_none():
    log = DBStatsLog(context_wrap(NO_LOG))
    assert list(log.data.keys()) == []
