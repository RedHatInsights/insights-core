from insights.client import InsightsClient

InsightsClient().upload(
    payload='test.tar.gz',
    content_type='application/vnd.redhat.advisor.test+tgz')
