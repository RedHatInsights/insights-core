#!/usr/bin/env python

import json
import logging
import os
import sys

from insights.parsr import query

log = logging.getLogger(__name__)
logging.basicConfig(format='%(message)s', level=logging.INFO)

coverage_json = "coverage.json"

if len(sys.argv) < 2:
    log.error("Provide changed files.")
    sys.exit(1)

if not os.path.exists(coverage_json):
    log.error("'coverage.json' does not exist.")
    sys.exit(1)

coverage_report = None
with open(coverage_json) as fp:
    coverage_report = query.from_dict(json.load(fp))

if not coverage_report:
    log.error("No coverage report.")
    sys.exit(1)

changed_files = []
with open(sys.argv[1]) as fp:
    changed_files = list(filter(None, (l.strip() for l in fp.read().splitlines())))

if not changed_files:
    log.info("No change needs to check coverage in this PR.")
    sys.exit(0)

log.info(f"File(s) need to check coverage:")
for chf in changed_files:
    log.info(f"  - {chf}")

log.info("===================================================================")
log.info(f"Total Coverage: {coverage_report.totals.percent_covered_display.value}%")

okay_flag = True
log.info("File(s) Missing Coverage:")
for chf in changed_files:
    cov = coverage_report.find(chf).summary.percent_covered_display.value
    if cov:
        okay_flag = int(cov) == 100
        log.info(f"  - {chf}: {cov}%")

sys.exit(1 if not okay_flag else 0)
