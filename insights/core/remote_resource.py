import requests
import requests_cache


class RemoteResource(object):
    """
    RemoteResource class for accessing external Web resources.

    Functions:
        get(): Calls `get()` function of the RemoteRersource superclass and returns the response payload.

    Each line is parsed into a dictionary with the following keys:

    Examples:
        >>> from insights.core.remote_resource import RemoteResource
        >>> rr = RemoteResource()
        >>> rtn = rr.get("http://google.com")
        >>> print (rtn.content)
    """

    timeout = 10

    @classmethod
    def get(cls, url, params={}, headers={}):
        """
        Returns the response payload from the request to the given URL.
        Args:
            url (str): The URL for the WEB API that the request is being made too.
            params (dict): Dictionary containing the query string parameters
            headers (dict): Dictionary containing anny HTTP headers needed.
        Returns:
            InstalledRpm: Installed RPM with highest version
        """

        return requests.get(url, params=params, headers=headers, timeout=cls.timeout, verify=False)


class CachedRemoteResource(RemoteResource):
    """
    RemoteResource subclass for accessing external Web resources using caching.

    Functions:
        get(): Calls `set_cache()` to initialize the cache then calls the `get()` function of the
        RemoteResource superclass and returns the response payload
        set_cache(): Called by the `get()` function to initialize the cache for the Web request

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
        """
        Initializes the cache for the web requests and supplies a `get()` function which calls the `get()` function in
        the RemoteResource superclass

        """

        try:
            requests_cache.install_cache('core', old_data_on_error=self.old_data_on_error,
                                         backend=self.__backend, expire_after=self.expire_after)
        except Exception as ex:
            raise Exception("Error initializing requests_cache", ex)
