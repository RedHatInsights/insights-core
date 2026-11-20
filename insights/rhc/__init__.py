"""
Adapter that lets rhc's Collector framework (rhc-collector) trigger
insights-core's existing collection engine.

1. Implements the executable contract rhc-collector expects
   (<executable> collect, write into CWD, exit 0/non-zero).
2. Calls insights.collect.collect() - the same engine
   insights-client uses internally.
"""

import logging
import os
import shutil
import sys

logger = logging.getLogger(__name__)

# Exit codes. rhc-collector only cares about zero vs. non-zero,
# but we keep a couple of named values for our own log messages/tests.
EXIT_OK = 0
EXIT_USAGE_ERROR = 64
EXIT_COLLECTION_FAILED = 1


def _setup_logging():
    logging.basicConfig(
        level=logging.WARN,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _build_client_config():
    """
    Load configuration the same way insights-client's scheduler does
    : InsightsConfig().load_all().

    That reads /etc/insights-client/insights-client.conf and the redaction
    and tags files it points at. It's the only supported config path.
    """
    # Imported lazily so usage-error paths don't import the whole package.
    from insights.client.config import InsightsConfig

    return InsightsConfig().load_all()


def _get_machine_id():
    """
    insights.collect.collect() does not call this itself - it's
    orchestration-layer logic that insights-client normally handles before
    collection. On a host that never register, machine-id won't exist,
    so we generate/read it here, exactly as insights-client would.
    """
    from insights.client.utilities import generate_machine_id

    try:
        machine_id = generate_machine_id()
        logger.debug("machine-id: %s", machine_id)
    except Exception:
        logger.warning("Could not generate/read machine-id; continuing without it.", exc_info=True)


def _get_rm_conf(config):
    """
    Build the redaction config exactly as insights-client does
    (insights/client/client.py: collect() -> InsightsUploadConf(config).get_rm_conf()).
    """
    from insights.client.collection_rules import InsightsUploadConf

    try:
        return InsightsUploadConf(config).get_rm_conf()
    except Exception:
        logger.error("Could not load redaction configuration; aborting collection.", exc_info=True)
        raise


def _flatten_into_cwd(output_path, cwd):
    """
    insights.collect.collect() writes into tmp_path/archive_name/, not
    directly into the caller's CWD. rhc-collector expects the final
    archive contents directly in the scratch working directory it set
    via cmd.Dir before tar/xz-ing it, so we move everything up one level
    and remove the now-empty intermediate directory.
    """
    for name in os.listdir(output_path):
        shutil.move(os.path.join(output_path, name), os.path.join(cwd, name))
    os.rmdir(output_path)


def collect():
    """
    Runs one collection into the current working directory. Returns an
    exit code (0 = success).
    """
    from insights import collect as core_collect

    cwd = os.getcwd()

    try:
        config = _build_client_config()
    except Exception:
        logger.error("Could not load configuration.", exc_info=True)
        return EXIT_COLLECTION_FAILED

    _get_machine_id()

    try:
        rm_conf = _get_rm_conf(config)
    except Exception:
        return EXIT_COLLECTION_FAILED

    archive_name = core_collect.generate_archive_name()

    try:
        output_path, collect_errors = core_collect.collect(
            client_config=config,
            rm_conf=rm_conf,
            tmp_path=cwd,
            archive_name=archive_name,
            compress=False,  # rhc-collector does the tar/xz + upload itself
        )
    except Exception:
        logger.error("Core collection failed catastrophically.", exc_info=True)
        return EXIT_COLLECTION_FAILED

    if collect_errors:
        for exc_type, occurrences in collect_errors.items():
            for exc, component in occurrences:
                logger.warning("%s raised %s during collection of %s", component, exc_type.__name__, exc)

    _flatten_into_cwd(output_path, cwd)

    logger.info("Collection complete.")
    return EXIT_OK


def _main(argv=None):
    """
    Entry point implementing the Collector executable contract
    (rhc/doc/COLLECTORS.md): exactly one subcommand, collect.
    """
    argv = sys.argv[1:] if argv is None else argv
    prog = sys.argv[0] if sys.argv else __file__

    if argv != ["collect"]:
        sys.stderr.write("usage: {0} collect\n".format(prog))
        return EXIT_USAGE_ERROR

    sys.argv = [prog]

    _setup_logging()
    return collect()


if __name__ == "__main__":
    sys.exit(_main())
