import logging
import re
from collections import defaultdict
from falafel.core import marshalling, MapperOutput, plugins
from falafel.core import context
from falafel.config.static import get_config
from falafel.util import logging_level

specs = get_config()
logger = logging.getLogger("mapper")
marshaller = marshalling.Marshaller()


def stringify_mapper(o):
    return "#".join([o.__module__, o.__name__])


def stringify(o):
    if isinstance(o[0], MapperOutput):
        r = []
        for item in o:
            r.append(item.to_json())
        return r
    else:
        return o


def serialize(output):
    logger.debug("Serializing output")
    new_output = {}
    for host, mapper_dict in output.iteritems():
        new_dict = {}
        for mapper, value in mapper_dict.iteritems():
            new_dict[stringify_mapper(mapper)] = stringify(value)
        new_output[host] = new_dict
    return marshalling.marshal(new_output)


def filter_lines(lines, target):
    to_keep = plugins.NAME_TO_FILTER_MAP.get(target, [])
    if to_keep:
        logger.debug("Filtering %d lines against target [%s]", len(lines), target)
        regex = re.compile("(%s)" % "|".join(map(re.escape, to_keep)))
        logger.debug("Filtering regex: %s", regex.pattern)
        r = [line for line in lines if regex.search(line)]
        logger.debug("Stripped %d lines", len(lines) - len(r))
        return r
    else:
        return lines


def create_context(doc, content):
    return context.Context(
        content=filter_lines(content.splitlines(), doc["target"]),
        path=doc["path"],
        hostname=doc["hostname"],
        release=doc["release"],
        version=doc["version"],
        machine_id=doc["attachment_uuid"] if doc["attachment_uuid"] else None,
        target=doc["target"],
        **{k: v for k, v in doc.items() if k in context.PRODUCT_NAMES or k == "metadata"}
    )


def _unmarshal(s):
    if isinstance(s, basestring):
        # Used for line-based JSON input
        return marshalling.unmarshal(s)
    else:  # Should be a dict; used during integration tests.
        return s


def handle_large_file(doc, stream):
    logger.debug("Large file [%s] detected", doc.get("target"))
    content = doc["content"]
    while True:
        try:
            new_doc = _unmarshal(stream.next())
        except StopIteration:
            yield doc["case_number"], create_context(doc, content)
            raise StopIteration
        new_file_boundary = (new_doc["attachment_uuid"] != doc["attachment_uuid"] or
                             new_doc["path"] != doc["path"])
        if new_file_boundary:
            yield doc["case_number"], create_context(doc, content)
            if specs.is_large(new_doc["target"]):
                content = new_doc["content"]
                doc = new_doc
            else:
                yield new_doc["case_number"], create_context(new_doc, new_doc["content"])
                break
        else:
            content = content + new_doc["content"]


def gen_contexts(stream):
    while True:
        doc = _unmarshal(stream.next())
        if doc and "target" in doc:
            if specs.is_large(doc["target"]):
                for case, ctx in handle_large_file(doc, stream):
                    yield case, ctx
            else:
                yield doc["case_number"], create_context(doc, doc["content"])


@logging_level(logger, logging.DEBUG)
def log_mappers(mappers):
    logger.debug("Custom mapper listing:")
    for symbolic_name in sorted(mappers.keys()):
        mapper_list = mappers[symbolic_name]
        logger.debug("\t%s: %s", symbolic_name, [m.serializable_id for m in mapper_list])


def run(stream, mappers=plugins.MAPPERS):
    logger.debug("Starting mapper run")
    if mappers != plugins.MAPPERS:
        log_mappers(mappers)
    output = defaultdict(lambda: defaultdict(list))
    cases = {}
    for case, host_id, mapper, result in run_mappers(stream, mappers):
        output[host_id][mapper].append(result)
        cases[host_id] = case
    return cases, output


def run_mappers(stream, mappers=plugins.MAPPERS):
    for case, ctx in gen_contexts(stream):
        for mapper in mappers[ctx.target]:
            logger.debug("Executing mapper [%s] against target [%s]",
                         mapper.serializable_id, ctx.target)
            try:
                if mapper.shared:
                    if isinstance(mapper, type) and issubclass(mapper, MapperOutput):
                        response = mapper.parse_context(ctx)
                    else:
                        response = mapper(ctx)
                else:
                    response = marshaller.marshal(
                        mapper(ctx), use_value_list=specs.is_multi_output(ctx.target))
                if response:
                    logger.debug("Response for [%s]", ctx.machine_id)
                    yield case, ctx.machine_id, mapper, response
            except Exception:
                logger.exception(mapper.serializable_id)


# This is so incredibly verbose that it should use TRACE (which doesn't exist)
@logging_level(logger, logging.DEBUG)
def log_content(ctx):
    logger.debug("ID: " + ctx.machine_id)
    logger.debug("Mapper content:")
    logger.debug("\n" + "\n".join(ctx.content))
