#!/usr/bin/env python


def _make_factory_func():

    from insights.config import static as s_factory
    from insights.config import db as d_factory

    s_config = s_factory.get_config()
    d_config = d_factory.get_config()

    s_config.compose(d_config)

    def inner():
        return s_config
    return inner


get_config = _make_factory_func()
