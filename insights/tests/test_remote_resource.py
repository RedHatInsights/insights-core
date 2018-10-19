from insights.core import RemoteResource, CachedRemoteResource
from insights.tests.mock_web_server import TestMockServer

GOOD_PAYLOAD = b'{"data":{"id": "001", "name": "Successful return from Mock Service"}}'
NOT_FOUND = b'{"error":{"code": "404", "message": "Not Found"}}'


class TestRemoteResource(TestMockServer):

    # Test RemoteResource
    def test_get_remote_resource(self):
        rr = RemoteResource()

        url = 'http://localhost:{port}/mock/'.format(port=self.server_port)
        rtn = rr.get(url)
        assert rtn.content == GOOD_PAYLOAD

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
        assert rtn.content == GOOD_PAYLOAD

    # Test CachedRemoteResource not found
    def test_get_cachedremoteResource_not_found(self):
        crr = CachedRemoteResource()

        url = 'http://localhost:{port}/moc/'.format(port=self.server_port)
        rtn = crr.get(url)
        assert rtn.content == NOT_FOUND
