
import pickle
import os


class CacheItem(object):
    def __init__(self, etag, content):
        self.etag = etag
        self.content = content


class URLCache(object):
    def __init__(self, path=None):
        '''
            Initialize a URLCache, loading entries from @path, if provided.
        '''
        self._path = path
        self._cache = {}
        if os.path.isfile(self._path):
            with open(self._path, "r+b") as f:
                self._cache = pickle.load(f)
        os.makedirs(os.path.dirname(self._path), exist_ok=True)

    def get(self, url):
        try:
            return self._cache[url]
        except KeyError:
            return None

    def set(self, url, etag, content):
        self._cache[url] = CacheItem(etag, content)

    def save(self):
        with open(self._path, "w+b") as f:
            pickle.dump(self._cache, f)
