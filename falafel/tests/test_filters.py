from falafel.core import plugins
from falafel.config.static import get_config

spec = get_config()

ERROR_MESSAGE = """
`{0}` is marked as large but has no filters defined.
""".strip()


def _check_filter(name, states):
    if True in states:
        return True
    else:
        for handler in plugins.MAPPERS[name]:
            if handler.filters:
                return True
        return False


def check_filters(name, states):
    if spec.is_large(name):
        assert _check_filter(name, states), ERROR_MESSAGE.format(name)


def gen_test_filter_tuple():
    return [(name, states) for name, states in plugins.SYMBOLIC_NAME_FILTER_MAPPING.iteritems()]


def gen_ids(filter_tuple):
    return [name for name, states in filter_tuple]
