from insights.client import InsightsClient
from insights.client.config import InsightsConfig

config = InsightsConfig(
    payload='test.tar.gz',
    content_type='application/vnd.redhat.advisor.test+tgz',
    upload_url='https://cert-api.access.redhat.com/r/insights/platform/upload/api/v1/upload')
client = InsightsClient(config)
client.upload()
