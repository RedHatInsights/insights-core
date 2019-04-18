from insights.parsers.ceph_insights import CephInsights
from insights.parsers import ceph_insights
from insights.tests import context_wrap
import six
import doctest

TEST_DATA = """
{
  "crush_map": {
    "tunables": {
      "profile": "jewel",
      "minimum_required_version": "jewel",
      "has_v3_rules": 0,
      "has_v4_buckets": 1,
      "choose_total_tries": 50,
      "require_feature_tunables3": 1,
      "require_feature_tunables5": 1,
      "legacy_tunables": 0,
      "chooseleaf_descend_once": 1,
      "chooseleaf_stable": 1,
      "choose_local_fallback_tries": 0,
      "has_v2_rules": 0,
      "straw_calc_version": 1,
      "allowed_bucket_algs": 54,
      "has_v5_rules": 0,
      "require_feature_tunables2": 1,
      "optimal_tunables": 1,
      "choose_local_tries": 0,
      "chooseleaf_vary_r": 1,
      "require_feature_tunables": 1
    },
    "rules": [
      {
        "min_size": 1,
        "rule_name": "replicated_rule",
        "steps": [
          {
            "item_name": "default",
            "item": -1,
            "op": "take"
          },
          {
            "num": 0,
            "type": "osd",
            "op": "choose_firstn"
          },
          {
            "op": "emit"
          }
        ],
        "ruleset": 0,
        "type": 1,
        "rule_id": 0,
        "max_size": 10
      }
    ],
    "buckets": [
      {
        "hash": "rjenkins1",
        "name": "default",
        "weight": 1926,
        "type_id": 10,
        "alg": "straw2",
        "type_name": "root",
        "items": [
          {
            "id": -3,
            "weight": 1926,
            "pos": 0
          }
        ],
        "id": -1
      },
      {
        "hash": "rjenkins1",
        "name": "default~ssd",
        "weight": 1926,
        "type_id": 10,
        "alg": "straw2",
        "type_name": "root",
        "items": [
          {
            "id": -4,
            "weight": 1926,
            "pos": 0
          }
        ],
        "id": -2
      },
      {
        "hash": "rjenkins1",
        "name": "daq",
        "weight": 1926,
        "type_id": 1,
        "alg": "straw2",
        "type_name": "host",
        "items": [
          {
            "id": 0,
            "weight": 642,
            "pos": 0
          },
          {
            "id": 1,
            "weight": 642,
            "pos": 1
          },
          {
            "id": 2,
            "weight": 642,
            "pos": 2
          }
        ],
        "id": -3
      },
      {
        "hash": "rjenkins1",
        "name": "daq~ssd",
        "weight": 1926,
        "type_id": 1,
        "alg": "straw2",
        "type_name": "host",
        "items": [
          {
            "id": 0,
            "weight": 642,
            "pos": 0
          },
          {
            "id": 1,
            "weight": 642,
            "pos": 1
          },
          {
            "id": 2,
            "weight": 642,
            "pos": 2
          }
        ],
        "id": -4
      }
    ],
    "devices": [
      {
        "class": "ssd",
        "id": 0,
        "name": "osd.0"
      },
      {
        "class": "ssd",
        "id": 1,
        "name": "osd.1"
      },
      {
        "class": "ssd",
        "id": 2,
        "name": "osd.2"
      }
    ],
    "choose_args": {},
    "types": [
      {
        "name": "osd",
        "type_id": 0
      },
      {
        "name": "host",
        "type_id": 1
      },
      {
        "name": "chassis",
        "type_id": 2
      },
      {
        "name": "rack",
        "type_id": 3
      },
      {
        "name": "row",
        "type_id": 4
      },
      {
        "name": "pdu",
        "type_id": 5
      },
      {
        "name": "pod",
        "type_id": 6
      },
      {
        "name": "room",
        "type_id": 7
      },
      {
        "name": "datacenter",
        "type_id": 8
      },
      {
        "name": "region",
        "type_id": 9
      },
      {
        "name": "root",
        "type_id": 10
      }
    ]
  },
  "pg_summary": {
    "by_osd": {
      "1": {
        "peering": 13
      },
      "0": {
        "peering": 16
      },
      "2": {
        "peering": 16
      }
    },
    "by_pool": {
      "1": {
        "peering": 8
      },
      "2": {
        "peering": 8
      }
    },
    "all": {
      "peering": 16
    },
    "pg_stats_sum": {
      "acting": 45,
      "log_size": 39,
      "ondisk_log_size": 39,
      "stat_sum": {
        "num_evict": 0,
        "num_evict_kb": 0,
        "num_bytes_hit_set_archive": 0,
        "num_whiteouts": 0,
        "num_objects_pinned": 0,
        "num_scrub_errors": 0,
        "num_evict_mode_full": 0,
        "num_read": 0,
        "num_objects_recovered": 0,
        "num_objects_omap": 14,
        "num_objects_missing_on_primary": 0,
        "num_write": 45,
        "num_object_clones": 0,
        "num_objects": 22,
        "num_deep_scrub_errors": 0,
        "num_shallow_scrub_errors": 0,
        "num_read_kb": 0,
        "num_objects_missing": 0,
        "num_flush_kb": 0,
        "num_flush_mode_high": 0,
        "num_write_kb": 13,
        "num_large_omap_objects": 0,
        "num_evict_mode_some": 0,
        "num_objects_degraded": 0,
        "num_flush": 0,
        "num_objects_misplaced": 0,
        "num_bytes_recovered": 0,
        "num_objects_hit_set_archive": 0,
        "num_legacy_snapsets": 0,
        "num_keys_recovered": 0,
        "num_flush_mode_low": 0,
        "num_objects_manifest": 0,
        "num_objects_unfound": 0,
        "num_promote": 0,
        "num_object_copies": 66,
        "num_bytes": 2286,
        "num_objects_dirty": 22
      },
      "up": 45
    }
  },
  "service_map": {
    "services": {},
    "epoch": 1,
    "modified": "0.000000"
  },
  "crashes": {
    "hours": 24,
    "summary": {}
  },
  "mon_status": {
    "election_epoch": 12,
    "quorum_age": "11.1322s",
    "outside_quorum": [],
    "rank": 0,
    "monmap": {
      "features": {
        "optional": [],
        "persistent": [
          "kraken",
          "luminous",
          "mimic",
          "osdmap-prune",
          "nautilus"
        ]
      },
      "created": "2018-09-21 10:41:49.406653",
      "modified": "2018-09-21 10:41:49.406653",
      "epoch": 1,
      "mons": [
        {
          "public_addr": "127.0.0.1:40226/0",
          "name": "a",
          "rank": 0,
          "addr": "127.0.0.1:40226/0"
        },
        {
          "public_addr": "127.0.0.1:40227/0",
          "name": "b",
          "rank": 1,
          "addr": "127.0.0.1:40227/0"
        },
        {
          "public_addr": "127.0.0.1:40228/0",
          "name": "c",
          "rank": 2,
          "addr": "127.0.0.1:40228/0"
        }
      ],
      "fsid": "d02162fd-bee9-4cb5-973b-2f7b6d97102a"
    },
    "state": "leader",
    "features": {
      "quorum_con": "4611087854031142911",
      "quorum_mon": [
        "kraken",
        "luminous",
        "mimic",
        "osdmap-prune",
        "nautilus"
      ],
      "required_mon": [
        "kraken",
        "luminous",
        "mimic",
        "osdmap-prune",
        "nautilus"
      ],
      "required_con": "2449958747315912708"
    },
    "extra_probe_peers": [],
    "feature_map": {
      "mds": [
        {
          "release": "luminous",
          "num": 1,
          "features": "0x3ffddff8ffa4ffff"
        }
      ],
      "mon": [
        {
          "release": "luminous",
          "num": 1,
          "features": "0x3ffddff8ffa4ffff"
        }
      ],
      "mgr": [
        {
          "release": "luminous",
          "num": 1,
          "features": "0x3ffddff8ffa4ffff"
        }
      ]
    },
    "quorum": [
      0,
      1,
      2
    ],
    "sync_provider": [],
    "name": "a"
  },
  "df": {
    "pools": [
      {
        "stats": {
          "wr": 0,
          "quota_objects": 0,
          "bytes_used": 0,
          "max_avail": 9553910784,
          "rd": 0,
          "rd_bytes": 0,
          "objects": 0,
          "percent_used": 0.0,
          "kb_used": 0,
          "quota_bytes": 0,
          "raw_bytes_used": 0,
          "wr_bytes": 0,
          "dirty": 0
        },
        "name": "cephfs_data_a",
        "id": 1
      },
      {
        "stats": {
          "wr": 45,
          "quota_objects": 0,
          "bytes_used": 2286,
          "max_avail": 9553910784,
          "rd": 0,
          "rd_bytes": 0,
          "objects": 22,
          "percent_used": 2.3927370307319507e-07,
          "kb_used": 3,
          "quota_bytes": 0,
          "raw_bytes_used": 6858,
          "wr_bytes": 13312,
          "dirty": 22
        },
        "name": "cephfs_metadata_a",
        "id": 2
      }
    ],
    "stats": {
      "total_objects": 22,
      "total_used_bytes": 3425656832,
      "total_bytes": 32413556736,
      "total_percent_used": 10.56859302520752,
      "total_avail_bytes": 28987899904
    }
  },
  "osd_tree": {
    "nodes": [
      {
        "children": [
          -3
        ],
        "type_id": 10,
        "type": "root",
        "id": -1,
        "name": "default"
      },
      {
        "name": "daq",
        "type_id": 1,
        "id": -3,
        "pool_weights": {},
        "type": "host",
        "children": [
          2,
          1,
          0
        ]
      },
      {
        "status": "up",
        "name": "osd.0",
        "exists": 1,
        "type_id": 0,
        "reweight": 1.0,
        "crush_weight": 0.009796142578125,
        "pool_weights": {},
        "primary_affinity": 1.0,
        "depth": 2,
        "device_class": "ssd",
        "type": "osd",
        "id": 0
      },
      {
        "status": "up",
        "name": "osd.1",
        "exists": 1,
        "type_id": 0,
        "reweight": 1.0,
        "crush_weight": 0.009796142578125,
        "pool_weights": {},
        "primary_affinity": 1.0,
        "depth": 2,
        "device_class": "ssd",
        "type": "osd",
        "id": 1
      },
      {
        "status": "up",
        "name": "osd.2",
        "exists": 1,
        "type_id": 0,
        "reweight": 1.0,
        "crush_weight": 0.009796142578125,
        "pool_weights": {},
        "primary_affinity": 1.0,
        "depth": 2,
        "device_class": "ssd",
        "type": "osd",
        "id": 2
      }
    ],
    "stray": []
  },
  "osd_metadata": {
    "1": {
      "bluefs_db_size": "67108864",
      "bluestore_bdev_size": "10737418240",
      "bluestore_bdev_driver": "KernelDevice"
    },
    "0": {
      "bluefs_db_size": "67108864",
      "bluestore_bdev_size": "10737418240",
      "bluestore_bdev_driver": "KernelDevice"
    },
    "2": {
      "bluefs_db_size": "67108864",
      "bluestore_bdev_size": "10737418240",
      "bluestore_bdev_driver": "KernelDevice"
    }
  },
  "osd_dump": {
    "nearfull_ratio": 0.9900000095367432,
    "backfillfull_ratio": 0.9900000095367432,
    "last_in_change": "2018-09-21 10:42:23.201021",
    "full_ratio": 0.9900000095367432,
    "cluster_snapshot": "",
    "pg_upmap": [],
    "new_purged_snaps": [],
    "erasure_code_profiles": {
      "default": {
        "crush-failure-domain": "osd",
        "k": "2",
        "technique": "reed_sol_van",
        "m": "1",
        "plugin": "jerasure"
      }
    },
    "osds": [
      {
        "public_addrs": {
          "addrvec": [
            {
              "nonce": 4283,
              "type": "legacy",
              "addr": "127.0.0.1:6800"
            }
          ]
        },
        "weight": 1.0,
        "up_from": 17,
        "heartbeat_front_addr": {
          "addrvec": [
            {
              "nonce": 4283,
              "type": "legacy",
              "addr": "127.0.0.1:6802"
            }
          ]
        },
        "down_at": 16,
        "up": 1,
        "cluster_addrs": {
          "addrvec": [
            {
              "nonce": 4283,
              "type": "legacy",
              "addr": "127.0.0.1:6801"
            }
          ]
        },
        "lost_at": 0,
        "primary_affinity": 1.0,
        "state": [
          "exists",
          "up"
        ],
        "last_clean_begin": 5,
        "last_clean_end": 15,
        "in": 1,
        "public_addr": "127.0.0.1:6800/4283",
        "up_thru": 19,
        "heartbeat_back_addrs": {
          "addrvec": [
            {
              "nonce": 4283,
              "type": "legacy",
              "addr": "127.0.0.1:6803"
            }
          ]
        },
        "cluster_addr": "127.0.0.1:6801/4283",
        "osd": 0,
        "uuid": "c8c26eda-d1e4-4ab2-839d-a07573414e41"
      },
      {
        "public_addrs": {
          "addrvec": [
            {
              "nonce": 4559,
              "type": "legacy",
              "addr": "127.0.0.1:6804"
            }
          ]
        },
        "weight": 1.0,
        "up_from": 18,
        "heartbeat_front_addr": {
          "addrvec": [
            {
              "nonce": 4559,
              "type": "legacy",
              "addr": "127.0.0.1:6806"
            }
          ]
        },
        "down_at": 17,
        "up": 1,
        "cluster_addrs": {
          "addrvec": [
            {
              "nonce": 4559,
              "type": "legacy",
              "addr": "127.0.0.1:6805"
            }
          ]
        },
        "lost_at": 0,
        "primary_affinity": 1.0,
        "state": [
          "exists",
          "up"
        ],
        "last_clean_begin": 8,
        "last_clean_end": 15,
        "in": 1,
        "public_addr": "127.0.0.1:6804/4559",
        "up_thru": 19,
        "heartbeat_back_addrs": {
          "addrvec": [
            {
              "nonce": 4559,
              "type": "legacy",
              "addr": "127.0.0.1:6807"
            }
          ]
        },
        "cluster_addr": "127.0.0.1:6805/4559",
        "osd": 1,
        "uuid": "b6105fad-2e66-4ea3-a0ff-b14eb1f3e52f"
      },
      {
        "public_addrs": {
          "addrvec": [
            {
              "nonce": 4723,
              "type": "legacy",
              "addr": "127.0.0.1:6809"
            }
          ]
        },
        "weight": 1.0,
        "up_from": 19,
        "heartbeat_front_addr": {
          "addrvec": [
            {
              "nonce": 4723,
              "type": "legacy",
              "addr": "127.0.0.1:6811"
            }
          ]
        },
        "down_at": 18,
        "up": 1,
        "cluster_addrs": {
          "addrvec": [
            {
              "nonce": 4723,
              "type": "legacy",
              "addr": "127.0.0.1:6810"
            }
          ]
        },
        "lost_at": 0,
        "primary_affinity": 1.0,
        "state": [
          "exists",
          "up"
        ],
        "last_clean_begin": 11,
        "last_clean_end": 15,
        "in": 1,
        "public_addr": "127.0.0.1:6809/4723",
        "up_thru": 19,
        "heartbeat_back_addrs": {
          "addrvec": [
            {
              "nonce": 4723,
              "type": "legacy",
              "addr": "127.0.0.1:6812"
            }
          ]
        },
        "cluster_addr": "127.0.0.1:6810/4723",
        "osd": 2,
        "uuid": "178b1a4e-1f8d-454e-b2b4-9fccc25e047e"
      }
    ],
    "epoch": 21,
    "require_min_compat_client": "jewel",
    "crush_version": 7,
    "primary_temp": [],
    "pool_max": 2,
    "max_osd": 3,
    "require_osd_release": "nautilus",
    "min_compat_client": "jewel",
    "osd_xinfo": [
      {
        "laggy_probability": 0.0,
        "laggy_interval": 0,
        "features": 4611087854031142911,
        "old_weight": 0,
        "down_stamp": "2018-09-21 10:58:51.931192",
        "osd": 0
      },
      {
        "laggy_probability": 0.0,
        "laggy_interval": 0,
        "features": 4611087854031142911,
        "old_weight": 0,
        "down_stamp": "2018-09-21 10:58:54.178595",
        "osd": 1
      },
      {
        "laggy_probability": 0.0,
        "laggy_interval": 0,
        "features": 4611087854031142911,
        "old_weight": 0,
        "down_stamp": "2018-09-21 10:58:55.191632",
        "osd": 2
      }
    ],
    "blacklist": {
      "127.0.0.1:6815/347750185": "2018-09-22 10:58:55.672857"
    },
    "last_up_change": "2018-09-21 10:58:55.510104",
    "flags_set": [
      "purged_snapdirs",
      "recovery_deletes",
      "sortbitwise"
    ],
    "fsid": "d02162fd-bee9-4cb5-973b-2f7b6d97102a",
    "flags_num": 1605632,
    "created": "2018-09-21 10:41:55.238114",
    "modified": "2018-09-21 10:58:55.672887",
    "flags": "sortbitwise,recovery_deletes,purged_snapdirs",
    "pg_upmap_items": [],
    "pools": [
      {
        "cache_target_full_ratio_micro": 800000,
        "fast_read": false,
        "stripe_width": 0,
        "flags_names": "hashpspool",
        "tier_of": -1,
        "hit_set_grade_decay_rate": 0,
        "pg_placement_num": 8,
        "use_gmt_hitset": true,
        "last_force_op_resend_preluminous": "0",
        "create_time": "2018-09-21 10:42:28.846328",
        "quota_max_bytes": 0,
        "erasure_code_profile": "",
        "snap_seq": 0,
        "expected_num_objects": 0,
        "size": 3,
        "pg_num_pending": 8,
        "auid": 0,
        "cache_min_flush_age": 0,
        "hit_set_period": 0,
        "min_read_recency_for_promote": 0,
        "target_max_objects": 0,
        "pg_placement_num_target": 8,
        "pg_num": 8,
        "type": 1,
        "pg_num_pending_dec_epoch": 12,
        "grade_table": [],
        "pool_name": "cephfs_data_a",
        "cache_min_evict_age": 0,
        "snap_mode": "selfmanaged",
        "pg_num_target": 8,
        "cache_mode": "none",
        "min_size": 1,
        "cache_target_dirty_high_ratio_micro": 600000,
        "object_hash": 2,
        "application_metadata": {
          "cephfs": {
            "data": "cephfs_a"
          }
        },
        "write_tier": -1,
        "cache_target_dirty_ratio_micro": 400000,
        "pool": 1,
        "removed_snaps": "[]",
        "crush_rule": 0,
        "tiers": [],
        "hit_set_params": {
          "type": "none"
        },
        "last_force_op_resend": "0",
        "pool_snaps": [],
        "quota_max_objects": 0,
        "last_force_op_resend_prenautilus": "0",
        "options": {},
        "hit_set_count": 0,
        "flags": 1,
        "target_max_bytes": 0,
        "snap_epoch": 0,
        "hit_set_search_last_n": 0,
        "last_change": "14",
        "min_write_recency_for_promote": 0,
        "read_tier": -1
      },
      {
        "cache_target_full_ratio_micro": 800000,
        "fast_read": false,
        "stripe_width": 0,
        "flags_names": "hashpspool",
        "tier_of": -1,
        "hit_set_grade_decay_rate": 0,
        "pg_placement_num": 8,
        "use_gmt_hitset": true,
        "last_force_op_resend_preluminous": "0",
        "create_time": "2018-09-21 10:42:29.266816",
        "quota_max_bytes": 0,
        "erasure_code_profile": "",
        "snap_seq": 0,
        "expected_num_objects": 0,
        "size": 3,
        "pg_num_pending": 8,
        "auid": 0,
        "cache_min_flush_age": 0,
        "hit_set_period": 0,
        "min_read_recency_for_promote": 0,
        "target_max_objects": 0,
        "pg_placement_num_target": 8,
        "pg_num": 8,
        "type": 1,
        "pg_num_pending_dec_epoch": 13,
        "grade_table": [],
        "pool_name": "cephfs_metadata_a",
        "cache_min_evict_age": 0,
        "snap_mode": "selfmanaged",
        "pg_num_target": 8,
        "cache_mode": "none",
        "min_size": 1,
        "cache_target_dirty_high_ratio_micro": 600000,
        "object_hash": 2,
        "application_metadata": {
          "cephfs": {
            "metadata": "cephfs_a"
          }
        },
        "write_tier": -1,
        "cache_target_dirty_ratio_micro": 400000,
        "pool": 2,
        "removed_snaps": "[]",
        "crush_rule": 0,
        "tiers": [],
        "hit_set_params": {
          "type": "none"
        },
        "last_force_op_resend": "0",
        "pool_snaps": [],
        "quota_max_objects": 0,
        "last_force_op_resend_prenautilus": "0",
        "options": {},
        "hit_set_count": 0,
        "flags": 1,
        "target_max_bytes": 0,
        "snap_epoch": 0,
        "hit_set_search_last_n": 0,
        "last_change": "15",
        "min_write_recency_for_promote": 0,
        "read_tier": -1
      }
    ],
    "new_removed_snaps": [],
    "removed_snaps_queue": []
  },
  "fs_map": {
    "compat": {
      "compat": {},
      "ro_compat": {},
      "incompat": {
        "feature_10": "snaprealm v2",
        "feature_8": "no anchor table",
        "feature_9": "file layout v2",
        "feature_2": "client writeable ranges",
        "feature_3": "default file layouts on dirs",
        "feature_1": "base v0.20",
        "feature_6": "dirfrag is stored in omap",
        "feature_4": "dir inode in separate object",
        "feature_5": "mds uses versioned encoding"
      }
    },
    "feature_flags": {
      "ever_enabled_multiple": false,
      "enable_multiple": false
    },
    "default_fscid": 1,
    "filesystems": [
      {
        "id": 1,
        "mdsmap": {
          "session_autoclose": 300,
          "balancer": "",
          "modified": "2018-09-21 10:58:59.856070",
          "last_failure_osd_epoch": 21,
          "in": [
            0
          ],
          "last_failure": 0,
          "max_file_size": 1099511627776,
          "explicitly_allowed_features": 0,
          "damaged": [],
          "tableserver": 0,
          "failed": [],
          "metadata_pool": 2,
          "epoch": 11,
          "flags": 18,
          "max_mds": 1,
          "compat": {
            "compat": {},
            "ro_compat": {},
            "incompat": {
              "feature_10": "snaprealm v2",
              "feature_8": "no anchor table",
              "feature_9": "file layout v2",
              "feature_2": "client writeable ranges",
              "feature_3": "default file layouts on dirs",
              "feature_1": "base v0.20",
              "feature_6": "dirfrag is stored in omap",
              "feature_4": "dir inode in separate object",
              "feature_5": "mds uses versioned encoding"
            }
          },
          "min_compat_client": "-1 (unspecified)",
          "data_pools": [
            1
          ],
          "info": {
            "gid_34136": {
              "standby_for_rank": -1,
              "addr": "127.0.0.1:6814/2139526630",
              "export_targets": [],
              "name": "b",
              "incarnation": 8,
              "state": "up:active",
              "state_seq": 4,
              "standby_for_fscid": -1,
              "standby_replay": false,
              "gid": 34136,
              "features": 4611087854031142911,
              "rank": 0,
              "standby_for_name": "",
              "addrs": {
                "addrvec": [
                  {
                    "nonce": 2139526630,
                    "type": "legacy",
                    "addr": "127.0.0.1:6814"
                  }
                ]
              }
            }
          },
          "fs_name": "cephfs_a",
          "created": "2018-09-21 10:42:30.305761",
          "standby_count_wanted": 1,
          "enabled": true,
          "up": {
            "mds_0": 34136
          },
          "session_timeout": 60,
          "stopped": [],
          "ever_allowed_features": 0,
          "root": 0
        }
      }
    ],
    "epoch": 11,
    "standbys": [
      {
        "standby_for_rank": -1,
        "addr": "127.0.0.1:6815/1585121408",
        "export_targets": [],
        "name": "c",
        "state": "up:standby",
        "incarnation": 0,
        "epoch": 7,
        "state_seq": 1,
        "standby_for_fscid": -1,
        "standby_replay": false,
        "gid": 34116,
        "features": 4611087854031142911,
        "rank": -1,
        "standby_for_name": "",
        "addrs": {
          "addrvec": [
            {
              "nonce": 1585121408,
              "type": "legacy",
              "addr": "127.0.0.1:6815"
            }
          ]
        }
      },
      {
        "standby_for_rank": -1,
        "addr": "127.0.0.1:6813/3705009905",
        "export_targets": [],
        "name": "a",
        "state": "up:standby",
        "incarnation": 0,
        "epoch": 7,
        "state_seq": 1,
        "standby_for_fscid": -1,
        "standby_replay": false,
        "gid": 34123,
        "features": 4611087854031142911,
        "rank": -1,
        "standby_for_name": "",
        "addrs": {
          "addrvec": [
            {
              "nonce": 3705009905,
              "type": "legacy",
              "addr": "127.0.0.1:6813"
            }
          ]
        }
      }
    ]
  },
  "version": {
    "release": 14,
    "major": 0,
    "full": "ceph version 14.0.0-3517-g5322f99370 (5322f99370d629f6927b9c948522a003fc5da5bb) nautilus (dev)",
    "minor": 0
  },
  "health": {
    "current": {
      "status": "HEALTH_WARN",
      "checks": {
        "PG_AVAILABILITY": {
          "detail": [
            {
              "message": "pg 1.0 is stuck peering for 990.119101, current state peering, last acting [1,0,2]"
            },
            {
              "message": "pg 1.1 is stuck peering for 990.111854, current state peering, last acting [2,0,1]"
            },
            {
              "message": "pg 1.2 is stuck peering for 990.119186, current state peering, last acting [0,2]"
            },
            {
              "message": "pg 1.3 is stuck peering for 990.118224, current state peering, last acting [1,2,0]"
            },
            {
              "message": "pg 1.4 is stuck peering for 990.119116, current state peering, last acting [1,0,2]"
            },
            {
              "message": "pg 1.5 is stuck peering for 990.111987, current state peering, last acting [2,0,1]"
            },
            {
              "message": "pg 1.6 is stuck peering for 990.118940, current state peering, last acting [1,0,2]"
            },
            {
              "message": "pg 1.7 is stuck peering for 990.117449, current state peering, last acting [1,2,0]"
            },
            {
              "message": "pg 2.0 is stuck peering for 989.765896, current state peering, last acting [2,1,0]"
            },
            {
              "message": "pg 2.1 is stuck peering for 989.768816, current state peering, last acting [2,1,0]"
            },
            {
              "message": "pg 2.2 is stuck peering for 989.765611, current state peering, last acting [0,2]"
            },
            {
              "message": "pg 2.3 is stuck peering for 989.768059, current state peering, last acting [1,2,0]"
            },
            {
              "message": "pg 2.4 is stuck peering for 989.750743, current state peering, last acting [1,0,2]"
            },
            {
              "message": "pg 2.5 is stuck peering for 989.768270, current state peering, last acting [1,0,2]"
            },
            {
              "message": "pg 2.6 is stuck peering for 988.783800, current state peering, last acting [0,2]"
            },
            {
              "message": "pg 2.7 is stuck peering for 989.768669, current state peering, last acting [1,0,2]"
            }
          ],
          "severity": "HEALTH_WARN",
          "summary": {
            "message": "Reduced data availability: 16 pgs peering"
          }
        }
      }
    },
    "history": {
      "checks": {
        "OSD_DOWN": {
          "HEALTH_WARN": {
            "detail": [
              "osd.1 (root=default,host=daq) is down",
              "osd.2 (root=default,host=daq) is down"
            ],
            "summary": [
              "1 osds down"
            ]
          }
        },
        "PG_AVAILABILITY": {
          "HEALTH_WARN": {
            "detail": [
              "pg 1.3 is stuck peering for 986.117085, current state peering, last acting [1,2,0]",
              "pg 1.5 is stuck peering for 988.111424, current state peering, last acting [2,0,1]",
              "pg 2.5 is stuck peering for 989.768270, current state peering, last acting [1,0,2]",
              "pg 1.7 is stuck peering for 990.117449, current state peering, last acting [1,2,0]",
              "pg 2.2 is stuck peering for 985.764472, current state peering, last acting [0,2]",
              "pg 1.2 is stuck peering for 988.118624, current state peering, last acting [0,2]",
              "pg 2.6 is stuck peering for 986.783237, current state peering, last acting [0,2]",
              "pg 2.6 is stuck peering for 988.783800, current state peering, last acting [0,2]",
              "pg 1.5 is stuck peering for 990.111987, current state peering, last acting [2,0,1]",
              "pg 1.5 is stuck peering for 986.110848, current state peering, last acting [2,0,1]",
              "pg 2.1 is stuck peering for 989.768816, current state peering, last acting [2,1,0]",
              "pg 1.7 is stuck peering for 986.116310, current state peering, last acting [1,2,0]",
              "pg 2.3 is stuck peering for 985.766920, current state peering, last acting [1,2,0]",
              "pg 2.5 is stuck peering for 987.767707, current state peering, last acting [1,0,2]",
              "pg 1.1 is stuck peering for 990.111854, current state peering, last acting [2,0,1]",
              "pg 2.7 is stuck peering for 985.767530, current state peering, last acting [1,0,2]",
              "pg 2.0 is stuck peering for 985.764757, current state peering, last acting [2,1,0]",
              "pg 2.1 is stuck peering for 987.768253, current state peering, last acting [2,1,0]",
              "pg 2.0 is stuck peering for 989.765896, current state peering, last acting [2,1,0]",
              "pg 1.2 is stuck peering for 990.119186, current state peering, last acting [0,2]",
              "pg 2.6 is stuck peering for 984.782661, current state peering, last acting [0,2]",
              "pg 2.7 is stuck peering for 987.768106, current state peering, last acting [1,0,2]",
              "pg 1.2 is stuck peering for 986.118047, current state peering, last acting [0,2]",
              "pg 2.4 is stuck peering for 987.750181, current state peering, last acting [1,0,2]",
              "pg 1.6 is stuck peering for 986.117801, current state peering, last acting [1,0,2]",
              "pg 1.6 is stuck peering for 988.118377, current state peering, last acting [1,0,2]",
              "pg 2.3 is stuck peering for 987.767497, current state peering, last acting [1,2,0]",
              "pg 2.2 is stuck peering for 987.765049, current state peering, last acting [0,2]",
              "pg 1.0 is stuck peering for 986.117962, current state peering, last acting [1,0,2]",
              "pg 1.4 is stuck peering for 988.118553, current state peering, last acting [1,0,2]",
              "pg 2.5 is stuck peering for 985.767131, current state peering, last acting [1,0,2]",
              "pg 1.0 is stuck peering for 990.119101, current state peering, last acting [1,0,2]",
              "pg 1.0 is stuck peering for 988.118539, current state peering, last acting [1,0,2]",
              "pg 2.4 is stuck peering for 985.749604, current state peering, last acting [1,0,2]",
              "pg 2.3 is stuck peering for 989.768059, current state peering, last acting [1,2,0]",
              "pg 2.2 is stuck peering for 989.765611, current state peering, last acting [0,2]",
              "pg 2.4 is stuck peering for 989.750743, current state peering, last acting [1,0,2]",
              "pg 2.0 is stuck peering for 987.765334, current state peering, last acting [2,1,0]",
              "pg 1.7 is stuck peering for 988.116886, current state peering, last acting [1,2,0]",
              "pg 1.4 is stuck peering for 986.117976, current state peering, last acting [1,0,2]",
              "pg 1.3 is stuck peering for 990.118224, current state peering, last acting [1,2,0]",
              "pg 2.7 is stuck peering for 989.768669, current state peering, last acting [1,0,2]",
              "pg 1.1 is stuck peering for 988.111291, current state peering, last acting [2,0,1]",
              "pg 1.1 is stuck peering for 986.110715, current state peering, last acting [2,0,1]",
              "pg 1.3 is stuck peering for 988.117661, current state peering, last acting [1,2,0]",
              "pg 1.4 is stuck peering for 990.119116, current state peering, last acting [1,0,2]",
              "pg 1.6 is stuck peering for 990.118940, current state peering, last acting [1,0,2]",
              "pg 2.1 is stuck peering for 985.767677, current state peering, last acting [2,1,0]"
            ],
            "summary": [
              "Reduced data availability: 16 pgs peering"
            ]
          }
        },
        "FS_DEGRADED": {
          "HEALTH_WARN": {
            "detail": [
              "fs cephfs_a is degraded"
            ],
            "summary": [
              "1 filesystem is degraded"
            ]
          }
        },
        "MDS_ALL_DOWN": {
          "HEALTH_ERR": {
            "detail": [
              "fs cephfs_a is offline because no MDS is active for it."
            ],
            "summary": [
              "1 filesystem is offline"
            ]
          }
        }
      }
    }
  },
  "manager_map": {
    "available": true,
    "active_change": "2018-09-21 10:58:50.982610",
    "available_modules": [
      {
        "name": "dashboard",
        "error_string": "No module named rbd",
        "can_run": false
      },
      {
        "name": "diskprediction",
        "error_string": "No module named rbd",
        "can_run": false
      },
      {
        "name": "hello",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "influx",
        "error_string": "influxdb python module not found",
        "can_run": false
      },
      {
        "name": "insights",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "iostat",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "localpool",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "orchestrator_cli",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "progress",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "prometheus",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "restful",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "rook",
        "error_string": "Kubernetes module not found",
        "can_run": false
      },
      {
        "name": "selftest",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "smart",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "telegraf",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "telemetry",
        "error_string": "",
        "can_run": true
      },
      {
        "name": "zabbix",
        "error_string": "",
        "can_run": true
      }
    ],
    "modules": [
      "balancer",
      "devicehealth",
      "insights",
      "iostat",
      "restful",
      "status"
    ],
    "active_name": "x",
    "epoch": 10,
    "standbys": [],
    "active_addrs": {
      "addrvec": [
        {
          "nonce": 4254,
          "type": "legacy",
          "addr": "127.0.0.1:6808"
        }
      ]
    },
    "services": {
      "restful": "https://daq:42226/"
    },
    "active_gid": 34106
  },
  "errors": [],
  "mon_map": {
    "features": {
      "optional": [],
      "persistent": [
        "kraken",
        "luminous",
        "mimic",
        "osdmap-prune",
        "nautilus"
      ]
    },
    "created": "2018-09-21 10:41:49.406653",
    "modified": "2018-09-21 10:41:49.406653",
    "epoch": 1,
    "mons": [
      {
        "public_addr": "127.0.0.1:40226/0",
        "name": "a",
        "rank": 0,
        "addr": "127.0.0.1:40226/0"
      },
      {
        "public_addr": "127.0.0.1:40227/0",
        "name": "b",
        "rank": 1,
        "addr": "127.0.0.1:40227/0"
      },
      {
        "public_addr": "127.0.0.1:40228/0",
        "name": "c",
        "rank": 2,
        "addr": "127.0.0.1:40228/0"
      }
    ],
    "fsid": "d02162fd-bee9-4cb5-973b-2f7b6d97102a"
  },
  "config": [
    {
      "name": "mon_pg_warn_min_per_osd",
      "level": "advanced",
      "section": "global",
      "mask": "",
      "value": "3",
      "can_update_at_runtime": true
    },
    {
      "name": "osd_pool_default_min_size",
      "level": "advanced",
      "section": "global",
      "mask": "",
      "value": "1",
      "can_update_at_runtime": true
    },
    {
      "name": "osd_pool_default_size",
      "level": "advanced",
      "section": "global",
      "mask": "",
      "value": "3",
      "can_update_at_runtime": true
    },
    {
      "name": "mon_allow_pool_delete",
      "level": "advanced",
      "section": "mon",
      "mask": "",
      "value": "true",
      "can_update_at_runtime": true
    },
    {
      "name": "mon_data_avail_crit",
      "level": "advanced",
      "section": "mon",
      "mask": "",
      "value": "1",
      "can_update_at_runtime": true
    },
    {
      "name": "mon_data_avail_warn",
      "level": "advanced",
      "section": "mon",
      "mask": "",
      "value": "2",
      "can_update_at_runtime": true
    },
    {
      "name": "mon_osd_reporter_subtree_level",
      "level": "advanced",
      "section": "mon",
      "mask": "",
      "value": "osd",
      "can_update_at_runtime": true
    },
    {
      "name": "mgr/restful/x/server_port",
      "level": "unknown",
      "section": "mgr",
      "mask": "",
      "value": "42226",
      "can_update_at_runtime": false
    },
    {
      "name": "osd_copyfrom_max_chunk",
      "level": "advanced",
      "section": "osd",
      "mask": "",
      "value": "524288",
      "can_update_at_runtime": true
    },
    {
      "name": "osd_debug_misdirected_ops",
      "level": "dev",
      "section": "osd",
      "mask": "",
      "value": "true",
      "can_update_at_runtime": true
    },
    {
      "name": "osd_debug_op_order",
      "level": "dev",
      "section": "osd",
      "mask": "",
      "value": "true",
      "can_update_at_runtime": true
    },
    {
      "name": "osd_scrub_load_threshold",
      "level": "advanced",
      "section": "osd",
      "mask": "",
      "value": "2000.000000",
      "can_update_at_runtime": true
    },
    {
      "name": "mds_debug_auth_pins",
      "level": "dev",
      "section": "mds",
      "mask": "",
      "value": "true",
      "can_update_at_runtime": true
    },
    {
      "name": "mds_debug_frag",
      "level": "dev",
      "section": "mds",
      "mask": "",
      "value": "true",
      "can_update_at_runtime": true
    },
    {
      "name": "mds_debug_subtrees",
      "level": "dev",
      "section": "mds",
      "mask": "",
      "value": "true",
      "can_update_at_runtime": true
    }
  ]
}
"""

