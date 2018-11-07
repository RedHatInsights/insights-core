import requests

import redis
import calendar
from cachecontrol.heuristics import BaseHeuristic
from cachecontrol.wrapper import CacheControl
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

    def __init__(self, session=None):

        self.session = session or requests.Session()

    def get(self, url, params={}, headers={}, auth=(), certificate_path=None):
        """
        Returns the response payload from the request to the given URL.

        Args:
            url (str): The URL for the WEB API that the request is being made too.
            params (dict): Dictionary containing the query string parameters.
            headers (dict): HTTP Headers that may be needed for the request.
            auth (tuple): User ID and password for Basic Auth
            certificate_path (str): Path to the ssl certificate.

        Returns:
            response: (HttpResponse): Response object from requests.get api request
        """

        certificate_path = certificate_path if certificate_path else False
        return self.session.get(url, params=params, headers=headers, verify=certificate_path, auth=auth,
                            timeout=self.timeout)


class CachedRemoteResource(RemoteResource):
    """
    RemoteResource subclass that sets up caching for subsequent Web resource requests.

    Attributes:
        expire_after (float): Amount of time in seconds that the cache will expire
        backend (str): Type of storage for cache `DictCache1`, `FileCache` or `RedisCache`
        redis_host (str): Hostname of redis instance if `RedisCache` backend is specified
        redis_port (int): Port used to contact the redis instance if `RedisCache` backend is specified
        file_cache_path (string): Path to where file cache will be stored if `FileCache` backend is specified

    Examples:
        >>> from insights.core.remote_resource import CachedRemoteResource
        >>> crr = CachedRemoteResource()
        >>> rtn = crr.get("http://google.com")
        >>> print (rtn.content)

    """

    expire_after = 180
    backend = "DictCache"
    redis_port = 6379
    redis_host = 'localhost'
    __heuristic = 'DefaultHeuristic'
    __cache = None
    file_cache_path = '.web_cache'

    def __init__(self):

        session = requests.Session()
        hclass = globals()[self.__heuristic]

        if not self.__class__.__cache:
            if self.backend == "RedisCache":
                pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port, db=0)
                r = redis.Redis(connection_pool=pool)
                self.__class__.cache = RedisCache(r)
            elif self.backend == "FileCache":
                self.__class__.cache = FileCache(self.file_cache_path)
            else:
                self.__class__.cache = None

        session = CacheControl(session, heuristic=hclass(self.expire_after), cache=self.__class__.cache)

        super(CachedRemoteResource, self).__init__(session)


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
            response (HttpResponse): The response from the remote service

        Returns:
            response:(HttpResponse.Headers): Http caching headers
        """
        if 'expires' in response.headers and 'cache-control' in response.headers:
            self.msg = self.server_cache_headers
            return response.headers
        else:
            self.msg = self.default_cache_vars
            date = parsedate(response.headers['date'])
            expires = datetime(*date[:6]) + timedelta(0, self.expire_after)
            response.headers.update({'expires': formatdate(calendar.timegm(expires.timetuple())),
                                'cache-control': 'public'})
            return response.headers

    def warning(self, response):
        return '110 - "%s"' % self.msg
