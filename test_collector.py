from insights.client.collection_rules import InsightsConfig
from insights.client.data_collector import DataCollector
import logging

logging.basicConfig()
logging.root.level = logging.INFO

BRANCH_INFO = {"remote_branch": -1, "remote_leaf": -1}

config = InsightsConfig()
config.collection_rules_file = "/home/klape/insights/frontend-assets/uploader.json"
config.gpg = False
uploader_json, rm_conf = config.get_conf(False)

dc = DataCollector()
dc.run_collection(uploader_json, rm_conf, BRANCH_INFO)