DEV_TEST_DATA = """
*** DEVELOPER MODE: setting PATH, PYTHONPATH and LD_LIBRARY_PATH ***
2018-09-26 11:32:02.830 7f39e866c700 -1 WARNING: all dangerous and experimental features are enabled.
2018-09-26 11:32:02.879 7f39e866c700 -1 WARNING: all dangerous and experimental features are enabled.
""" + TEST_DATA


def test_ceph_insights():
    for content in (TEST_DATA, DEV_TEST_DATA):
        ceph = CephInsights(context_wrap(content))

        assert ceph is not None

        assert isinstance(ceph.version, dict)
        assert isinstance(ceph.version["full"], six.string_types)
        for key in ("release", "major", "minor"):
            assert isinstance(ceph.version[key], int)

        assert isinstance(ceph.data["crashes"], dict)
        assert isinstance(ceph.data["health"], dict)
        assert isinstance(ceph.data["config"], list)
        assert isinstance(ceph.data["osd_dump"], dict)
        assert isinstance(ceph.data["df"], dict)
        assert isinstance(ceph.data["osd_tree"], dict)
        assert isinstance(ceph.data["fs_map"], dict)
        assert isinstance(ceph.data["crush_map"], dict)
        assert isinstance(ceph.data["mon_map"], dict)
        assert isinstance(ceph.data["service_map"], dict)
        assert isinstance(ceph.data["manager_map"], dict)
        assert isinstance(ceph.data["mon_status"], dict)
        assert isinstance(ceph.data["pg_summary"], dict)
        assert isinstance(ceph.data["osd_metadata"], dict)
        assert isinstance(ceph.data["version"], dict)
        assert isinstance(ceph.data["errors"], list)


def test_ceph_insights_documentation():
    env = {
        'ceph_insights': CephInsights(context_wrap(TEST_DATA))
    }
    failed, total = doctest.testmod(ceph_insights, globs=env)
    assert failed == 0
