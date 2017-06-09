#!/usr/bin/env python

import argparse
import json
import logging
import multiprocessing as mp
import os
import signal
import time
from collections import defaultdict
from random import sample

from insights.core import archives
from insights.core import load_package
from insights.core.evaluators import MultiEvaluator, SingleEvaluator
from insights.core.specs import SpecParser

try:
    from insights_nexus.config.factory import get_config
    config = get_config()
except:
    config = None

log = logging.getLogger(__name__)
stop = False


def stop_handler(signum, frame):
    global stop
    stop = True


signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGTERM, stop_handler)


def get_args():
    parser = argparse.ArgumentParser("python -m insights.tools.perf")
    parser.add_argument("-p", "--package", required=True, dest="package", help="Package containing the rules to process.")
    parser.add_argument("-n", "--num_archives", default=10, dest="num_archives", type=int, help="Number of archives to process.")
    parser.add_argument("-w", "--workers", default=mp.cpu_count() / 2, dest="num_workers", type=int, help="Number of processes to use.")
    parser.add_argument("-e", "--extract_dir", default="/tmp", dest="extract_dir", help="Working directory into which archives are extracted.")
    parser.add_argument("-d", "--debug", default=False, action="store_true", help="Output DEBUG level messages and final stats.")
    parser.add_argument("-s", "--silent", default=False, action="store_true", help="Output only FATAL messages and final stats.")
    parser.add_argument("-r", "--random", default=False, action="store_true", help="Randomly select archives from all available.")
    parser.add_argument("archive_path", nargs="*", help="Archive file or directory containing archives. Multiple files or directories may be specified.")
    return parser.parse_args()


def print_stats(times, start, end, num_workers):
    l = len(times)
    median = sorted(times)[l / 2] if l else 0.0
    avg = (sum(times) / float(l)) if l else 0.0
    msg = """
    Workers: %s
    Max: %s
    Min: %s
    Avg: %s
    Med: %s
    Tot: %s
    Throughput: %s
    """ % (num_workers, max(times), min(times), avg, median, l, (float(l) / (end - start)))
    print msg


def print_response(r):
    skips = set()
    for sk in r["skips"]:
        ski = sk["details"]
        something = ski[5:ski.index("]") + 1].replace("'", '"')
        for ha in json.loads(something):
            skips.add(ha)
    r["skips"] = list(skips)
    print json.dumps(r)


def get_paths(roots):
    paths = []
    for root in roots:
        if os.path.isdir(root):
            paths.extend([os.path.join(root, f) for f in os.listdir(root) if '.tar' in f])
        elif '.tar' in root:
            paths.append(root)
    return paths


def process_report(path, tmp_dir):
    with archives.TarExtractor() as extractor:
        if config is None:
            spec_mapper = SpecParser(extractor.from_path(path, tmp_dir))
        else:
            spec_mapper = SpecParser(extractor.from_path(path, tmp_dir), config)
        md = json.loads(spec_mapper.get_content("metadata.json", split=False, default="{}"))
        evaluator = MultiEvaluator(spec_mapper) if md and 'systems' in md else SingleEvaluator(spec_mapper)
        return evaluator.process()


def worker(paths, extract_dir, results_queue):
    for path in paths:
        if stop:
            results_queue.put(None)
            return

        result = None
        start = time.time()
        try:
            result = process_report(path, extract_dir)
        except Exception as ex:
            result = ex

        duration = time.time() - start
        results_queue.put((duration, result))


def process_reports(paths, extract_dir, num_workers):
    start = time.time()
    times = []
    results = []

    results_queue = mp.Queue()

    buckets = defaultdict(list)
    for idx, path in enumerate(paths):
        buckets[idx % num_workers].append(path)

    pool = []
    for i, p in buckets.iteritems():
        args = (p, extract_dir, results_queue)
        proc = mp.Process(target=worker, name="worker-%s" % i, args=args)
        pool.append(proc)

    for proc in pool:
        proc.start()

    def signal_handler(signum, frame):
        print_stats(times, start, time.time(), num_workers)

    signal.signal(signal.SIGUSR1, signal_handler)

    stops = 0
    for i in range(len(paths)):
        t = results_queue.get()
        if t is None:
            stops += 1
            if stops == num_workers:
                break
            else:
                continue
        d, r = t
        times.append(d)
        results.append(r)

    print_stats(times, start, time.time(), num_workers)
    for proc in pool:
        proc.join()


def main():
    args = get_args()

    if args.silent:
        logging.basicConfig(level=logging.FATAL)
    else:
        logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    load_package(args.package)

    extract_dir = args.extract_dir
    num_archives = args.num_archives
    paths = get_paths(args.archive_path)
    if num_archives < len(paths):
        if args.random:
            paths = sample(paths, num_archives)
        else:
            paths = paths[:num_archives]

    if len(paths) > 1:
        process_reports(paths, extract_dir, args.num_workers)
    else:
        print_response(process_report(paths[0], extract_dir))


if __name__ == "__main__":
    main()
