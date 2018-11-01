from insights.core.remote_resource import RemoteResource, CachedRemoteResource
from insights.tests.mock_web_server import TestMockServer

GOOD_PAYLOAD = b'Successful return from Mock Service'
NOT_FOUND = b'{"error":{"code": "404", "message": "Not Found"}}'


class TestRemoteResource(TestMockServer):

    # Test RemoteResource
    def test_get_remote_resource(self):
        rr = RemoteResource()

        url = 'http://localhost:{port}/mock/'.format(port=self.server_port)
        rtn = rr.get(url)
        assert GOOD_PAYLOAD in rtn.content

    # Test RemoteResource not found
    def test_get_remoteResource_not_found(self):
        rr = RemoteResource()

        url = 'http://localhost:{port}/moc/'.format(port=self.server_port)
        rtn = rr.get(url)
        assert rtn.content == NOT_FOUND

    # Test CachedRemoteResource
    def test_get_cachedremote_resource(self):
        crr = CachedRemoteResource()

        url = 'http://localhost:{port}/mock/'.format(port=self.server_port)
        rtn = crr.get(url)
        assert GOOD_PAYLOAD in rtn.content

    # Test CachedRemoteResource returns cached response
    def test_get_cachedremote_resource_cached(self):
        crr = CachedRemoteResource()

        url = 'http://localhost:{port}/mock/'.format(port=self.server_port)
        rtn = crr.get(url)
        cont_1 = rtn.content
        rtn = crr.get(url)
        cont_2 = rtn.content
        assert cont_1 == cont_2

    # Test CachedRemoteResource not found
    def test_get_cachedremoteResource_not_found(self):
        crr = CachedRemoteResource()

        url = 'http://localhost:{port}/moc/'.format(port=self.server_port)
        rtn = crr.get(url)
        assert rtn.content == NOT_FOUND
