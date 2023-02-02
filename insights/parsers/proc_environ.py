"""
ProcEnviron - File ``/proc/<PID>/environ``
==========================================

Parser for parsing the ``environ`` file under ``/proc/<PID>``
directory.

"""
from insights.core import LegacyItemAccess, Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


class ProcEnviron(Parser, LegacyItemAccess):
    """
    Base class for parsing the ``environ`` file under special ``/proc/<PID>``
    directory into a dictionaries with environment variable name as key and containing
    environment variable value.

    Typical content looks like::

        REGISTRIES=--add-registry registry.access.redhat.com \x00OPTIONS= --selinux-enabled       --signature-verification=False\x00DOCKER_HTTP_HOST_COMPAT=1\x00ADD_REGISTRY=--add-registry registry.access.redhat.com\x00PATH=/usr/libexec/docker:/usr/bin:/usr/sbin\x00PWD=/run/docker/libcontainerd/containerd/135240dbd15a834acb21d68867930917afcc84c5f006ba65004acd88dccab756/init\x00LANG=en_US.UTF-8\x00GOTRACEBACK=crash\x00DOCKER_NETWORK_OPTIONS= --mtu=1450\x00DOCKER_CERT_PATH=/etc/docker\x00SHLVL=0\x00DOCKER_STORAGE_OPTIONS=--storage-driver devicemapper --storage-opt dm.fs=xfs --storage-opt dm.thinpooldev=/dev/mapper/docker--vg-docker--pool --storage-opt dm.use_deferred_removal=true --storage-opt dm.use_deferred_deletion=true \x00

    Examples:
        >>> proc_environ['REGISTRIES']
        '--add-registry registry.access.redhat.com'
        >>> 'OPTIONS' in proc_environ
        True

    Raises:
        insights.core.exceptions.SkipComponent: if the ``environ`` file is empty or doesn't exist.
        insights.core.exceptions.ParseException: if the ``environ`` file content is incorrect.

    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty output.")
        if len(content) != 1:
            raise ParseException("Incorrect content: '{0}'".format(content[-1]))

        self.data = {}
        for item in content[0].split('\x00'):
            if '=' in item:
                k, v = item.strip().split('=', 1)
                self.data[k] = v
            elif item:
                raise ParseException("Incorrect content: '{0}'".format(item))


@parser(Specs.openshift_fluentd_environ)
class OpenshiftFluentdEnviron(ProcEnviron):
    """
    Class for parsing the ``environ`` file of the ``fluentd`` process.
    """
    pass


@parser(Specs.openshift_router_environ)
class OpenshiftRouterEnviron(ProcEnviron):
    """
    Class for parsing the ``environ`` file of the ``openshift-route`` process.
    """
    pass
