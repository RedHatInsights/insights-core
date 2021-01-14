"""
ProcEnviron - File ``/proc/<PID>/environ``
==========================================

Parser for parsing the ``environ`` file under ``/proc/<PID>`` directory.

"""

from insights import Parser, parser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.environ_all)
class ProcEnviron(Parser, dict):
    """
    Class for parsing the ``/proc/<PID>/environ`` file into a dictionaries
    with environment variable name as key and containing environment variable
    value.

    Typical content looks like::

        REGISTRIES=--add-registry registry.access.redhat.com \x00OPTIONS= --selinux-enabled --signature-verification=False\x00DOCKER_HTTP_HOST_COMPAT=1\x00ADD_REGISTRY=--add-registry registry.access.redhat.com\x00PATH=/usr/libexec/docker:/usr/bin:/usr/sbin\x00PWD=/run/docker/libcontainerd/containerd/135240dbd15a834acb21d68867930917afcc84c5f006ba65004acd88dccab756/init\x00LANG=en_US.UTF-8\x00GOTRACEBACK=crash\x00DOCKER_NETWORK_OPTIONS= --mtu=1450\x00DOCKER_CERT_PATH=/etc/docker\x00SHLVL=0\x00DOCKER_STORAGE_OPTIONS=--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/docker--vg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true \x00

    Examples:
        >>> proc_environ['REGISTRIES']
        '--add-registry registry.access.redhat.com'
        >>> 'OPTIONS' in proc_environ
        True

    Raises:
        insights.parsers.SkipException: if the ``environ`` file is empty or doesn't exist.
        insights.parsers.ParseException: if the ``environ`` file content is incorrect.

    Attributes:
        pid(int): The PID of the ``environ`` got from the file path
    """

    def parse_content(self, content):
        if len(content) > 1:
            raise ParseException("Incorrect content: '{0}'".format(content[-1]))

        data = {}
        cnt = content[0] if content else ''
        for item in cnt.split('\x00'):
            if '=' in item:
                k, v = item.strip().split('=', 1)
                data[k] = v
            elif item:
                raise ParseException("Incorrect content: '{0}'".format(item))

        if not data:
            raise SkipException("Empty output.")

        self.pid = int(self.file_path.lstrip('/').split('/')[1])
        self.update(data)

    @property
    def data(self):
        return self


@parser(Specs.openshift_fluentd_environ)
class OpenshiftFluentdEnviron(ProcEnviron):
    """
    .. warning::

        This Parser is deprecated, please use the
        :func:`insights.combiners.proc_environ.ProcEnvironAll.get_environ_of_proc`
        function instead.

    Class for parsing the ``environ`` file of the ``fluentd`` process.
    """
    def __init__(self, context):
        deprecated(
            OpenshiftFluentdEnviron,
            'Please use the \
            :func:`insights.combiners.proc_environ.ProcEnvironAll.get_environ_of_proc` \
            function instead.'
        )
        super(OpenshiftFluentdEnviron, self).__init__(context)


@parser(Specs.openshift_router_environ)
class OpenshiftRouterEnviron(ProcEnviron):
    """
    .. warning::

        This Parser is deprecated, please use the
        :func:`insights.combiners.proc_environ.ProcEnvironAll.get_environ_of_proc`
        function instead.

    Class for parsing the ``environ`` file of the ``openshift-route`` process.
    """
    def __init__(self, context):
        deprecated(
            OpenshiftRouterEnviron,
            'Please use the \
            :func:`insights.combiners.proc_environ.ProcEnvironAll.get_environ_of_proc` \
            function instead.'
        )
        super(OpenshiftRouterEnviron, self).__init__(context)
