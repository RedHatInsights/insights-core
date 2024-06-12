from insights.client.apps.ansible.playbook_verifier.contrib.ruamel_yaml.ruamel.yaml.comments import (
    CommentedMap,
    CommentedSeq,
)


class PlaybookSerializer:
    @classmethod
    def serialize(cls, source):
        """Serialize snippet into string.

        :param source: Parsed playbook.
        :type source: dict | yaml.comments.CommentedMap
        :returns: Serialized playbook.
        :rtype: str
        """
        return cls._dict(source)

    @classmethod
    def _dict(cls, source):
        """
        :type source: dict | yaml.comments.CommentedMap
        :rtype: str
        """
        result_map = {}  # type: dict[str, str]

        for key, value in source.items():
            if isinstance(value, dict) or isinstance(value, CommentedMap):
                result_map[key] = cls._dict(value)
                continue
            if isinstance(value, list) or isinstance(value, CommentedSeq):
                result_map[key] = cls._list(value)
                continue
            if isinstance(value, int) or isinstance(value, float):
                result_map[key] = str(value)
                continue
            result_map[key] = "'{value}'".format(value=value)

        result = "ordereddict(["
        result += ", ".join(
            "('{key}', {value})".format(key=key, value=value)
            for key, value in result_map.items()
        )
        result += "])"
        return result

    @classmethod
    def _list(cls, source):
        """
        :type source: list | yaml.comments.CommentedSeq
        :rtype: str
        """
        result_list = []  # type: list[str]

        for value in source:
            if isinstance(value, list) or isinstance(value, CommentedSeq):
                result_list.append(cls._list(value))
                continue
            if isinstance(value, dict) or isinstance(value, CommentedMap):
                result_list.append(cls._dict(value))
                continue
            if isinstance(value, int) or isinstance(value, float):
                result_list.append(str(value))
                continue
            result_list.append("'{value}'".format(value=value))

        result = "["
        result += ", ".join(value for value in result_list)
        result += "]"
        return result
