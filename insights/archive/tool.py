import json
import atexit
import hashlib
import os
import re
import shutil
import subprocess
import shlex
import tempfile
from contextlib import contextmanager

from insights.config import CommandSpec
from insights.config.static import get_config
from insights.parsers.uname import rhel_release_map
from insights.core import context as ctx
from insights.util import fs

_data_spec_config = get_config()

REPO_PATH = "./repository"


class TempMaker(object):

    def __init__(self, cleanup=True, path='/tmp'):
        self.cleanup = cleanup
        self.path = tempfile.mkdtemp(suffix='_insights_archive', dir=path)
        self.temps = set()

    def get_temp(self):
        path = tempfile.mkdtemp(dir=self.path)
        self.temps.add(path)
        return path

    def close(self):
        if self.cleanup:
            fs.remove(self.path)


__tmp_maker = None


def __cleanup():
    if __tmp_maker:
        __tmp_maker.close()


def get_temp_dir():
    global __tmp_maker
    if not __tmp_maker:
        __tmp_maker = TempMaker()
        atexit.register(__cleanup)
    return __tmp_maker.get_temp()


class BaseArchive(object):

    root_prefix = "base_archives"

    def __init__(self, name, validate=True):
        self.name = name
        root_prefix = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      REPO_PATH,
                                      self.root_prefix))
        if not os.path.exists(root_prefix):
            os.makedirs(root_prefix)
        self.root_dir = os.path.join(root_prefix, name)
        if validate:
            self.validate()

    def validate(self):
        if not self.name:
            raise ValueError("Name not valid")
        if not os.path.exists(self.root_dir):
            raise IOError("{0} {1} can not be found".format(self.__class__.__name__, self.name))

    def files(self, absolute=False):
        prefix_len = 0 if absolute else len(self.root_dir) + 1
        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                yield os.path.join(dirpath[prefix_len:], filename)


def strip_slash(path):
    path = path.strip()
    if path.startswith("/"):
        path = path.lstrip("/")
    return path


class TempOverlay(BaseArchive):

    def __init__(self, files):
        self.name = "TempOverlay"
        self.cached_files = files if files else []
        self.root_dir = get_temp_dir()
        for i, t in enumerate(self.cached_files):
            path, content = t
            path = strip_slash(path)
            self.cached_files[i] = (path, content)
            self.add_file(path, content)

    def add_file(self, path, content):
        if not isinstance(path, str):
            raise ValueError("Invalid path type: {0}".format(type(path)))
        # We don't allow absolute paths
        if content:
            full_path = os.path.join(self.root_dir, path)
            if not os.path.exists(os.path.dirname(full_path)):
                os.makedirs(os.path.dirname(full_path))
            with open(full_path, "w") as f:
                f.write(content.encode("utf-8") + "\n")

    def files(self, absolute=False):
        for path, content in self.cached_files:
            if content:
                yield os.path.join(self.root_dir, path) if absolute else path


class Overlay(BaseArchive):

    root_prefix = "overlays"


