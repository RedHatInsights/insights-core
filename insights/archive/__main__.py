from __future__ import print_function
import argparse
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor

from insights.archive import repo, get_archives
from insights.util import fs

p = argparse.ArgumentParser("python -m insights.archive")
p.add_argument("which", choices=("demo", "integration"))
p.add_argument("-v", "--verbose", dest="verbose", action="store_true", default=False)
p.add_argument("-q", "--quiet", dest="quiet", action="store_true", default=False)
p.add_argument("-c", "--clean", dest="clean", action="store_true", default=False)
p.add_argument("-d", "--destination", dest="destination", default="")
p.add_argument("-u", "--upload", action="store_true", default=False)
p.add_argument("-H", "--host", default="localhost:8080")
p.add_argument("-a", "--auth", default="")
p.add_argument("-s", "--systems", default="")
p.add_argument("-x", "--exclude", type=int, default=0)
p.add_argument("package")

args = p.parse_args()
repo.console = not args.quiet
demo_anchovies = list(get_archives(args.package, args.systems))
random.shuffle(demo_anchovies)


def post_it(url, anchovy, file_name, args):
    r = session.post(url % anchovy.machine_id, files={"file": open(file_name, "rb")})
    if r.status_code == 201:
        print("*** Uploaded", anchovy.name)
        if args.verbose:
            print(json.dumps(r.json(), indent=4))
        else:
            print("Rule hits:", [str(rpt["rule_id"]) for rpt in r.json()["reports"]])
    else:
        print("*** Upload FAILED for %s: %d" % (anchovy.name, r.status_code))
        print(r.text)
        sys.exit(1)


for i in range(args.exclude):
    print("Excluding [%s]" % demo_anchovies.pop().name)

if args.which == "integration":
    dest = args.destination if args.destination else repo.DEFAULT_DEST
    if os.path.exists(dest) and args.clean:
        print("Cleaning integration tests.")
        fs.remove(dest)
    list(repo.build_integration_test_archives(args.package,
                                              machine_id="c21320b6-29b1-11e5-adc7-28d244603426"))
else:
    dest = args.destination if args.destination else "./demo-archives"
    if os.path.exists(dest) and args.clean:
        print("Cleaning demo archives.")
        fs.remove(dest)
    demo_anchovies.sort(key=lambda x: x.name)
    repo.build_all(demo_anchovies, dest=dest, clean=args.clean)
    if args.upload:
        import requests
        if args.verbose:
            import json
        session = requests.Session()
        session.headers = {"User-Agent": "Insights Demo Client"}
        session.auth = tuple(args.auth.split(":"))
        assert len(session.auth) == 2
        url = "http://%s" % args.host + "/r/insights/uploads/%s"
        pool = ThreadPoolExecutor(16)
        for anchovy in demo_anchovies:
            file_name = os.path.join(dest, anchovy.name + ".tar.gz")
            pool.submit(post_it, url, anchovy, file_name, args)
        pool.shutdown()
