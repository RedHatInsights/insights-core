from mock.mock import patch
from cachecontrol.cache import DictCache
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
    def test_get_remote_resource_not_found(self):
        rr = RemoteResource()

        url = 'http://localhost:{port}/moc/'.format(port=self.server_port)
        rtn = rr.get(url)
        assert rtn.content == NOT_FOUND

    # Test disable RemoteResource
    @patch('insights.core.remote_resource.RemoteResource.allow_remote_resource_access', new=False)
    def test_get_disable_remote_resource(self):
        try:
            rr = RemoteResource()
            url = 'http://localhost:{port}/moc/'.format(port=self.server_port)
            rr.get(url)
            raise AssertionError("Expected code to be unreachable")
        except Exception as e:
            assert str(e) == "Remote resource access is disabled"

    # Test CachedRemoteResource not cached
    def test_get_cached_remote_resource(self):
        crr = CachedRemoteResource()

        url = 'http://localhost:{port}/mock/'.format(port=self.server_port)
        rtn = crr.get(url)
        assert GOOD_PAYLOAD in rtn.content

    # Test CachedRemoteResource returns cached response
    def test_get_cached_remote_resource_cached(self):
        crr = CachedRemoteResource()

        url = 'http://localhost:{port}/mock/'.format(port=self.server_port)
        rtn = crr.get(url)
        cont_1 = rtn.content
        rtn = crr.get(url)
        cont_2 = rtn.content
        assert cont_1 == cont_2

    # Test CachedRemoteResource not found
    def test_get_cached_remote_resource_not_found(self):
        crr = CachedRemoteResource()

        url = 'http://localhost:{port}/moc/'.format(port=self.server_port)
        rtn = crr.get(url)
        assert rtn.content == NOT_FOUND

    def test_save_dict_cache(self):
        crr = CachedRemoteResource()
        assert crr._cache is not None
        assert isinstance(crr._cache, DictCache)

        crr2 = CachedRemoteResource()
        assert crr2._cache is not None
        assert isinstance(crr2._cache, DictCache)

        assert crr._cache is crr2._cache
