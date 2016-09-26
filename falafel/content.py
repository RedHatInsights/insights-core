import git
import json
import logging
import os
import signal
import sys
import yaml
from .util import parse_table, word_wrap
from .core import load_package, plugins
from .tests import plugin_tests, ensure_cache_populated

try:
    import tornado.ioloop
    import tornado.web
    import tornado.wsgi
except:
    print "Dependencies 'tornado' is required for falafel-content"
    raise

logger = logging.getLogger("content")

CONTENT_PREFIX = "content"

PLUGIN_PACKAGE = "telemetry.rules.plugins"

REQUIRED_FIELDS = [
    "rule_id", "name", "email"
]

CONTENT_FIELDS = [
    "summary", "generic", "reason", "resolution", "more_info"
]

YAML_FIELDS = [
    "error_key", "description", "node_id", "severity",
    "category", "reboot_required", "type"
]

EXAMPLE_REQUEST = {
    "rule_id": "lvm_filter|LVM_FILTER",
    "name": "Andrew Hecox",
    "email": "ahecox@redhat.com",
    "reason": "skedoodle",
    "category": "Stability"
}


def write_content(content, path, wrap=False):
    content = content.replace("\\n", "\n")
    with open(path, "wb") as fp:
        if content.strip() == "NULL":
            fp.write("\n")
        elif wrap:
            for line in content.splitlines():
                for wrapped_line in word_wrap(line):
                    fp.write(wrapped_line + "\n")
        else:
            fp.write(content)
    return path


def compute_plugin_module(module, package):
    orig = module
    # TODO: Start with falafel.core.plugins.MAPPERS instead of sys.modules
    print module
    module = [sys.modules[m].__name__ for m in sys.modules if m.endswith("." + module)]
    assert len(module) < 2, module
    if not module:
        return ".".join(["retired", orig])
    module = module[0].split(package)[1].strip(".")
    intermediate = module.split(".")[:-1]
    if intermediate:
        intermediate.append(module.split(".")[-1])
        module = ".".join(intermediate)
    return module


def compute_plugin_dir(module, package):
    return compute_plugin_module(module, package).replace(".", "/")


def gen_yaml(data):
    y = {k: data[k] for k in YAML_FIELDS}
    return yaml.dump(y, default_flow_style=False, default_style="")


def save_rule(d, prefix="", package=PLUGIN_PACKAGE):
    module, error_key = d["rule_id"].split("|")
    plugin_dir = os.path.join(prefix, compute_plugin_dir(module, package))
    error_key_dir = os.path.join(plugin_dir, error_key)
    if not os.path.exists(error_key_dir):
        os.makedirs(error_key_dir)
    for content in CONTENT_FIELDS:
        if content in d:
            yield write_content(d[content],
                                os.path.join(plugin_dir, error_key, content + ".md"))
    yield write_content(gen_yaml(d),
                        os.path.join(plugin_dir, error_key, "metadata.yaml"))


def import_tsv():
    repo = git.Repo(".")
    load_package(PLUGIN_PACKAGE)
    data = parse_table(sys.stdin.read().splitlines(), "\t")
    for row in data:
        row["reboot_required"] = row["reboot_required"] == "1"
        row["node_id"] = row["node_id"] if row["node_id"] != "NULL" else None
    to_add = []
    for d in data:
        to_add.extend(list(save_rule(d, CONTENT_PREFIX)))
    repo.index.add(to_add)


def apply_changeset(repo, to_add, message, name, email):
    repo.index.add(to_add)
    repo.index.commit(message, author=git.objects.util.Actor(name, email))


def read_error_key(path):
    d = {"content": {}}
    for f in CONTENT_FIELDS:
        with open(os.path.join(path, f + ".md")) as fp:
            d["content"][f] = fp.read().strip()
    with open(os.path.join(path, "metadata.yaml"), "r") as fp:
        y = yaml.load(fp)
    d["metadata"] = y
    return d


def read_plugin_module(path):
    try:
        for error_key in os.listdir(path):
            yield read_error_key(os.path.join(path, error_key))
    except:
        logger.warning("Missing content: %s", os.path.basename(path))
        logger.warning(path)


def split_rule_id(rule_id):
    if "|" in rule_id:
        return rule_id.split("|")
    else:
        return rule_id, None


class ContentParamHandler(tornado.web.RequestHandler):

    def initialize(self, repo, plugin_package, test_package):
        self.repo = repo
        self.plugin_package = plugin_package
        self.test_package = test_package

    def get(self, rule_id):
        module, error_key = split_rule_id(rule_id)
        module_end = compute_plugin_module(module, self.plugin_package)
        module_name = ".".join([self.plugin_package, module_end])
        params = [expected for _, _, expected in plugin_tests(module_name) if expected]
        unwrapped = [i[0] if isinstance(i, list) else i for i in params]
        if error_key is not None:
            unwrapped = [p for p in unwrapped if p["error_key"] == error_key]
        for p in unwrapped:
            if "type" in p:
                del p["type"]
            if "affected_hosts" in p:
                p["hostname_mapping"] = {system_id: "hostname" for system_id in p["affected_hosts"]}
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(unwrapped))


