import requests

import redis
import calendar
from cachecontrol.heuristics import BaseHeuristic
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

from datetime import datetime, timedelta
from email.utils import parsedate, formatdate
from cachecontrol.caches.redis_cache import RedisCache


class RemoteResource(object):
    """
    RemoteResource class for accessing external Web resources.

    Attributes:
        timeout(float): Time in seconds for the requests.get api call to wait before returning a timeout exception

    Examples:
        >>> from insights.core.remote_resource import RemoteResource
        >>> rr = RemoteResource()
        >>> rtn = rr.get("http://google.com")
        >>> print (rtn.content)
    """

    timeout = 10

    def __init__(self, sess=None):

        if not sess:
            self.sess = requests.Session()

    def get(cls, url, params={}, headers={}, auth=(), verify=False):
        """
        Returns the response payload from the request to the given URL.

        Args:
            url (str): The URL for the WEB API that the request is being made too.
            params (dict): Dictionary containing the query string parameters.
            headers (dict): HTTP Headers that may be needed forthe request.
            auth (tuple): User ID and password for Basic Auth
            verify (str/bool): Value must be path to the Cert Bundle if verifying the SSL certificate
             or boolean False to ignore verifying the SSL certificate.

        Returns:
            Response:(Response): Response object from requests.get api request
        """

        resp = cls.sess.get(url, params=params, headers=headers, verify=verify, auth=auth,
                            timeout=cls.timeout)

        return resp


class CachedRemoteResource(RemoteResource):
    """
    RemoteResource subclass that sets up caching for subsequent Web resource requests.

    Attributes:
        expire_after (float): Amount of time in seconds that the cache will expire
        backend (str): Type of storage for cache `DictCache1, `FileCache" or `RedisCache`
        __heuristic (str): Heuristic method name to manage HTTP cache headers.
        session (object): Requests session object

    Examples:
        >>> from insights.core.remote_resource import CachedRemoteResource
        >>> crr = CachedRemoteResource()
        >>> rtn = crr.get("http://google.com")
        >>> print (rtn.content)

    """

    expire_after = 180
    backend = "DictCache"
    __heuristic = 'DefaultHeuristic'
    session = None

    def __init__(self):

        if not self.session:
            self.session = requests.Session()
        hclass = globals()[self.__heuristic]

        if self.backend == "redis":
            pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
            r = redis.Redis(connection_pool=pool)
            self.sess = CacheControl(self.session, heuristic=hclass(self.expire_after), cache=RedisCache(r))

        elif self.backend == "FileCache":
            self.sess = CacheControl(self.session, heuristic=hclass(self.expire_after), cache=FileCache('.web_cache'))
        else:
            self.sess = CacheControl(self.session, heuristic=hclass(self.expire_after))

        super(CachedRemoteResource, self).__init__(self.sess)


class DefaultHeuristic(BaseHeuristic):
    """
    BaseHeuristic subclass that sets the default caching headers if not supplied by the remote service.

    Attributes:
        default_cache_vars (str): Message content warning that the response from the remote server did not
          return proper HTTP cache headers so we will use default cache settings
        server_cache_headers (str): Message content warning that we are using cache settings returned by the
          remote server.
    """

    default_cache_vars = "Remote service caching headers not set correctly, using default caching"
    server_cache_headers = "Caching being done based on caching headers returned by remote service"

    def __init__(self, expire_after):

        self.expire_after = expire_after

    def update_headers(self, response):
        """
        Returns the updated caching headers.

        Args:
            response (HTTPResponse): The response from the remote service

        Returns:
            Response:(HTTPResponse): Http caching headers
        """
        if 'expires' in response.headers and response.headers['expires'] > 0 and \
                'cache-control' in response.headers and response.headers['cache-control'] != 'private':
            self.msg = self.server_cache_headers
            return {
                'expires': response.headers['expires'],
                'cache-control': response.headers['cache-control'],
            }
        else:
            self.msg = self.default_cache_vars
            date = parsedate(response.headers['date'])
            expires = datetime(*date[:6]) + timedelta(0, self.expire_after)
            return {
                'expires': formatdate(calendar.timegm(expires.timetuple())),
                'cache-control': 'public',
            }

    def warning(self, response):
        return '110 - "%s"' % self.msg
