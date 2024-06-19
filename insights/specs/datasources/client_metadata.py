"""
Custom datasource for client metadata
"""
import json
import logging
import os
import yaml

from itertools import chain

from insights import package_info
from insights.client.constants import InsightsConstants as constants
from insights.core.blacklist import BLACKLISTED_SPECS
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent, ContentException
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider

try:
    from insights_client.constants import InsightsConstants as wrapper_constants
except ImportError:
    wrapper_constants = None


logger = logging.getLogger(__name__)


@datasource(HostContext)
def ansible_host(broker):
    """
    Custom datasource for ``ansible_host`` getting from insights-client
    configuration.

    Raises:
        SkipComponent: When there is no `ansible_host` is configured.

    Returns:
        str: The Ansible Hostname
    """
    insights_config = broker.get('client_config')
    if insights_config and insights_config.ansible_host:
        return DatasourceProvider(content=insights_config.ansible_host,
                                  relative_path='ansible_host')
    raise SkipComponent


@datasource(HostContext)
def basic_auth_insights_client(broker):
    """
    Custom datasource for ``username`` and ``password`` getting from insights-client
    configuration.

    Raises:
        SkipComponent: When there is no insights_config.

    Returns:
        dict: username/password exitsing boolean
    """
    insights_config = broker.get('client_config')
    result = {}
    if insights_config:
        if insights_config.username:
            result['username_set'] = True
        if insights_config.password:
            result['pass_set'] = True
        if result:
            return DatasourceProvider(content=json.dumps(result), relative_path='basic_conf')
    raise SkipComponent


@datasource(HostContext)
def blacklist_report(broker):
    """
    Custom datasource for ``blacklist_report`` getting from insights-client
    configuration.

    Returns:
        str: The JSON strings
    """
    def length(lst):
        '''
        Because of how the INI remove.conf is parsed,
        an empty value in the conf will produce
        the value [''] when parsed. Do not include
        these in the report
        '''
        return len(list(filter(None, lst)))

    redact_config = broker.get('redact_config')
    client_config = broker.get('client_config')

    ret = dict(
        obfuscate=False,
        obfuscate_hostname=False,
        commands=0,
        files=0,
        components=0,
        patterns=0,
        keywords=0,
        using_new_format=True,
        using_patterns_regex=False,
    )
    if client_config:
        ret.update(
            obfuscate=client_config.obfuscate,
            obfuscate_hostname=client_config.obfuscate_hostname,
        )
    if redact_config:
        ret.update(
            commands=length(redact_config.get('commands', [])),
            files=length(redact_config.get('files', [])),
            components=length(redact_config.get('components', [])),
            keywords=length(redact_config.get('keywords', [])),
            using_new_format=redact_config.get('new_format', True),
        )
        if isinstance(redact_config.get('patterns'), dict):
            ret.update(
                patterns=length(redact_config['patterns']['regex']),
                using_patterns_regex=True
            )
        else:
            ret.update(patterns=length(redact_config.get('patterns')))
    return DatasourceProvider(content=json.dumps(ret),
                              relative_path='blacklist_report')


@datasource(HostContext)
def blacklisted_specs(broker):
    """
    Custom datasource for ``blacklisted_specs`` getting from insights-client
    configuration.

    Raises:
        SkipComponent: When there is no `file-redaction` is configured.

    Returns:
        str: The JSON strings
    """
    if BLACKLISTED_SPECS:
        return DatasourceProvider(content=json.dumps({"specs": BLACKLISTED_SPECS}),
                                  relative_path='blacklisted_specs')
    raise SkipComponent


@datasource(HostContext)
def branch_info(broker):
    """
    Custom datasource for ``branch_info`` getting from insights-client
    configuration.

    Returns:
        str: The JSON strings
    """
    insights_config = broker.get('client_config')
    if insights_config:
        if insights_config.offline:
            branch_info = constants.default_branch_info
        else:
            branch_info = insights_config.branch_info
    return DatasourceProvider(content=json.dumps(branch_info),
                              relative_path='branch_info')


@datasource(HostContext)
def display_name(broker):
    """
    Custom datasource for ``display_name`` getting from insights-client
    configuration.

    Raises:
        SkipComponent: When there is no `display_name` is configured.

    Returns:
        str: The JSON strings
    """
    insights_config = broker.get('client_config')
    if insights_config and insights_config.display_name:
        return DatasourceProvider(content=insights_config.display_name,
                                  relative_path='display_name')
    raise SkipComponent


@datasource(HostContext)
def egg_release(broker):
    """
    Custom datasource for ``display_name`` getting from insights-client
    configuration.

    Raises:
        SkipComponent: When cannot get the `egg_release`.

    Returns:
        str: The JSON strings
    """
    egg_release = ''
    try:
        with open(constants.egg_release_file) as fil:
            egg_release = fil.read()
    except (IOError, MemoryError) as e:
        logger.debug('Could not read the egg release file: %s', str(e))

    if egg_release:
        return DatasourceProvider(content=egg_release,
                                  relative_path='egg_release')
    raise SkipComponent


@datasource(HostContext)
def tags(broker):
    """
    Custom datasource for ``tags`` getting from insights-client configuration.

    Raises:
        SkipComponent: When there is no `tags.yaml` is configured.
        ContentException: When any exceptions occur.

    Returns:
        str: The JSON strings
    """
    tags = None
    # Get the 'tags.yaml' from the host first.
    tags_file_path = constants.default_tags_file
    if os.path.isfile(tags_file_path):
        try:
            with open(tags_file_path) as fp:
                tags = yaml.safe_load(fp) or {}
        except (yaml.YAMLError, yaml.parser.ParserError) as e:
            # can't parse yaml from conf
            logger.error("Invalid YAML. Unable to load '%s'" % tags_file_path)
            raise ContentException('ERROR: Cannot parse %s.\n\nError details: \n%s\n' % (tags_file_path, e))

        # --START--
        # NOTE:
        # The following code is from the following function
        # - insights.client.data_collector.DataCollector._write_tags
        # Please keep them consistence before removing that.
        def f(k, v):
            if type(v) is list:
                col = []
                for val in v:
                    col.append(f(k, val))
                return list(chain.from_iterable(col))
            elif type(v) is dict:
                col = []
                for key, val in v.items():
                    col.append(f(k + ":" + key, val))
                return list(chain.from_iterable(col))
            else:
                return [{"key": k, "value": v, "namespace": constants.app_name}]
        t = []
        for k, v in tags.items():
            iv = f(k, v)
            t.append(iv)
        t = list(chain.from_iterable(t))
        # --END--

        if t:
            # The actual file path in archive:
            # - insights-archive-xxx/data/tags.json
            return DatasourceProvider(content=json.dumps(t),
                                      relative_path='tags.json')
        msg = "Empty YAML. Unable to load '%s'." % tags_file_path
        logger.error(msg)
        raise ContentException(msg)
    logger.debug("'%s' does not exist" % tags_file_path)
    raise SkipComponent("No such file '%s'." % tags_file_path)


@datasource(HostContext)
def version_info(broker):
    """
    Custom datasource for ``version_info`` getting from insights-client configuration.

    Returns:
        str: The JSON strings of version info
    """
    try:
        client_version = wrapper_constants.version
    except AttributeError:
        client_version = None

    version_info = {}
    version_info['core_version'] = '{0}-{1}'.format(package_info['VERSION'],
                                                    package_info['RELEASE'])
    version_info['client_version'] = client_version

    return DatasourceProvider(content=json.dumps(version_info),
                              relative_path='version_info')
