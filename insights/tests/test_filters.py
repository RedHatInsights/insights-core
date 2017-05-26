from insights.core import plugins
from insights.config.static import get_config

spec = get_config()

ERROR_MESSAGE = """
`{0}` is marked as large but has no filters defined.
""".strip()


def _symbolic_names(plugin):
    names = []
    for m in plugin["mappers"]:
        names.extend(m.symbolic_names)
    if [n for n in names if 'rabbit' in n]:
        print plugin
        print names
    return names


def _check_filter(name, states):
    if True in states:
        return True
    else:
        for handler in plugins.MAPPERS[name]:
            if handler.filters:
                return True
        # At this point we there are no filters defined
        # But we need to make sure this symbolic name is really used before reporting
        return False if any(m.consumers for m in plugins.MAPPERS[name]) else True


def check_filters(name, states):
    if spec.is_large(name):
        assert _check_filter(name, states), ERROR_MESSAGE.format(name)


def gen_test_filter_tuple():
    return [(name, states) for name, states in plugins.SYMBOLIC_NAME_FILTER_MAPPING.iteritems()]


def gen_ids(filter_tuple):
    return [name for name, states in filter_tuple]