class Transform(object):

    def __init__(self, path, force_create=True):
        self.path = path
        self.ops = []
        self.paths = []
        self.force_create = force_create

    def resolve_paths(self, archive):
        specs = _data_spec_config.get_spec_list(self.path)
        if not specs:
            specs = _data_spec_config.get_meta_spec_list(self.path)
            if not specs:
                raise ValueError("Invalid symbolic name: [%s]" % self.path)
        for archive_file in archive.files():
            for spec in specs:
                if spec.matches(archive_file, suffix="$"):
                    self.paths.append(archive_file)
        if not self.paths:
            if self.force_create:
                primary_value = specs[0]
                if isinstance(primary_value, CommandSpec):
                    new_path = os.path.join(archive.root_dir, "insights_commands", primary_value.get_path())
                else:
                    new_path = os.path.join(archive.root_dir, primary_value.get_path())
                self.paths.append(new_path)
            else:
                raise ValueError("Symbolic name not found: {0}".format(self.path))

    def replace(self, content):
        def _replace(path):
            parent_dir = os.path.dirname(path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            with open(path, 'w') as fp:
                fp.write(content.encode("utf-8") + "\n")
        self.ops.append(_replace)
        return self

    def append(self, content):
        def _append(path):
            with open(path, 'a') as fp:
                fp.write(content.encode("utf-8") + "\n")
        self.ops.append(_append)
        return self

    def sub(self, pattern, replacement):
        pattern = make_regexp(pattern)

        def _sub(path):
            with file_replacer(path) as (fp, tf):
                for line in fp:
                    tf.write(pattern.sub(replacement, line))

        self.ops.append(_sub)
        return self

    def grep(self, pattern, keep=True):
        pattern = make_regexp(pattern)

        def _grep(path):
            with file_replacer(path) as (fp, tf):
                for line in fp:
                    if bool(pattern.match(line)) == keep:  # xor
                        tf.write(line)
                    else:
                        continue

        self.ops.append(_grep)
        return self

    def exclude(self, pattern):
        return self.grep(pattern, keep=False)

    def execute(self, root_dir):
        for op in self.ops:
            for path in self.paths:
                op(os.path.join(root_dir, path))
        self.paths = []


class TestArchive(BaseArchive):

    root_prefix = "test_archives"

    def __init__(self, name, base_archive="rhel7", overlays=None, transforms=None, machine_id=None, removals=None, compression="gz", hostname=None, **kwargs):
        super(TestArchive, self).__init__(name, validate=False)
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)
        self.base_archive = (
            base_archive if isinstance(base_archive, BaseArchive) else BaseArchive(base_archive))
        self.overlays = [Overlay(o) for o in overlays] if overlays else []
        self.transforms = transforms if transforms else []
        self.machine_id = machine_id if machine_id else self.generate_machine_id()
        self.machine_id_override = bool(machine_id)
        self.removals = removals if removals else []
        self.compression = compression
        self.hostname = hostname if hostname else self.machine_id
        self.extra = kwargs

    def create_dir_structure(self):
        self.copy_archive(self.base_archive)
        for spec in self.removals:
            if isinstance(spec, str):
                spec = _data_spec_config.get_spec_list(spec)[0]
            for f in filter(spec.matches, self.files()):
                path_to_unlink = os.path.join(self.root_dir, f)
                if os.path.exists(path_to_unlink):
                    os.unlink(path_to_unlink)

        for o in self.overlays:
            self.copy_archive(o)
        for t in self.transforms:
            t.resolve_paths(self)
            t.execute(self.root_dir)
        self.apply_metadata()

    def apply_plugin(self, plugin):
        self.transform(*plugin.get("transforms", []))
        self.overlay(*plugin.get("overlays", []))

    def apply_metadata(self):
        machine_id_path = os.path.join(self.root_dir, "etc/redhat-access-insights")

        if not os.path.exists(machine_id_path):
            os.makedirs(machine_id_path)

        with open(os.path.join(machine_id_path, "machine-id"), "w") as f:
            f.write(self.machine_id if self.machine_id_override else self.generate_machine_id())
        with open(os.path.join(self.root_dir, "branch_info"), "w") as f:
            f.write(self.generate_branch_info())

    @contextmanager
    def file_content(self, name):
        with open(os.path.join(self.root_dir, name), "r") as fd:
            yield fd

    def transform(self, *t):
        for transform in t:
            self.transforms.append(transform)
        return self

    def overlay(self, *o):
        for overlay in o:
            self.overlays.append(overlay)
        return self

    def get_context(self):
        return ctx.Context(hostname=self.hostname,
                           machine_id=self.machine_id,
                           **self.extra)

    def generate_machine_id(self):
        h = hashlib.sha224(self.name)
        h.update(self.base_archive.name)
        for overlay in self.overlays:
            h.update(overlay.name)
        for transform in self.transforms:
            h.update(transform.path)
        return "TEST-" + h.hexdigest()

    def generate_branch_info(self):
        return '{"remote_branch": -1, "remote_leaf": -1}'

    def copy_archive(self, archive):
        for fname in archive.files():
            src = os.path.join(archive.root_dir, fname)
            dst = os.path.join(self.root_dir, fname)
            dstdir = os.path.dirname(dst)
            if not os.path.exists(dstdir):
                os.makedirs(dstdir)
            shutil.copyfile(src, dst)

    def export_options(self):
        if self.compression == "gz":
            return "czf", "tar.gz"
        elif self.compression == "xz":
            return "cJf", "tar.xz"
        else:
            return "cf", "tar"

    def export(self, dest=".", nested_root=True):
        options, ext = self.export_options()
        if nested_root:
            dir_root = os.path.join(self.root_dir, "..")
            root_name = self.name
        else:
            dir_root = self.root_dir
            root_name = "."
        subprocess.check_call(
            shlex.split("tar {0} {1}.{2} -C {3} {4}".format(
                options, os.path.join(dest, self.name),
                ext, dir_root, root_name)))
        return self.output_path(dest)

    def output_path(self, dest):
        return os.path.join(dest, "{0}.{1}".format(
            self.name,
            self.export_options()[1]))

    def clean(self):
        fs.remove(self.root_dir)

    def build(self, dest, force=False):
        if force:
            self.clean()
        elif os.path.exists(self.output_path(dest)):
            return self.output_path(dest)
        self.create_dir_structure()
        return self.export(dest)

    def apply_input_data(self, input_data):
        self._apply_input_data_removals(input_data)
        self._apply_input_data_content(input_data)
        if input_data.hostname != "hostname.example.com":
            self.transforms.append(Transform("hostname").replace(input_data.hostname))
        self.machine_id = input_data.machine_id
        self.machine_id_override = True
        if input_data.release != "default-release":
            self.transforms.append(Transform("redhat-release").replace(input_data.release))
        if (input_data.version != ["-1", "-1"] and
                not [t.path for t in self.transforms if t.path == "uname"]):
            rhel_version = ".".join(input_data.version)
            for kernel, rhel in rhel_release_map.items():
                if rhel_version == rhel:
                    nvr_regex = " \d*\.\d*\.\d*-\d*"
                    self.transforms.append(Transform("uname").sub(nvr_regex, " " + kernel))

    def _apply_input_data_removals(self, input_data):
        for symbolic_name in input_data.to_remove:
            self.removals.extend(_data_spec_config.get_spec_list(symbolic_name))

    def _apply_input_data_content(self, input_data):
        for record in input_data.records:
            target = record["target"]
            content = record["context"].content
            path = record["context"].path
            if path and "BOGUS" not in path:
                # Presence of path means it's a pattern file, which means it
                # probably won't exist in the current archive
                self.overlays.append(TempOverlay([(path, content)]))
            else:
                self.transforms.append(Transform(target).replace(content))


