"""engine_config - command ``engine-config --all``
==================================================

This module provides access to ovirt-engine configuration parameters
by parsing output of command ``engine-config --all``.
"""
from collections import namedtuple
from operator import itemgetter

from .. import parser, get_active_lines, CommandParser
from insights.specs import Specs


@parser(Specs.engine_config_all)
class EngineConfigAll(CommandParser):
    """Parsing output of command ``engine-config --all``

    The parser tries its best to get `value` & `version` for specified
    `keyword`. At the moment it works well for output which has
    `keyword`, `value` & `version` in a single line. It ignores
    keywords where is fails. It skip(rather fails) the `keyword`
    having multi-line output.

    Typical output of ``engine-config --all`` command is::

        MaxRerunVmOnVdsCount: 3 version: general
        MaxStorageVdsTimeoutCheckSec: 30 version: general
        ClusterRequiredRngSourcesDefault:  version: 3.6
        ClusterRequiredRngSourcesDefault:  version: 4.0
        ClusterRequiredRngSourcesDefault:  version: 4.1
        HotUnplugCpuSupported: {"x86":"false","ppc":"false"} version: 3.6
        HotUnplugCpuSupported: {"x86":"false","ppc":"false"} version: 4.0
        HotUnplugCpuSupported: {"x86":"true","ppc":"true"} version: 4.1


    Examples:

        >>> from insights.parsers.engine_config import EngineConfigAll
        >>> from insights.tests import context_wrap
        >>> output = EngineConfigAll(context_wrap(OUTPUT))}
        >>> 'MaxRerunVmOnVdsCount' in output
        True
        >>> output['MaxRerunVmOnVdsCount']
        ['3']
        >>> output.get('MaxRerunVmOnVdsCount')
        ['3']
        >>> output['HotUnplugCpuSupported']
        ['{"x86":"false","ppc":"false"}', '{"x86":"false","ppc":"false"}', '{"x86":"true","ppc":"true"}']
        >>> output['ClusterRequiredRngSourcesDefault']
        []
        >>> output.head('HotUnplugCpuSupported')
        '{"x86":"false","ppc":"false"}'
        >>> output.last('HotUnplugCpuSupported')
        '{"x86":"true","ppc":"true"}'
        >>> output.get_version('HotUnplugCpuSupported')
        ['3.6', '4.0', '4.1']
        >>> 'IDoNotExit' in output
        False
        >>> output['IDoNotExit']
        []
        >>> output.get('IDoNotExit')
        []
        >>> output.get_version('IDoNotExit')
        []
        >>> output.head('IDoNotExist)
        >>> output.last('IDoNotExist)

    Attributes:
        fields (list): List of `KeyValue` namedtupules for
                       each line in the configuration file.

        keywords (set): Set of keywords present in the configuration
                        file, each keyword has been converted to lowercase.
    """
    keyvalue = namedtuple('KeyValue',
                          ['keyword', 'value', 'version', 'kw_lower'])
    """namedtuple: Represent name value pair as a namedtuple with case."""

    def parse_content(self, content):
        """Parse each active line for keyword, values & version.

        Args:

            content (list): Output of command ``engine-config --all``.
        """
        self.fields = []
        for line in get_active_lines(content):
            try:
                key, val, ver = itemgetter(0, 1, -1)(line.split(' '))
                self.fields.append(self.keyvalue(key.strip(':'), val, ver, key.strip(':').lower()))  # noqa
            except:
                # TODO: Log an exception.
                pass
        self.keywords = set([kw.kw_lower for kw in self.fields])

    def __contains__(self, keyword):
        return keyword.lower() in self.keywords

    def __iter__(self):
        return iter(self.fields)

    def __getitem__(self, keyword):
        return self.get(keyword)

    def get(self, keyword):
        """A get value for keyword specified. A "dictionary like" method.

        Example:

            >>> output.get('MaxStorageVdsTimeoutCheckSec')
            ['30']

        Args:

            keyword (str): A key. For ex. `HotUnplugCpuSupported`.

        Returns:

            list: Values associated with a keyword. Returns an empty
            list if, all the values are empty or `keyword` does not
            exist.
        """
        kw = keyword.lower()
        if kw in self.keywords:
            return [kv.value for kv in self.fields if kv.kw_lower == kw if kv.value]
        return []

    def head(self, keyword):
        """Get first element from values(list).

        Example:

            >>> output['HotUnplugCpuSupported']
            ['{"x86":"false","ppc":"false"}', '{"x86":"false","ppc":"false"}', '{"x86":"true","ppc":"true"}']
            >>> output.head('HotUnplugCpuSupported')
            '{"x86":"false","ppc":"false"}'

        Args:

            keyword (str): A key. For ex. `HotUnplugCpuSupported`.

        Returns:

            str: First element from values(list) associated with a keyword else None
        """
        values = self.__getitem__(keyword)
        if values:
            return values[0]

    def last(self, keyword):
        """Get last element from values(list).

        Example:

            >>> output['HotUnplugCpuSupported']
            ['{"x86":"false","ppc":"false"}', '{"x86":"false","ppc":"false"}', '{"x86":"true","ppc":"true"}']
            >>> output.last('HotUnplugCpuSupported')
            '{"x86":"true","ppc":"true"}'

        Args:

            keyword (str): A key. For ex. `HotUnplugCpuSupported`.

        Returns:

            str: Last element from values(list) associated with a keyword else None.
        """
        values = self.__getitem__(keyword)
        if values:
            return values[-1]

    def get_version(self, keyword):
        """Get versions associated with a key.

        Typical output is ``engine-config --all`` command::

            MaxStorageVdsTimeoutCheckSec: 30 version: general
            HotUnplugCpuSupported: {"x86":"false","ppc":"false"} version: 3.6
            HotUnplugCpuSupported: {"x86":"false","ppc":"false"} version: 4.0
            HotUnplugCpuSupported: {"x86":"true","ppc":"true"} version: 4.1

        Examples:

            >>> output.get_version('MaxStorageVdsTimeoutCheckSec')
            ['general']
            >>> output.get_version('HotUnplugCpuSupported')
            ['3.6', '4.0', '4.1']

        Args:

            keyword (str): A key. For ex. `HotUnplugCpuSupported`.

        Returns:

            list: Versions associated with a keyword. Returns an empty
            list if, all the versions are empty or `keyword` does not
            exist.
        """
        kw = keyword.lower()
        if kw in self.keywords:
            return [kv.version for kv in self.fields if kv.kw_lower == kw if kv.version]
        return []
