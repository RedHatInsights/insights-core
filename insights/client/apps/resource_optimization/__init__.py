from insights.client.archive import InsightsArchive
from insights.client.utilities import determine_hostname
from datetime import date, timedelta
import subprocess
import json


ROS_CONTENT_TYPE = 'application/vnd.redhat.resource-optimization.something+tgz'


class RosClient:
    def __init__(self, config):
        hostname = determine_hostname()
        log_date = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
        self.archive = InsightsArchive(config)
        self.commands = [
            {
                'cmd': f"pmlogsummary /var/log/pcp/pmlogger/{hostname}/{log_date}.index mem.util.used",
                'metric': 'avg_memory_used'
            },
            {
                'cmd': f"pmlogsummary /var/log/pcp/pmlogger/{hostname}/{log_date}.index mem.physmem",
                'metric': 'avg_memory'
            }
        ]

    def collect_metrics(self):
        data = {}
        tmpfile = '/var/tmp/metrics.json'
        for command in self.commands:
            p1 = subprocess.run(command['cmd'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            data[command['metric']] = p1.stdout.decode().split()[1]

        with open(tmpfile, 'w') as f:
            json.dump(data, f)

        self.archive.copy_file(tmpfile)
        return self.archive.create_tar_file(), ROS_CONTENT_TYPE
