import sys
import time
import pytest
from cachecontrol.cache import DictCache
from insights.core.remote_resource import RemoteResource, CachedRemoteResource
from insights.tests.mock_web_server import TestMockServer

GOOD_PAYLOAD = b'Successful return from Mock Service'
NOT_FOUND = b'{"error":{"code": "404", "message": "Not Found"}}'


class TestRemoteResource(TestMockServer):

    # Test CachedRemoteResource returns cached response with specified expire_after
    # - To avoid the `expire_after` is set to the default 180 seconds, this case
    #   should be tested at first
    @pytest.mark.skipif(sys.version_info < (2, 7), reason="CacheControl requires python 2.7 or higher")
    def test_get_cached_remote_resource_cached_expire_after(self):
        url = 'http://localhost:{port}/mock/'.format(port=self.server_port)
        crr = CachedRemoteResource(expire_after=1)
        rtn = crr.get(url)
        exp_1 = rtn.headers['expires']
        time.sleep(2)
        rtn = crr.get(url)
        exp_2 = rtn.headers['expires']
        assert exp_1 != exp_2

        crr = CachedRemoteResource(expire_after=10)
        # Refresh the cache
        crr.get(url)
        time.sleep(1)
        # Use the new expire_after
        rtn = crr.get(url)
        exp_1 = rtn.headers['expires']
        time.sleep(1)
        rtn = crr.get(url)
        exp_2 = rtn.headers['expires']
        assert exp_1 == exp_2

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

    # Test CachedRemoteResource not cached
    def test_get_cached_remote_resource(self):
        crr = CachedRemoteResource()

        url = 'http://localhost:{port}/mock/'.format(port=self.server_port)
        rtn = crr.get(url)
        assert GOOD_PAYLOAD in rtn.content

    # Test CachedRemoteResource returns cached response
    @pytest.mark.skipif(sys.version_info < (2, 7), reason="CacheControl requires python 2.7 or higher")
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