class MultiArchive(TestArchive):

    def __init__(self, name, archives=None, machine_id=None, display_name=None, **kwargs):
        super(MultiArchive, self).__init__(name, machine_id=machine_id, **kwargs)
        self.archives = archives if archives else []
        self.metadata = None
        self.display_name = display_name
        self.extra_metadata = {}

    def copy_archive(self, archive):
        pass

    def apply_metadata(self):
        pass

    def add_metadata(self, md):
        self.extra_metadata.update(md)
        return self

    def build(self, dest, force=True):
        if force:
            self.clean()
        elif os.path.exists(self.output_path(dest)):
            return self.output_path(dest)
        if not self.metadata:
            self.metadata = self.build_metadata(self.archives)
        self.transforms.append(self.metadata)
        self.create_dir_structure()
        for sub_archive in self.archives:
            sub_archive.compression = None
            sub_archive_path = sub_archive.build(dest, force=force)
            shutil.move(sub_archive_path, self.root_dir)
        return self.export(dest, nested_root=False)

    def build_metadata(self, sub_archives):
        first_ctx = sub_archives[0].get_context()
        product = first_ctx.product()
        parent = get_parent(sub_archives)
        systems = []
        for system in sub_archives:
            sys_ctx = system.get_context()
            systems.append({
                "product": product.name,
                "display_name": sys_ctx.hostname,
                "system_id": sys_ctx.machine_id,
                "type": sys_ctx.product().role,
                "links": build_links(system, sub_archives, parent)
            })
        metadata = {
            "product": product.name,
            "display_name": self.display_name if self.display_name else parent.hostname,
            "rhel_version": first_ctx.release,
            "system_id": self.machine_id if self.machine_id else first_ctx.machine_id,
            "systems": systems
        }
        metadata.update(self.extra_metadata)
        return Transform("metadata.json").replace(json.dumps(metadata))

    def apply_input_data(self, sub_archives):
        self.metadata = self.build_metadata(sub_archives)
        for i, input_data in enumerate(sub_archives):
            sub_archive = TestArchive("sub-archive-%d" % i, compression=None)
            sub_archive.apply_input_data(input_data)
            self.archives.append(sub_archive)


def build_links(target_archive, all_archives, parent):
    links = []
    is_parent = target_archive == parent
    if is_parent:
        for archive in all_archives:
            ctx = archive.get_context()
            links.append({
                "system_id": ctx.machine_id,
                "type": ctx.product().role
            })
    else:
        ctx = parent.get_context()
        links.append({
            "system_id": ctx.machine_id,
            "type": ctx.product().role
        })
    return links


def get_parent(sub_archives):
    for a in sub_archives:
        if a.get_context().product().is_parent():
            return a


@contextmanager
def file_replacer(path):
    with open(path, 'r') as fp:
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            yield fp, tf
            tf.flush()
            temp_name = tf.name
    shutil.move(temp_name, path)


def make_regexp(pattern):
    if not hasattr(pattern, 'match'):
        pattern = re.compile(pattern)
    return pattern