class ContentHandler(tornado.web.RequestHandler):

    def initialize(self, repo, plugin_package, test_package):
        self.repo = repo
        self.plugin_package = plugin_package
        self.test_package = test_package
        self.content_prefix = os.path.join(self.repo.working_tree_dir, CONTENT_PREFIX)

    def get_content_for(self, module, error_key=None):
        p = os.path.join(self.content_prefix, compute_plugin_dir(module, self.plugin_package))
        for content in read_plugin_module(p):
            this_error_key = content["metadata"]["error_key"]
            if error_key is None or this_error_key == error_key:
                yield this_error_key, content

    def get_all_content(self, iterable):
        for plugin in iterable:
            p = plugin["module"].split(".")[-1]
            for content in self.get_content_for(p):
                yield content


class SingleContentHandler(ContentHandler):

    def get(self, rule_id):
        module, error_key = split_rule_id(rule_id)
        d = dict(self.get_content_for(module, error_key))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(d))


class BulkContentHandler(ContentHandler):

    def get(self):
        gen = (p for n, p in plugins.PLUGINS.items() if PLUGIN_PACKAGE in n)
        d = dict(self.get_all_content(gen))
        self.write(json.dumps(d))

    def post(self):
        try:
            d = json.loads(self.request.body)
        except Exception:
            self.set_status(400)
            self.write("Invalid document")
            return
        missing_fields = [f for f in REQUIRED_FIELDS if f not in d]
        if missing_fields:
            self.write("Missing field %s" % ",".join(missing_fields))
            self.set_status(400)
            return
        module, error_key = d["rule_id"].split("|")
        plugin_path = os.path.join(self.content_prefix, compute_plugin_dir(module))
        yaml_path = os.path.join(plugin_path, error_key, "metadata.yaml")
        with open(yaml_path, "r") as fp:
            d = yaml.load(fp).update(d)
        apply_changeset(self.repo, list(save_rule(d, self.content_prefix)),
                        "Posted content update for %s" % d["rule_id"],
                        d["name"], d["email"])


class ErrorKeyHandler(tornado.web.RequestHandler):

    def initialize(self, repo, plugin_package, test_package):
        self.repo = repo
        self.plugin_package = plugin_package
        self.test_package = test_package
        self.content_prefix = os.path.join(self.repo.working_tree_dir, CONTENT_PREFIX)

    def get(self):
        result = []
        all_the_reducers = plugins.REDUCERS.values() + plugins.CLUSTER_REDUCERS.values()
        for module_str in [r.__module__ for r in all_the_reducers]:
            real_module = sys.modules[module_str]
            for k, v in real_module.__dict__.items():
                if k.startswith("ERROR_KEY"):
                    result.append("|".join([module_str.split(".")[-1], v]))
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(result))


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        d = os.path.dirname(os.path.abspath(__file__))
        idx = os.path.join(d, "index.html")
        with open(idx) as fp:
            content = fp.read()
            self.set_header("Content-Type", "text/html")
            self.set_header("Content-Length", len(content))
            self.write(content)


def sig_handler(signum, frame):
    logger.debug("Received signal {0}.".format(signum))
    tornado.ioloop.IOLoop.current().add_callback_from_signal(shutdown)


def shutdown():
    logger.info("Shutting Down.")
    tornado.ioloop.IOLoop.current().stop()


def main():
    from optparse import OptionParser
    import git
    logging.basicConfig()
    p = OptionParser()
    p.add_option("--plugin-package", help="plugin package")
    p.add_option("--test-package", help="test package")
    p.add_option("-p", "--port", help="listening port",
                 default=8080, action="store", type="int")
    p.add_option("--git-path", help="git path",
                 default=".", action="store", type="string")
    opts, args = p.parse_args()
    if not opts.plugin_package:
        logger.error("Please provide plugin package")
    load_package(opts.plugin_package)
    params = {
        "repo": git.Repo(opts.git_path),
        "plugin_package": opts.plugin_package,
        "test_package": opts.test_package
    }
    routes = [
        (r"/content/?$", BulkContentHandler, params),
        (r"/content/([a-zA-Z0-9_%|]+)/?$", SingleContentHandler, params),
        (r"/error_keys/?$", ErrorKeyHandler, params),
        (r"/?$", IndexHandler)
    ]
    if opts.test_package:
        load_package(opts.test_package)
        routes.append((r"/params/([a-zA-Z0-9_|%]+)/?$", ContentParamHandler, params))
        ensure_cache_populated()
    application = tornado.web.Application(routes)
    application.listen(opts.port)
    loop = tornado.ioloop.IOLoop.current()
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    loop.start()
    loop.close()

if __name__ == "__main__":
    import_tsv()
