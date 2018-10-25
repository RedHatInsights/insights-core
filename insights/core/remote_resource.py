import requests
import requests_cache


class RemoteResource(object):
    """
    RemoteResource class for accessing external Web resources.

    Attributes:
        timeout(float): Time in seconds for the requests.get api call to wait before returning a timeout exception
        cert_path(str): Path to the cert file if supplied.
        headers (dict): Dictionary containing HTTP headers needed.

    Examples:
        >>> from insights.core.remote_resource import RemoteResource
        >>> rr = RemoteResource()
        >>> rtn = rr.get("http://google.com")
        >>> print (rtn.content)
    """

    timeout = 10
    cert_path = None
    headers = {}

    @classmethod
    def get(cls, url, params={}):
        """
        Returns the response payload from the request to the given URL.

        Args:
            url (str): The URL for the WEB API that the request is being made too.
            params (dict): Dictionary containing the query string parameters

        Returns:
            Response:(Response): Response object from requests.get api request
        """

        cls.cert_path if cls.cert_path else False

        return requests.get(url, params=params, headers=cls.headers, timeout=cls.timeout, verify=cls.cert_path)


class CachedRemoteResource(RemoteResource):
    """
    RemoteResource subclass that sets up caching for subsequent Web resource requests.

    Attributes:
        expire_after(float): Amount of time in seconds that the cache will expire
        old_data_on_error(bool): If True, expired cached data will be used for unsuccessful requests

    Raises:
        Exception

    Examples:
        >>> from insights.core.remote_resource import CachedRemoteResource
        >>> crr = CachedRemoteResource()
        >>> rtn = crr.get("http://google.com")
        >>> print (rtn.content)

    """

    expire_after = 180
    old_data_on_error = True
    __backend = "memory"

    def __init__(self):

        try:
            requests_cache.install_cache('core', old_data_on_error=self.old_data_on_error,
                                         backend=self.__backend, expire_after=self.expire_after)
        except Exception as ex:
            raise Exception("Error initializing requests_cache", ex)
