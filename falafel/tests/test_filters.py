from falafel.core import plugins

ERROR_MESSAGE = """

The following plugins do not specify filters for symbolic
name `{1}`:

    {0}

This will prevent the plugin from receiving data that it expects.
Add filters to your mapper like so:

    @mapper('{1}', ['filter', 'string'])
""".rstrip()


def check_filters(name, states):
    plugins = "\n    ".join(states.get(False, []))
    assert len(states) == 1, ERROR_MESSAGE.format(plugins, name)


def test_filters():
    from falafel.mappers import *  # noqa
    for name, states in plugins.SYMBOLIC_NAME_FILTER_MAPPING.iteritems():
        yield check_filters, name, states
