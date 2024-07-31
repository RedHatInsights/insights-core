import logging

import six
from insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.comments import (
    CommentedMap,
    CommentedSeq,
)

logger = logging.getLogger(__name__)


class PlaybookSerializer:
    @classmethod
    def serialize(cls, value):
        """Serialize a playbook into a string.

        :returns: Serialized playbook.
        :rtype: str
        """
        return cls._obj(value)

    @classmethod
    def _obj(cls, value):
        """
        :type value: any
        :rtype: str
        """
        if isinstance(value, dict) or isinstance(value, CommentedMap):
            return cls._dict(value)
        if isinstance(value, list) or isinstance(value, CommentedSeq):
            return cls._list(value)
        if isinstance(value, int) or isinstance(value, float):
            return str(value)
        if isinstance(value, six.string_types):
            return cls._str(value)

        logger.debug("Value type not recognized, it may misbehave: {value} ({typ})".format(
            value=value, typ=type(value).__name__)
        )
        return "'" + str(value) + "'"

    @classmethod
    def _str(cls, value):
        """
        :type value: str
        :rtype: str
        """
        # no quote      'no quote'
        # single'quote  "single'quote"
        # double"quote  'double"quote'
        # both"'quotes  'both"\'quotes'

        quote = "'"
        if "'" in value:
            if '"' not in value:
                quote = '"'
            else:
                value = value.replace("'", "\\'")

        return quote + value + quote

    @classmethod
    def _dict(cls, value):
        """
        :type value: dict | yaml.comments.CommentedMap
        :rtype: str
        """
        result = "ordereddict(["
        result += ", ".join(
            "('{key}', {value})".format(key=k, value=cls._obj(v))
            for k, v in value.items()
        )
        result += "])"
        return result

    @classmethod
    def _list(cls, value):
        """
        :type value: list | yaml.comments.CommentedSeq
        :rtype: str
        """
        result = "["
        result += ", ".join(cls._obj(v) for v in value)
        result += "]"
        return result
