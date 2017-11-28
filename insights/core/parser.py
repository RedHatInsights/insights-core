import logging
import re
from collections import defaultdict
from insights.core import marshalling, plugins, SkipComponent
from insights.core import context
from insights.config.static import get_config
from insights.util import logging_level

specs = get_config()
logger = logging.getLogger("parser")
marshaller = marshalling.Marshaller()


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
def log_parsers(parsers):
    logger.debug("Custom parser listing:")
    for symbolic_name in sorted(parsers.keys()):
        parser_list = parsers[symbolic_name]
        logger.debug("\t%s: %s", symbolic_name, [m.serializable_id for m in parser_list])


def run(stream, parsers=plugins.PARSERS):
    logger.debug("Starting parser run")
    if parsers != plugins.PARSERS:
        log_parsers(parsers)
    output = defaultdict(lambda: defaultdict(list))
    cases = {}
    for case, host_id, parser, result in run_parsers(stream, parsers):
        output[host_id][parser].append(result)
        cases[host_id] = case
    return cases, output


def run_parsers(stream, parsers=plugins.PARSERS):
    for case, ctx in gen_contexts(stream):
        for parser in parsers[ctx.target]:
            logger.debug("Executing parser [%s] against target [%s]",
                         parser, ctx.target)
            try:
                if parser.shared:
                    response = parser(ctx)
                else:
                    response = marshaller.marshal(
                        parser(ctx), use_value_list=specs.is_multi_output(ctx.target))
                if response is not None:
                    logger.debug("Response for [%s] = %s", ctx.machine_id, response)
                    yield case, ctx.machine_id, parser, response
                else:
                    logger.debug("Response for [%s] = %s - treating this as not a valid response", ctx.machine_id, response)
            except SkipComponent as sc:
                logger.debug("Skipping parser %s: %s" % (str(parser), str(sc)))
            except Exception:
                logger.exception(str(parser))


# This is so incredibly verbose that it should use TRACE (which doesn't exist)
@logging_level(logger, logging.DEBUG)
def log_content(ctx):
    logger.debug("ID: " + ctx.machine_id)
    logger.debug("Parser content:")
    logger.debug("\n" + "\n".join(ctx.content))
