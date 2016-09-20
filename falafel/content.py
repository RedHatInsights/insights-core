import git
import json
import logging
import os
import signal
import sys
import yaml
from falafel.util import parse_table
from falafel.core import load_package
from falafel.core import plugins

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


def word_wrap(line, wrap_len=72):
    if len(line) > wrap_len:
        for i, c in enumerate(reversed(line[:wrap_len])):
            if c == " ":
                break_point = wrap_len - i
                yield line[:break_point].strip()
                for more in word_wrap(line[break_point:], wrap_len):
                    yield more
                break
    else:
        yield line.strip()


def write_content(content, path, wrap=True):
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


def compute_plugin_dir(module):
    orig = module
    # TODO: Start with falafel.core.plugins.MAPPERS instead of sys.modules
    module = [sys.modules[m].__name__ for m in sys.modules if m.endswith("." + module)]
    assert len(module) < 2, module
    if not module:
        return os.path.join("retired", orig)
    module = module[0].split(PLUGIN_PACKAGE)[1].strip(".")
    intermediate = module.split(".")[:-1]
    if intermediate:
        intermediate.append(module.split(".")[-1])
        module = os.path.join(*intermediate)
    return module


def gen_yaml(data):
    y = {k: data[k] for k in YAML_FIELDS}
    return yaml.dump(y, default_flow_style=False, default_style="")


def save_rule(d, prefix=""):
    module, error_key = d["rule_id"].split("|")
    plugin_dir = os.path.join(prefix, compute_plugin_dir(module))
    error_key_dir = os.path.join(plugin_dir, error_key)
    if not os.path.exists(error_key_dir):
        os.makedirs(error_key_dir)
    for content in CONTENT_FIELDS:
        if content in d:
            yield write_content(d[content],
                                os.path.join(plugin_dir, error_key, content + ".md"))
    yield write_content(gen_yaml(d),
                        os.path.join(plugin_dir, error_key, "metadata.yaml"),
                        wrap=False)


def import_tsv():
    repo = git.Repo(".")
    load_package(PLUGIN_PACKAGE)
    data = parse_table(sys.stdin.read().splitlines(), "\t")
    for row in data:
        row["reboot_required"] = row["reboot_required"] == "1"
    to_add = []
    for d in data:
        to_add.extend(list(save_rule(d, CONTENT_PREFIX)))
    apply_changeset(repo,
                    to_add,
                    "Import content from TSV",
                    "Kyle Lape",
                    "klape@redhat.com")


def apply_changeset(repo, to_add, message, name, email):
    repo.index.add(to_add)
    repo.index.commit(message, author=git.objects.util.Actor(name, email))


def read_error_key(path):
    d = {}
    for f in CONTENT_FIELDS:
        with open(os.path.join(path, f + ".md")) as fp:
            d[f] = fp.read().strip()
    with open(os.path.join(path, "metadata.yaml"), "r") as fp:
        y = yaml.load(fp)
    d.update(y)
    return d


def read_plugin(path):
    try:
        for d in os.listdir(path):
            yield read_error_key(os.path.join(path, d))
    except:
        logger.warning("Missing content: %s", os.path.basename(path))
        logger.warning(path)


def sig_handler(signum, frame):
    logger.debug("Received signal {0}.".format(signum))
    tornado.ioloop.IOLoop.current().add_callback_from_signal(shutdown)


def shutdown():
    logger.info("Shutting Down.")
    tornado.ioloop.IOLoop.current().stop()


class ContentHandler(tornado.web.RequestHandler):

    def initialize(self, repo):
        self.repo = repo
        self.content_prefix = os.path.join(self.repo.working_tree_dir, CONTENT_PREFIX)

    def get(self):
        d = []
        for plugin in [p for n, p in plugins.PLUGINS.items() if PLUGIN_PACKAGE in n]:
            p = compute_plugin_dir(plugin["module"].split(".")[-1])
            p = os.path.join(self.content_prefix, p)
            d.extend(read_plugin(p))
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
            d.update(yaml.load(fp))
        apply_changeset(self.repo, list(save_rule(d, self.content_prefix)),
                        "Posted content update for %s" % d["rule_id"],
                        d["name"], d["email"])


def main():
    from optparse import OptionParser
    import git
    logging.basicConfig()
    p = OptionParser()
    p.add_option("--plugin-module", help="plugin module")
    p.add_option("-p", "--port", help="listening port",
                 default=8080, action="store", type="int")
    p.add_option("--git-path", help="git path",
                 default=".", action="store", type="string")
    opts, args = p.parse_args()
    load_package(opts.plugin_module)
    params = {"repo": git.Repo(opts.git_path)}
    application = tornado.web.Application([
        (r"/content", ContentHandler, params)
    ])
    application.listen(opts.port)
    loop = tornado.ioloop.IOLoop.current()
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    loop.start()
    loop.close()

if __name__ == "__main__":
    import_tsv()
