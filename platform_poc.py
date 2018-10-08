from insights.client import InsightsClient

client = InsightsClient()
client.config.legacy_upload = False
client.upload(
    payload='test.tar.gz',
    content_type='application/vnd.redhat.advisor.test+tgz')
