#!/usr/bin/env python

from falafel.config import InsightsDataSpecConfig
import specs as static_specs

_configs = {}


def _get_config(static_spec_module=static_specs):
    all_specs = dict(static_spec_module.static_specs)
    all_specs.update(static_spec_module.openshift)
    return InsightsDataSpecConfig(
        all_specs,
        static_spec_module.meta_files,
        pre_commands=static_specs.pre_commands)


def get_config(module=static_specs):
    if module not in _configs:
        _configs[module] = _get_config(module)

    return _configs.get(module)
