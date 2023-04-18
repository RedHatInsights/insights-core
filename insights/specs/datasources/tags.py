"""
Custom datasource for tags.json
"""
import json
import logging
import os
import yaml

from itertools import chain

from insights.client.constants import InsightsConstants as constants
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent, ContentException
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider


logger = logging.getLogger(__name__)


@datasource(HostContext)
def tags(broker):
    """
    Custom datasource for ``tags.json`` generated (converted) by the
    insights-client tool.

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
            return DatasourceProvider(content=json.dumps(t), relative_path='tags.json')
        msg = "Empty YAML. Unable to load '%s'." % tags_file_path
        logger.error(msg)
        raise ContentException(msg)
    logger.debug("'%s' does not exist" % tags_file_path)
    raise SkipComponent("No such file '%s'." % tags_file_path)
