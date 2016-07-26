import logging
import sys
from collections import defaultdict
from falafel.core import marshalling, plugins
from falafel.config.static import get_config
from falafel.util import logging_level

specs = get_config()
logger = logging.getLogger("reducer")
marshaller = marshalling.Marshaller()


def string_to_mapper(o):
    try:
        module, fn_name = o.split("#")
        return getattr(sys.modules[module], fn_name)
    except:
        raise ValueError("Invalid mapper key: %s" % o)


def value_to_class(o):
    if len(o) > 0 and isinstance(o[0], list) and len(o[0]) == 3:
        r = []
        for item in o:
            cls_name, data, computed = item
            module, cls = cls_name.split("#")
            module = sys.modules[module]
            path = computed["file_path"] if "file_path" in computed else None
            r.append(getattr(module, cls)(data, path=path))
        return r if r else o
    return o


def deserialize(s):
    logger.debug("Deserializing")
    mapper_output = marshalling.unmarshal(s)
    new_output = {}
    for host, mapper_dict in mapper_output.iteritems():
        new_dict = {}
        for mapper_name, value in mapper_dict.iteritems():
            new_key = string_to_mapper(mapper_name)
            new_dict[new_key] = value_to_class(value)
        new_output[host] = new_dict
    return new_output


def pattern_file(symbolic_name):
    return specs.is_multi_output(symbolic_name)


def autobox(symbolic_names, output):
    if pattern_file(symbolic_names[0]):
        return marshaller.unmarshal_to_context(output)
    elif len(output) > 1:
        logger.warning("Simple file [%s] has multiple returns", symbolic_names[0])
    return output[0]


def collect_mapper_output(mapper_dict):
    plugin_output = defaultdict(dict)
    shared_output = {}
    for mapper, output in mapper_dict.iteritems():
        if mapper.shared:
            is_pattern = pattern_file(mapper.symbolic_names[0])
            shared_output[mapper] = output if is_pattern else output[0]
        else:
            plugin = sys.modules[mapper.__module__]
            plugin_output[plugin].update(autobox(mapper.symbolic_names, output))
    return plugin_output, shared_output


def collect_mapper_output_multi(mapper_dict):
    combined_local_output = defaultdict(lambda: defaultdict(list))
    combined_shared_output = defaultdict(dict)
    for host, mapper_dict in mapper_dict.iteritems():
        plugin_output, shared_output = collect_mapper_output(mapper_dict)
        for plugin, output in plugin_output.iteritems():
            for k, v in output.iteritems():
                combined_local_output[plugin][k].append(v)
        for mapper, output in shared_output.iteritems():
            combined_shared_output[mapper][host] = output
    return combined_local_output, combined_shared_output


def run_multi(mapper_output, error_handler, reducers=plugins.CLUSTER_REDUCERS):
    logger.debug("Multi-node reducer run started")
    if reducers != plugins.CLUSTER_REDUCERS:
        log_reducers(reducers)
    plugin_output, shared_output = collect_mapper_output_multi(mapper_output)
    for func, r in _run(reducers, plugin_output, shared_output, error_handler):
        yield func, r


def run(mapper_output, error_handler):
    logger.debug("Batch-mode reducer run started")
    for host, mapper_dict in mapper_output.iteritems():
        for func, r in run_host(mapper_dict, error_handler):
            yield host, func, r


def run_host(mapper_dict, error_handler, reducers=plugins.REDUCERS):
    logger.debug("Single-node reducer run started")
    if reducers != plugins.REDUCERS:
        log_reducers(reducers)
    plugin_output, shared_output = collect_mapper_output(mapper_dict)
    for func, r in _run(reducers, plugin_output, shared_output, error_handler):
        yield func, r
    for func, r in default_reducer_results(plugin_output):
        yield func, r


@logging_level(logger, logging.DEBUG)
def log_reducers(reducers):
    logger.debug("Custom reducer listing:")
    for reducer in sorted(reducers.values()):
        logger.debug("\t" + reducer.serializable_id)


@logging_level(logger, logging.DEBUG)
def log_mapper_outputs(func, local_output, shared_output):
    logger.debug("Invoking reducer [%s]", func.serializable_id)
    logger.debug("\tLocal keys: %s", sorted(local_output.keys()))
    if len(shared_output) > 0 and hasattr(shared_output.keys()[0], "serializable_id"):
        mapper_outputs = [o.serializable_id for o in sorted(shared_output.keys())]
    else:
        mapper_outputs = [o for o in sorted(shared_output.keys())]
    logger.debug("\tShared mapper outputs: %s", mapper_outputs)


def _run(reducers, plugin_output, shared_output, error_handler):
    for func in reducers.values():
        real_module = sys.modules[func.__module__]
        local_output = plugin_output[real_module]
        log_mapper_outputs(func, local_output, shared_output)
        r = run_reducer(func, local_output, shared_output, error_handler)
        logger.debug("Reducer output: %s", r)
        if r:
            yield func, r


def default_reducer_results(plugin_output):
    for module, output in plugin_output.iteritems():
        if "type" in output and output["type"] in ["metadata", "rule"]:
            yield plugins.PLUGINS[module.__name__]["mappers"][0], output


def run_reducer(func, local, shared, error_handler):
    try:
        return func(local=local, shared=shared)
    except Exception as e:
        error_handler(func, e, local, shared)
