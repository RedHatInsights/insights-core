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

from insights.parsers.rhv_log_collector_analyzer import RhvLogCollectorJson
from insights.tests import context_wrap

RHV_ANALYZER_JSON = """
{
    "hostname": "localhost.localdomain.localdomain",
    "rhv-log-collector-analyzer": [
        {
            "bugzilla": "",
            "description": "Found Cluster(s) using Legacy Migration Policy It is recommended to update the Migration Policy. Please visit: https://access.redhat.com/solutions/3143541",
            "file": "cluster_query_migration_policy_check_legacy.sql",
            "hash": "fb908a5befb8bedd2c87d8d7fcd6f305",
            "id": "67cd9967367beb3e7431a4e5b1970efc4914007af95735de40c2298ea6f18f19",
            "id_host": "08985ce25cee4dcd8a2e56cebc3574ad",
            "kb": "https://access.redhat.com/solutions/3143541",
            "name": "check_legacy_policy",
            "path": "/usr/share/rhv-log-collector-analyzer/analyzer/produceReport/sqls/cluster_query_migration_policy_check_legacy.sql",
            "result": [
                [
                    {
                        "Cluster": "fccl",
                        "Data Center": "fcdc",
                        "NO.": 1
                    }
                ],
                [
                    {
                        "Cluster": "larry",
                        "Data Center": "Default",
                        "NO.": 2
                    }
                ],
                [
                    {
                        "Cluster": "larry",
                        "Data Center": "lo-dc",
                        "NO.": 3
                    }
                ],
                [
                    {
                        "Cluster": "larry",
                        "Data Center": "fcdc",
                        "NO.": 4
                    }
                ],
                [
                    {
                        "Cluster": "larry",
                        "Data Center": "larry",
                        "NO.": 5
                    }
                ],
                [
                    {
                        "Cluster": "lo-cl",
                        "Data Center": "lo-dc",
                        "NO.": 6
                    }
                ]
            ],
            "time": "0.0137791633606",
            "type": "WARNING",
            "when": "2018-06-27 00:19:14"
        }
   ]
}
""".strip()


class TestRhvLogCollectorJson():
    def test_rhv_log_collector_json(self):
        result = RhvLogCollectorJson(context_wrap(RHV_ANALYZER_JSON))

        assert result.data == {
            "hostname": "localhost.localdomain.localdomain",
            "rhv-log-collector-analyzer": [
                {
                    "bugzilla": "",
                    "description": "Found Cluster(s) using Legacy Migration Policy It is recommended to update the Migration Policy. Please visit: https://access.redhat.com/solutions/3143541",
                    "file": "cluster_query_migration_policy_check_legacy.sql",
                    "hash": "fb908a5befb8bedd2c87d8d7fcd6f305",
                    "id": "67cd9967367beb3e7431a4e5b1970efc4914007af95735de40c2298ea6f18f19",
                    "id_host": "08985ce25cee4dcd8a2e56cebc3574ad",
                    "kb": "https://access.redhat.com/solutions/3143541",
                    "name": "check_legacy_policy",
                    "path": "/usr/share/rhv-log-collector-analyzer/analyzer/produceReport/sqls/cluster_query_migration_policy_check_legacy.sql",
                    "result": [
                        [
                            {
                                "Cluster": "fccl",
                                "Data Center": "fcdc",
                                "NO.": 1
                            }
                        ],
                        [
                            {
                                "Cluster": "larry",
                                "Data Center": "Default",
                                "NO.": 2
                            }
                        ],
                        [
                            {
                                "Cluster": "larry",
                                "Data Center": "lo-dc",
                                "NO.": 3
                            }
                        ],
                        [
                            {
                                "Cluster": "larry",
                                "Data Center": "fcdc",
                                "NO.": 4
                            }
                        ],
                        [
                            {
                                "Cluster": "larry",
                                "Data Center": "larry",
                                "NO.": 5
                            }
                        ],
                        [
                            {
                                "Cluster": "lo-cl",
                                "Data Center": "lo-dc",
                                "NO.": 6
                            }
                        ]
                    ],
                    "time": "0.0137791633606",
                    "type": "WARNING",
                    "when": "2018-06-27 00:19:14"
                }
            ]
        }
        assert result['rhv-log-collector-analyzer'][0]['file'] == 'cluster_query_migration_policy_check_legacy.sql'
