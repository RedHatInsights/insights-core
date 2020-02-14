import os
import pickle
import time

_KEEPTIME = 300  # 5 minutes


class CacheItem(object):
    def __init__(self, etag, content, cached_at):
        self.etag = etag
        self.content = content
        self.cached_at = cached_at


class URLCache(object):
    """
        URLCache is a simple pickle cache, intended to be used as an HTTP
        response cache.
    """
    def __init__(self, path=None):
        """
            Initialize a URLCache, loading entries from @path, if provided.
        """
        self._path = path
        self._cache = {}
        if os.path.isfile(self._path):
            with open(self._path, "r+b") as f:
                try:
                    self._cache = pickle.load(f)
                except EOFError:
                    self._cache = {}
        if not os.path.exists(os.path.dirname(self._path)):
            os.makedirs(os.path.dirname(self._path))

    def get(self, url):
        try:
            item = self._cache[url]
            if item.cached_at + _KEEPTIME <= time.time():
                del (self._cache, url)
                return None
            return self._cache[url]
        except KeyError:
            return None

    def set(self, url, etag, content):
        self._cache[url] = CacheItem(etag, content, time.time())

    def save(self):
        with open(self._path, "w+b") as f:
            pickle.dump(self._cache, f)
