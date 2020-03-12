import tempfile

from insights.client import url_cache
from mock.mock import patch


def test_url_cache_hit():
    f = tempfile.NamedTemporaryFile()
    c = url_cache.URLCache(path=f.name)
    c.set("http://foo", "abcd", "OK")
    c.save()
    assert c.get("http://foo").content == "OK"


@patch("insights.client.url_cache._KEEPTIME", new=0)
def test_url_cache_miss():
    f = tempfile.NamedTemporaryFile()
    c = url_cache.URLCache(path=f.name)
    c.set("http://foo", "abcd", "OK")
    c.save()
    assert c.get("http://foo") is None
